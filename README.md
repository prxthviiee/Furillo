# 🐾 Furillo - Animal Welfare Platform

A comprehensive web application connecting people, pets, and NGOs for animal welfare, adoption, and rescue operations.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Furillo is a modern web platform designed to bridge the gap between animal welfare organizations (NGOs) and individuals who want to help animals. The platform facilitates pet adoption, lost pet reporting, rescue alerts, and awareness campaigns.

### Mission
To ensure every animal deserves a safe, loving home by creating a caring and connected space where people and organizations can come together to make a real difference in the lives of animals.

## ✨ Features

### 🏠 For Users
- **Pet Adoption**: Browse and request adoption of pets from trusted NGOs
- **Lost Pet Reporting**: Report lost pets and track their recovery status
- **Rescue Alerts**: Send emergency alerts for animals in distress
- **Awareness Campaigns**: Participate in animal welfare campaigns
- **Real-time Chat**: Communicate with NGOs through integrated messaging
- **Profile Management**: Complete user profiles with pet information

### 🏢 For NGOs
- **Pet Management**: Add and manage pets available for adoption
- **Adoption Requests**: Review and manage adoption applications
- **Campaign Creation**: Create awareness campaigns with detailed information
- **Rescue Operations**: Respond to emergency rescue alerts
- **Dashboard Analytics**: Track adoption rates, campaign responses, and rescue operations
- **Status Management**: Update request statuses and provide feedback

### 🔧 Technical Features
- **Real-time Messaging**: WebSocket-based chat system
- **File Uploads**: Image uploads for pets and campaigns
- **Map Integration**: Location-based rescue alerts
- **Responsive Design**: Mobile-friendly interface
- **User Authentication**: Secure login/registration system
- **Database Management**: SQLite with migration support

## 🛠 Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database management
- **Flask-Login**: User authentication
- **Flask-SocketIO**: Real-time messaging
- **Flask-Migrate**: Database migrations

### Frontend
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library
- **Leaflet.js**: Interactive maps
- **JavaScript**: Client-side functionality

### Database
- **SQLite**: Lightweight database (development)
- **PostgreSQL**: Production database (recommended)

### Development Tools
- **Python 3.8+**: Programming language
- **pip**: Package manager
- **Git**: Version control

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Furillo
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install test dependencies (optional)
pip install -r test_requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///instance/furillo.db
```

### Step 5: Initialize Database

```bash
# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run database migrations (if any)
flask db upgrade
```

### Step 6: Create Static Directories

```bash
# Create necessary directories for file uploads
mkdir -p static/pet_images
mkdir -p static/campaign_images
mkdir -p static/chat_uploads
```

### Step 7: Run the Application

```bash
# Development server
python app.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
Furillo/
├── app.py                          # Main Flask application
├── models.py                       # Database models
├── requirements.txt                # Python dependencies
├── test_app.py                    # Test suite
├── run_tests.py                   # Test runner
├── test_requirements.txt          # Test dependencies
├── TEST_README.md                 # Testing documentation
├── README.md                      # This file
├── import_ngos.py                 # NGO data import script
├── instance/                      # Database files
│   └── furillo.db
├── migrations/                    # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
├── static/                        # Static files
│   ├── css/
│   │   └── style.css
│   ├── images/
│   ├── pet_images/
│   ├── campaign_images/
│   └── chat_uploads/
└── Templates/                     # HTML templates
    ├── base.html
    ├── about.html
    ├── login.html
    ├── register.html
    ├── user_dashboard.html
    ├── ngo_dashboard.html
    ├── adoption_posts.html
    ├── publish_campaign.html
    ├── rescue_alert.html
    └── ... (other templates)
```

## 🚀 Usage

### Getting Started

1. **Visit the Homepage**: Navigate to `http://localhost:5000`
2. **Register**: Create an account as either a user or NGO
3. **Complete Profile**: Fill out your profile information
4. **Start Using**: Access dashboard and features based on your user type

### User Workflow

1. **Registration & Login**
   - Register as a regular user
   - Complete user questionnaire
   - Add pet information (optional)

2. **Browse Adoptions**
   - View available pets for adoption
   - Filter by breed, age, location
   - Request adoption for desired pets

3. **Report Lost Pets**
   - Submit lost pet reports
   - Track recovery status
   - Chat with assigned NGO

4. **Participate in Campaigns**
   - Browse awareness campaigns
   - Respond to campaigns of interest
   - Receive event details

5. **Emergency Alerts**
   - Report animals in distress
   - Provide location and details
   - Track rescue progress

### NGO Workflow

1. **Registration & Setup**
   - Register as an NGO
   - Complete NGO profile
   - Add organization details

2. **Pet Management**
   - Add pets available for adoption
   - Upload pet images
   - Manage pet information

3. **Adoption Requests**
   - Review adoption applications
   - Update request statuses
   - Communicate with applicants

4. **Campaign Creation**
   - Create awareness campaigns
   - Set campaign duration and capacity
   - Track campaign responses

5. **Rescue Operations**
   - Respond to emergency alerts
   - Update rescue status
   - Coordinate rescue efforts

## 🔌 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage with campaigns |
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/user/questionnaire` | Complete user profile |
| GET/POST | `/user/pet-profile` | Add pet information |
| GET | `/user/dashboard` | User dashboard |
| GET/POST | `/user/report-lost` | Report lost pet |
| GET | `/adopt` | View adoption posts |
| POST | `/adopt/request/<pet_id>` | Request adoption |

### NGO Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/ngo/profile` | NGO profile management |
| GET | `/ngo/dashboard` | NGO dashboard |
| GET/POST | `/ngo/pet-profile` | Add NGO pets |
| GET | `/ngo/view-request` | View adoption requests |
| POST | `/ngo/update-request-status/<id>` | Update request status |

### Campaign Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/ngo/publish-campaign` | Create campaign |
| GET | `/campaigns` | View all campaigns |
| POST | `/campaign/respond/<id>` | Respond to campaign |
| POST | `/ngo/delete-campaign/<id>` | Delete campaign |

### Rescue Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/rescue` | Create rescue alert |
| POST | `/ngo/update-rescue-status/<id>` | Update rescue status |
| POST | `/ngo/delete-rescue-alert/<id>` | Delete rescue alert |

### Messaging Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/ngo/conversation/<id>` | Adoption conversation |
| GET/POST | `/ngo/lostpet_chat/<id>` | Lost pet conversation |
| GET/POST | `/rescue_chat/<id>` | Rescue conversation |

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m unittest test_app.AuthenticationTests -v
python -m unittest test_app.AdoptionTests -v
python -m unittest test_app.CampaignTests -v

# Run with coverage
coverage run -m unittest test_app.py
coverage report
```

### Test Coverage

The test suite covers:
- ✅ Authentication (registration, login, logout)
- ✅ User profiles and pet management
- ✅ NGO operations and dashboard
- ✅ Adoption system (requests, status updates)
- ✅ Lost pet reporting and tracking
- ✅ Campaign creation and responses
- ✅ Rescue alert system
- ✅ Real-time messaging
- ✅ File uploads
- ✅ Error handling and validation

For detailed testing information, see [TEST_README.md](TEST_README.md).

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your_production_secret_key
   export DATABASE_URL=postgresql://user:pass@localhost/furillo
   ```

2. **Database Setup**
   ```bash
   # Install PostgreSQL
   sudo apt-get install postgresql postgresql-contrib
   
   # Create database
   createdb furillo
   ```

3. **Web Server Setup**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   
   # Run with Gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

4. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /static {
           alias /path/to/your/app/static;
       }
   }
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python -c "from app import app, db; app.app_context().push(); db.create_all()"

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   python run_tests.py
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation as needed