from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'user', 'ngo', or 'admin'
    is_profile_complete = db.Column(db.Boolean, default=False)

    # User Profile
    full_name = db.Column(db.String(100))
    nickname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    dob = db.Column(db.String(20))
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))

    # NGO Profile Fields
    ngo_name = db.Column(db.String(100))
    ngo_established = db.Column(db.String(10))
    ngo_occupancy = db.Column(db.Integer)
    ngo_contact = db.Column(db.String(20))
    ngo_types_animals = db.Column(db.String(200))

    # Relationships
    pets = db.relationship('Pet', backref='owner', lazy=True)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    breed = db.Column(db.String(80))
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    age = db.Column(db.Integer)
    height = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    color = db.Column(db.String(50))
    special_mark = db.Column(db.String(100))
    vaccination = db.Column(db.String(100))
    is_for_adoption = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pet_image = db.Column(db.String(300))  # File path or URL for pet image

class AdoptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # NGO is also a User
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, accepted, in-review, Other
    manual_status = db.Column(db.String(200))  # For custom status when 'Other' is selected
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', foreign_keys=[user_id])
    pet = db.relationship('Pet')
    ngo = db.relationship('User', foreign_keys=[ngo_id])

class LostPetReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_lost = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='Started')  # Found, In progress, Started, Other
    manual_status = db.Column(db.String(200))  # For custom status when 'Other' is selected

    user = db.relationship('User', foreign_keys=[user_id])
    ngo = db.relationship('User', foreign_keys=[ngo_id])

class AdoptionMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('adoption_request.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    read_by_ngo = db.Column(db.Boolean, default=False)
    read_by_user = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.String(300))  # File path or URL for attachments

    sender = db.relationship('User')
    request = db.relationship('AdoptionRequest', backref='messages')

class LostPetMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('lost_pet_report.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    read_by_ngo = db.Column(db.Boolean, default=False)
    read_by_user = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.String(300))  # File path or URL for attachments

    sender = db.relationship('User')
    report = db.relationship('LostPetReport', backref='messages')

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    capacity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    ngo = db.relationship('User')
    responses = db.relationship('CampaignResponse', backref='campaign', cascade='all, delete-orphan')

class CampaignResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))
    event_details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User')

class RescueAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(256), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    name = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(64), nullable=False)
    landmark = db.Column(db.String(128), nullable=False)
    animal_type = db.Column(db.String(32), nullable=False)
    wait_time = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')  # Active, Resolved, Other
    manual_status = db.Column(db.String(200))  # For custom status when 'Other' is selected
    messages = db.relationship('RescueMessage', backref='alert', cascade='all, delete-orphan')

class RescueMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('rescue_alert.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    read_by_ngo = db.Column(db.Boolean, default=False)
    read_by_user = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.String(300))  # File path or URL for attachments

    sender = db.relationship('User')
