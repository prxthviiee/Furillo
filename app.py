import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Pet, AdoptionRequest, LostPetReport, AdoptionMessage, LostPetMessage, Campaign, CampaignResponse, RescueAlert, RescueMessage
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask_migrate import Migrate


# Setup
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'furillo.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

UPLOAD_FOLDER = os.path.join(basedir, 'static', 'campaign_images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)
migrate = Migrate(app, db)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables_once():
    if not hasattr(app, 'tables_created'):
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(user_type='admin').first():
                admin = User(
                    username='admin',
                    email='admin@furillo.com',
                    password_hash=generate_password_hash('admin123'),
                    user_type='admin',
                    is_profile_complete=True,
                    full_name='Admin User'
                )
                db.session.add(admin)
                db.session.commit()
        app.tables_created = True

# Routes
@app.route('/')
def about():
    all_campaigns = Campaign.query.order_by(Campaign.timestamp.desc()).all()
    return render_template('about.html', campaigns=all_campaigns)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('login_as')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if user_type not in ['user', 'ngo']:
            flash("Invalid registration type.", "danger")
            return redirect(request.url)

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(request.url)
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(request.url)

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_to_dashboard()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_as = request.form.get('login_as')

        user = User.query.filter_by(username=username).first()

        if user and user.user_type == login_as and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {user.nickname or user.full_name or user.username}!", "success")
            return redirect_to_dashboard()
        else:
            flash("Invalid username, password, or user type.", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

def redirect_to_dashboard():
    if current_user.user_type == 'user':
        if not current_user.is_profile_complete:
            return redirect(url_for('user_questionnaire'))
        return redirect(url_for('user_dashboard'))
    elif current_user.user_type == 'ngo':
        if not current_user.is_profile_complete:
            return redirect(url_for('ngo_profile'))
        return redirect(url_for('ngo_dashboard'))
    elif current_user.user_type == 'admin':
        return "Admin panel coming soon"
    else:
        logout_user()
        flash("Unknown user type.", "danger")
        return redirect(url_for('login'))

@app.route('/user/questionnaire', methods=['GET', 'POST'])
@login_required
def user_questionnaire():
    if current_user.user_type != 'user':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()

    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.nickname = request.form.get('nickname')
        current_user.dob = request.form.get('dob')
        current_user.address = request.form.get('address')
        current_user.pin_code = request.form.get('pin_code')
        current_user.phone = request.form.get('phone')
        current_user.is_profile_complete = True

        have_pet = request.form.get('have_pet')
        db.session.commit()

        if have_pet == 'yes':
            return redirect(url_for('pet_profile_create'))
        return redirect(url_for('user_dashboard'))

    return render_template('user_questionnaire.html')

@app.route('/user/pet-profile', methods=['GET', 'POST'])
@login_required
def pet_profile_create():
    if current_user.user_type != 'user':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()

    if request.method == 'POST':
        file = request.files.get('pet_image')
        pet_image_path = None
        if file and file.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            upload_dir = os.path.join('static', 'pet_images')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            pet_image_path = f'pet_images/{filename}'
        pet = Pet(
            name=request.form.get('name'),
            breed=request.form.get('breed'),
            gender=request.form.get('gender'),
            dob=request.form.get('dob'),
            age=int(request.form.get('age')),
            height=request.form.get('height'),
            weight=request.form.get('weight'),
            color=request.form.get('color'),
            special_mark=request.form.get('special_mark'),
            vaccination=request.form.get('vaccination'),
            is_for_adoption=False,
            owner=current_user,
            pet_image=pet_image_path
        )
        db.session.add(pet)
        db.session.commit()
        flash("Pet profile created.", "success")
        return redirect(url_for('user_dashboard'))

    return render_template('pet_profile.html')

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.user_type != 'user':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()
    pets = current_user.pets
    lost_reports = LostPetReport.query.filter_by(user_id=current_user.id).order_by(LostPetReport.timestamp.desc()).limit(3).all()
    adoption_requests = AdoptionRequest.query.filter_by(user_id=current_user.id).order_by(AdoptionRequest.timestamp.desc()).limit(3).all()
    campaigns = Campaign.query.order_by(Campaign.timestamp.desc()).all()
    user_conversations = AdoptionRequest.query.filter_by(user_id=current_user.id).all()
    user_lost_reports = LostPetReport.query.filter_by(user_id=current_user.id).order_by(LostPetReport.timestamp.desc()).all()
    user_campaign_responses = {resp.campaign_id: resp for resp in CampaignResponse.query.filter_by(user_id=current_user.id).all()}
    campaign_response_counts = {c.id: len(c.responses) for c in campaigns}
    user_rescue_alerts = RescueAlert.query.filter_by(user_id=current_user.id).order_by(RescueAlert.timestamp.desc()).all()
    return render_template('user_dashboard.html', user=current_user, pets=pets, lost_reports=lost_reports, adoption_requests=adoption_requests, campaigns=campaigns, user_conversations=user_conversations, user_lost_reports=user_lost_reports, user_campaign_responses=user_campaign_responses, campaign_response_counts=campaign_response_counts, user_rescue_alerts=user_rescue_alerts)

@app.route('/ngo/profile', methods=['GET', 'POST'])
@login_required
def ngo_profile():
    if current_user.user_type != 'ngo':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()

    if request.method == 'POST':
        current_user.ngo_name = request.form.get('ngo_name')
        current_user.ngo_established = request.form.get('ngo_established')
        current_user.ngo_occupancy = None
        current_user.address = request.form.get('address')
        current_user.pin_code = request.form.get('pin_code')
        current_user.email = request.form.get('email')
        current_user.ngo_contact = request.form.get('ngo_contact')
        current_user.ngo_types_animals = request.form.get('ngo_types_animals')
        current_user.is_profile_complete = True

        db.session.commit()
        flash("NGO profile saved.", "success")
        return redirect(url_for('ngo_dashboard'))

    return render_template('ngo_profile.html', ngo=current_user)

@app.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.user_type != 'ngo':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()
    # Auto-delete expired campaigns
    expired = Campaign.query.filter(Campaign.end_date != None, Campaign.end_date < date.today()).all()
    for c in expired:
        db.session.delete(c)
    if expired:
        db.session.commit()
    # Always update NGO occupancy to be accurate
    current_user.ngo_occupancy = Pet.query.filter_by(user_id=current_user.id).count()
    db.session.commit()
    lost_reports = LostPetReport.query.filter_by(ngo_id=current_user.id).all()
    pending_count = AdoptionRequest.query.filter_by(ngo_id=current_user.id, status='pending').count()
    ngo_campaigns = Campaign.query.filter_by(ngo_id=current_user.id).order_by(Campaign.timestamp.desc()).all()
    campaign_response_counts = {c.id: len(c.responses) for c in ngo_campaigns}
    requests = AdoptionRequest.query.filter_by(ngo_id=current_user.id).all()
    rescue_alerts = RescueAlert.query.order_by(RescueAlert.timestamp.desc()).all()
    return render_template(
        'ngo_dashboard.html',
        ngo=current_user,
        lost_reports=lost_reports,
        pending_count=pending_count,
        ngo_campaigns=ngo_campaigns,
        campaign_response_counts=campaign_response_counts,
        requests=requests,
        rescue_alerts=rescue_alerts
    )

@app.route('/ngo/update-request-status/<int:request_id>', methods=['POST'])
@login_required
def update_request_status(request_id):
    req = AdoptionRequest.query.get_or_404(request_id)
    if current_user.id != req.ngo_id:
        flash("Access denied.", "danger")
        return redirect(url_for('view_request'))
    new_status = request.form.get('status')
    manual_status = request.form.get('manual_status') if new_status == 'Other' else None
    if new_status in ['pending', 'in-review', 'accepted', 'rejected', 'Other']:
        req.status = new_status
        req.manual_status = manual_status
        db.session.commit()
        if new_status == 'accepted':
            # Remove all other adoption requests for this pet except the accepted one
            AdoptionRequest.query.filter(AdoptionRequest.pet_id == req.pet_id, AdoptionRequest.id != req.id).delete(synchronize_session=False)
            # Transfer pet ownership to the user and set as not for adoption
            pet = req.pet
            if pet:
                pet.is_for_adoption = False
                pet.user_id = req.user_id
                db.session.commit()
                # Update NGO occupancy
                ngo = User.query.get(req.ngo_id)
                if ngo:
                    ngo.ngo_occupancy = Pet.query.filter_by(user_id=ngo.id).count()
                    db.session.commit()
        flash(f"Request status updated to {new_status}.", "success")
    return redirect(url_for('ngo_dashboard'))

# NEW: Lost Pet Reporting
@app.route('/user/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost_pet():
    ngos = User.query.filter_by(user_type='ngo').all()
    pets = current_user.pets  # Fetch user's pets
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        date_lost = request.form.get('date_lost')
        description = request.form.get('description')
        ngo_id = request.form.get('ngo_id')
        if not ngo_id:
            flash("Please select an NGO.", "danger")
            return render_template('report_lost_pet.html', ngos=ngos, pets=pets)
        report = LostPetReport(
            user_id=current_user.id,
            ngo_id=int(ngo_id),
            name=name,
            location=location,
            date_lost=date_lost,
            description=description
        )
        db.session.add(report)
        db.session.commit()
        flash("Lost pet report submitted successfully!", "success")
        return redirect(url_for('user_dashboard'))
    return render_template('report_lost_pet.html', ngos=ngos, pets=pets)

# NEW: View Pet Adoptions
@app.route('/adopt')
@login_required
def view_adoptions():
    ngos = User.query.filter_by(user_type='ngo').all()
    ngo_pets = {}
    for ngo in ngos:
        pets = [pet for pet in ngo.pets if pet.is_for_adoption]
        if pets:
            ngo_pets[ngo] = pets
    selected_ngo_id = request.args.get('ngo_id')
    try:
        selected_ngo_id = int(selected_ngo_id) if selected_ngo_id and selected_ngo_id.isdigit() else None
    except Exception:
        selected_ngo_id = None
    return render_template('adoption_posts.html', ngos=ngos, ngo_pets=ngo_pets, selected_ngo_id=selected_ngo_id)

# NEW: Awareness Campaign Creation
@app.route('/user/create-awareness', methods=['GET', 'POST'])
@login_required
def create_awareness():
    if current_user.user_type != 'user':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()

    if request.method == 'POST':
        # You can save this to DB later
        flash("Awareness campaign published!", "success")
        return redirect(url_for('user_dashboard'))

    return render_template('create_awareness.html')

@app.route('/ngo/pet-profile', methods=['GET', 'POST'])
@login_required
def ngo_pet_profile_create():
    if current_user.user_type != 'ngo':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()

    if request.method == 'POST':
        file = request.files.get('pet_image')
        pet_image_path = None
        if file and file.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            upload_dir = os.path.join('static', 'pet_images')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            pet_image_path = f'pet_images/{filename}'
        pet = Pet(
            name=request.form.get('name'),
            breed=request.form.get('breed'),
            gender=request.form.get('gender'),
            dob=request.form.get('dob'),
            age=int(request.form.get('age')),
            height=request.form.get('height'),
            weight=request.form.get('weight'),
            color=request.form.get('color'),
            special_mark=request.form.get('special_mark'),
            vaccination=request.form.get('vaccination'),
            is_for_adoption=True,
            owner=current_user,
            pet_image=pet_image_path
        )
        db.session.add(pet)
        db.session.commit()
        # Update occupancy using a fresh DB query
        current_user.ngo_occupancy = Pet.query.filter_by(user_id=current_user.id).count()
        print(current_user.ngo_occupancy)
        db.session.commit()
        db.session.refresh(current_user)
        flash("Pet profile created for NGO.", "success")
        return redirect(url_for('ngo_dashboard'))

    return render_template('pet_profile.html')

@app.route('/adopt/request/<int:pet_id>', methods=['POST'])
@login_required
def request_adoption(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    ngo = pet.owner
    existing = AdoptionRequest.query.filter_by(user_id=current_user.id, pet_id=pet_id).first()
    if existing:
        flash("You have already requested adoption for this pet.", "warning")
        return redirect(url_for('view_adoptions'))
    req = AdoptionRequest(user_id=current_user.id, pet_id=pet_id, ngo_id=ngo.id)
    db.session.add(req)
    db.session.commit()
    flash("Adoption request sent!", "success")
    return redirect(url_for('view_adoptions'))

@app.route('/ngo/view-request')
@login_required
def view_request():
    if current_user.user_type != 'ngo':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()
    requests = AdoptionRequest.query.filter_by(ngo_id=current_user.id).all()
    return render_template('view_request.html', adoption_requests=requests)

@app.route('/ngo/conversation/<int:request_id>', methods=['GET', 'POST'])
@login_required
def adoption_conversation(request_id):
    adoption_request = AdoptionRequest.query.get_or_404(request_id)
    if current_user.id not in [adoption_request.ngo_id, adoption_request.user_id]:
        flash("Access denied.", "danger")
        return redirect(url_for('ngo_dashboard'))
    # Mark messages as read
    if current_user.id == adoption_request.ngo_id:
        for msg in adoption_request.messages:
            if not msg.read_by_ngo:
                msg.read_by_ngo = True
        db.session.commit()
    elif current_user.id == adoption_request.user_id:
        for msg in adoption_request.messages:
            if not msg.read_by_user:
                msg.read_by_user = True
        db.session.commit()
    if request.method == 'POST':
        if adoption_request.status not in ['accepted', 'rejected', 'Other']:
            msg = request.form.get('message')
            file = request.files.get('attachment')
            attachment_path = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_dir = os.path.join('static', 'chat_uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                attachment_path = f'chat_uploads/{filename}'
            if msg or attachment_path:
                new_msg = AdoptionMessage(
                    request_id=request_id,
                    sender_id=current_user.id,
                    message=msg,
                    attachment=attachment_path
                )
                db.session.add(new_msg)
                db.session.commit()
                flash("Message sent.", "success")
                return redirect(url_for('adoption_conversation', request_id=request_id))
    messages = AdoptionMessage.query.filter_by(request_id=request_id).order_by(AdoptionMessage.timestamp).all()
    chat_enabled = adoption_request.status not in ['accepted', 'rejected', 'Other']
    return render_template('adoption_conversation.html', adoption_request=adoption_request, messages=messages, current_user_id=current_user.id, chat_enabled=chat_enabled)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    request_id = data['request_id']
    message = data['message']
    sender = current_user
    new_msg = AdoptionMessage(
        request_id=request_id,
        sender_id=sender.id,
        message=message
    )
    db.session.add(new_msg)
    db.session.commit()
    emit('receive_message', {
        'sender': sender.full_name or sender.username,
        'sender_id': sender.id,
        'message': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }, room='adoption_' + str(request_id))

@app.route('/ngo/lostpet_chat/<int:report_id>', methods=['GET', 'POST'])
@login_required
def lostpet_conversation(report_id):
    report = LostPetReport.query.get_or_404(report_id)
    if current_user.id not in [report.ngo_id, report.user_id]:
        flash("Access denied.", "danger")
        return redirect(url_for('ngo_dashboard'))
    # Mark messages as read
    if current_user.id == report.ngo_id:
        for msg in report.messages:
            if not msg.read_by_ngo:
                msg.read_by_ngo = True
        db.session.commit()
    elif current_user.id == report.user_id:
        for msg in report.messages:
            if not msg.read_by_user:
                msg.read_by_user = True
        db.session.commit()
    if request.method == 'POST':
        if report.status not in ['Found', 'Accepted', 'Other']:
            msg = request.form.get('message')
            file = request.files.get('attachment')
            attachment_path = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_dir = os.path.join('static', 'chat_uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                attachment_path = f'chat_uploads/{filename}'
            if msg or attachment_path:
                if not msg:
                    msg = "(Attachment)"
                new_msg = LostPetMessage(
                    report_id=report_id,
                    sender_id=current_user.id,
                    message=msg,
                    attachment=attachment_path
                )
                db.session.add(new_msg)
                db.session.commit()
                flash("Message sent.", "success")
                return redirect(url_for('lostpet_conversation', report_id=report_id))
    messages = LostPetMessage.query.filter_by(report_id=report_id).order_by(LostPetMessage.timestamp).all()
    chat_enabled = report.status not in ['Found', 'Accepted', 'Other']
    return render_template('lostpet_conversation.html', report=report, messages=messages, current_user_id=current_user.id, chat_enabled=chat_enabled)

@socketio.on('join_lostpet')
def on_join_lostpet(data):
    room = data['room']
    join_room(room)

@socketio.on('send_lostpet_message')
def handle_send_lostpet_message(data):
    report_id = data['report_id']
    message = data['message']
    sender = current_user
    new_msg = LostPetMessage(
        report_id=report_id,
        sender_id=sender.id,
        message=message
    )
    db.session.add(new_msg)
    db.session.commit()
    emit('receive_lostpet_message', {
        'sender': sender.full_name or sender.username,
        'sender_id': sender.id,
        'message': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }, room='lostpet_' + str(report_id))

@app.route('/ngo/publish-campaign', methods=['GET', 'POST'])
@login_required
def publish_campaign():
    if current_user.user_type != 'ngo':
        flash("Access denied.", "danger")
        return redirect_to_dashboard()
    image_url = None
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        capacity = request.form.get('capacity')
        file = request.files.get('image_file')
        if file:
            print("UPLOAD FILENAME:", file.filename)
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print("UPLOAD PATH:", upload_path)
                try:
                    file.save(upload_path)
                    image_url = url_for('static', filename=f'campaign_images/{filename}')
                    print("Image saved and URL:", image_url)
                except Exception as e:
                    print("ERROR saving file:", e)
                    flash(f"Error saving image: {e}", "danger")
            else:
                print("File type not allowed:", file.filename)
                flash("File type not allowed. Please upload a PNG, JPG, JPEG, or GIF.", "danger")
        if not title or not description:
            flash("Title and description are required.", "danger")
            return render_template('publish_campaign.html', image_url=image_url)
        campaign = Campaign(
            ngo_id=current_user.id,
            title=title,
            description=description,
            image_url=image_url,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            capacity=int(capacity) if capacity else None
        )
        db.session.add(campaign)
        db.session.commit()
        flash("Campaign published!", "success")
        return redirect(url_for('ngo_dashboard'))
    return render_template('publish_campaign.html', image_url=image_url)

@app.route('/campaigns')
def campaigns():
    all_campaigns = Campaign.query.order_by(Campaign.timestamp.desc()).all()
    return render_template('campaigns.html', campaigns=all_campaigns)

@app.route('/campaign/respond/<int:campaign_id>', methods=['POST'])
def respond_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.is_authenticated:
        # User is logged in, use their details
        name = current_user.full_name or current_user.username
        phone = current_user.phone
        address = current_user.address
        user_id = current_user.id
    else:
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        user_id = None
    if not name or not phone or not address:
        flash("All details are required.", "danger")
        return redirect(request.referrer or url_for('about'))
    response = CampaignResponse(
        campaign_id=campaign_id,
        user_id=user_id,
        name=name,
        phone=phone,
        address=address
    )
    db.session.add(response)
    db.session.commit()
    flash("Thank you for responding to the campaign!", "success")
    return redirect(request.referrer or url_for('about'))

@app.route('/ngo/delete-campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.id != campaign.ngo_id:
        flash("Access denied.", "danger")
        return redirect(url_for('ngo_dashboard'))
    # Optionally, delete the image file from disk
    if campaign.image_url:
        try:
            image_path = os.path.join(basedir, campaign.image_url.lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print("Error deleting image file:", e)
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign deleted.", "success")
    return redirect(url_for('ngo_dashboard'))

@app.route('/ngo/update-campaign-response/<int:response_id>', methods=['POST'])
@login_required
def update_campaign_response(response_id):
    response = CampaignResponse.query.get_or_404(response_id)
    if response.campaign_id is None:
        flash("Invalid campaign response: missing campaign.", "danger")
        return redirect(url_for('ngo_dashboard'))
    campaign = response.campaign
    if current_user.id != campaign.ngo_id:
        flash("Access denied.", "danger")
        return redirect(url_for('ngo_dashboard'))
    event_details = request.form.get('event_details')
    response.event_details = event_details
    db.session.commit()
    flash("Event details sent to responder.", "success")
    return redirect(url_for('ngo_dashboard'))

@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.route('/user/pet-upload-image/<int:pet_id>', methods=['POST'])
@login_required
def pet_upload_image(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.owner != current_user:
        flash("Access denied.", "danger")
        return redirect(url_for('user_dashboard'))
    file = request.files.get('pet_image')
    if file and file.filename:
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        upload_dir = os.path.join('static', 'pet_images')
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        pet.pet_image = f'pet_images/{filename}'
        db.session.commit()
        flash("Image uploaded successfully!", "success")
    else:
        flash("No image selected.", "warning")
    # Redirect to the appropriate dashboard
    if current_user.user_type == 'ngo':
        return redirect(url_for('ngo_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/pet/delete/<int:pet_id>', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.owner != current_user:
        flash("Access denied.", "danger")
        return redirect(url_for('user_dashboard'))
    db.session.delete(pet)
    db.session.commit()
    flash("Pet deleted successfully!", "success")
    if current_user.user_type == 'ngo':
        return redirect(url_for('ngo_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/user/delete-adoption-request/<int:request_id>', methods=['POST'])
@login_required
def delete_adoption_request(request_id):
    req = AdoptionRequest.query.get_or_404(request_id)
    if req.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('user_dashboard'))
    db.session.delete(req)
    db.session.commit()
    flash('Adoption request deleted.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/ngo/update-lostpet-status/<int:report_id>', methods=['POST'])
@login_required
def update_lostpet_status(report_id):
    report = LostPetReport.query.get_or_404(report_id)
    if current_user.id != report.ngo_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('ngo_dashboard'))
    status = request.form.get('status')
    manual_status = request.form.get('manual_status') if status == 'Other' else None
    report.status = status
    report.manual_status = manual_status
    db.session.commit()
    flash('Lost pet report status updated.', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/ngo/update-rescue-status/<int:alert_id>', methods=['POST'])
@login_required
def update_rescue_status(alert_id):
    alert = RescueAlert.query.get_or_404(alert_id)
    if current_user.user_type != 'ngo':
        flash('Access denied.', 'danger')
        return redirect(url_for('ngo_dashboard'))
    status = request.form.get('status')
    manual_status = request.form.get('manual_status') if status == 'Other' else None
    alert.status = status
    alert.manual_status = manual_status
    db.session.commit()
    flash('Rescue alert status updated.', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/ngo/delete-rescue-alert/<int:alert_id>', methods=['POST'])
@login_required
def delete_rescue_alert(alert_id):
    alert = RescueAlert.query.get_or_404(alert_id)
    if current_user.user_type != 'ngo':
        flash('Access denied.', 'danger')
        return redirect(url_for('ngo_dashboard'))
    if alert.status != 'Resolved':
        flash('Only resolved alerts can be deleted.', 'warning')
        return redirect(url_for('ngo_dashboard'))
    db.session.delete(alert)
    db.session.commit()
    flash('Rescue alert deleted.', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/rescue', methods=['GET', 'POST'])
def rescue_alert():
    if request.method == 'POST':
        location = request.form.get('location')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        name = request.form.get('name')
        contact = request.form.get('contact')
        landmark = request.form.get('landmark')
        animal_type = request.form.get('animal_type')
        wait_time = request.form.get('wait_time')
        is_registered = False
        user_id = None
        if current_user.is_authenticated:
            is_registered = True
            user_id = current_user.id
            name = current_user.full_name or current_user.username or name
            contact = current_user.phone or contact
        # Store the alert in DB
        alert = RescueAlert(
            location=location,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            name=name,
            contact=contact,
            landmark=landmark,
            animal_type=animal_type,
            wait_time=wait_time,
            user_id=user_id
        )
        db.session.add(alert)
        db.session.commit()
        ngos = User.query.filter_by(user_type='ngo').all()
        for ngo in ngos:
            pass
        if is_registered:
            flash('Emergency alert sent! Our NGOs have been notified. You may be contacted for more details.', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            if wait_time == '> 1 hour':
                flash('Thank you for your patience! Our NGO team will be there for the rescue. We have your location and contact details.', 'success')
            else:
                flash('We have your location and contact details. Our NGO team will reach you as soon as possible!', 'success')
            return render_template('rescue_alert.html', submitted=True)
    return render_template('rescue_alert.html')

@app.route('/rescue_chat/<int:alert_id>', methods=['GET', 'POST'])
@login_required
def rescue_conversation(alert_id):
    alert = RescueAlert.query.get_or_404(alert_id)
    # Only allow chat if alert.user_id exists (registered user)
    if alert.user_id is None:
        flash('Chat is only available for registered users and NGOs.', 'info')
        return render_template('rescue_conversation.html', alert=alert, messages=[], current_user_id=current_user.id, chat_enabled=False)
    # Only the user who created the alert or any NGO can access
    if current_user.id != alert.user_id and current_user.user_type != 'ngo':
        flash('Access denied.', 'danger')
        return redirect(url_for('user_dashboard'))
    # Mark messages as read
    if current_user.user_type == 'ngo':
        for msg in alert.messages:
            if not msg.read_by_ngo:
                msg.read_by_ngo = True
        db.session.commit()
    elif current_user.id == alert.user_id:
        for msg in alert.messages:
            if not msg.read_by_user:
                msg.read_by_user = True
        db.session.commit()
    if request.method == 'POST':
        msg = request.form.get('message')
        file = request.files.get('attachment')
        attachment_path = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_dir = os.path.join('static', 'chat_uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            attachment_path = f'chat_uploads/{filename}'
        if msg or attachment_path:
            new_msg = RescueMessage(
                alert_id=alert_id,
                sender_id=current_user.id,
                message=msg,
                attachment=attachment_path
            )
            db.session.add(new_msg)
            db.session.commit()
            flash('Message sent.', 'success')
            return redirect(url_for('rescue_conversation', alert_id=alert_id))
    messages = RescueMessage.query.filter_by(alert_id=alert_id).order_by(RescueMessage.timestamp).all()
    return render_template('rescue_conversation.html', alert=alert, messages=messages, current_user_id=current_user.id, chat_enabled=True)

@socketio.on('join_rescue')
def on_join_rescue(data):
    room = data['room']
    join_room(room)

@socketio.on('send_rescue_message')
def handle_send_rescue_message(data):
    alert_id = data['alert_id']
    message = data['message']
    sender = current_user
    new_msg = RescueMessage(
        alert_id=alert_id,
        sender_id=sender.id,
        message=message
    )
    db.session.add(new_msg)
    db.session.commit()
    emit('receive_rescue_message', {
        'sender': sender.full_name or sender.username,
        'sender_id': sender.id,
        'message': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }, room='rescue_' + str(alert_id))

if __name__ == '__main__':
    socketio.run(app, debug=True)
