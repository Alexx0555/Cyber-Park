# 🅿️ CyberPark - Smart Parking Management Application

A comprehensive full-stack parking management system with real-time spot tracking, loyalty rewards, admin dashboard, and automated email notifications.

![CyberPark](https://img.shields.io/badge/CyberPark-System-4ecdc4?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey?style=flat-square)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Admin Access](#-admin-access)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### User Features
- 🔐 **User Authentication** - Secure registration and login system with JWT tokens
- 🅿️ **Real-time Parking Spot Availability** - View and book available parking spots
- 🚗 **Vehicle Management** - Support for regular and EV vehicles
- ⭐ **Loyalty Points System** - Earn points with every booking (2 points per hour)
- 📊 **Parking History** - Track all your past parking sessions
- 💳 **Secure Payments** - Integrated payment system with cost calculation
- 📧 **Email Notifications** - Automated booking confirmations and monthly reports
- 🎭 **Feedback System** - Submit and track feedback with status updates

### Admin Features
- 👑 **Admin Dashboard** - Comprehensive management portal with analytics
- 🏢 **Parking Lot Management** - Create, edit, and delete parking locations
- 🅿️ **Spot Management** - Configure spots, set maintenance mode, manage EV spots
- 👥 **User Management** - View and manage all registered users
- 📈 **Analytics & Charts** - Revenue tracking and lot usage visualization
- 📊 **Data Export** - Export user data to CSV
- 📧 **Bulk Email Reports** - Send monthly reports to all users
- 🎭 **Feedback Management** - Review and respond to user feedback

### Technical Features
- 🎨 **Modern UI** - Cyberpunk-themed interface with Three.js animations
- 🌙 **Dark Mode** - Homepage with dark/light theme toggle
- 📱 **Responsive Design** - Mobile-friendly interface
- ⚡ **Real-time Updates** - Live parking spot availability
- 🔄 **Background Tasks** - Celery-powered async email sending
- 🗄️ **Database** - SQLite with SQLAlchemy ORM
- 🔒 **Security** - Password hashing, JWT authentication, role-based access

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 2.3.3
- **Database:** SQLite with SQLAlchemy 2.0.21
- **Authentication:** JWT (PyJWT 2.8.0)
- **Task Queue:** Celery 5.3.4 with Redis
- **Email:** Flask-Mail 0.9.1
- **Caching:** Flask-Caching 2.1.0
- **Security:** Cryptography 41.0.4

### Frontend
- **Framework:** Vue.js 3.5.13
- **Build Tool:** Vite 6.3.5
- **Router:** Vue Router 4.5.1
- **3D Graphics:** Three.js 0.180.0
- **Charts:** Chart.js 4.5.0
- **Notifications:** Vue Toastification 2.0.0-rc.5

### Infrastructure
- **Message Broker:** Redis 5.0.0
- **Task Scheduler:** Celery Beat

## 📁 Project Structure

```
Vehicle-parking-App/
├── backend/                    # Backend Flask application
│   ├── __init__.py            # App factory and configuration
│   ├── models.py              # Database models
│   ├── routes.py              # API routes
│   ├── auth.py                # Authentication utilities
│   ├── utils.py               # Email sending functions
│   ├── tasks.py               # Celery background tasks
│   └── init_admin.py          # Admin user initialization
├── frontend/                   # Frontend Vue.js application
│   ├── src/
│   │   ├── components/        # Vue components
│   │   │   ├── Homepage.vue   # Landing page with Three.js
│   │   │   ├── logreg.vue     # Login/Register
│   │   │   ├── userdash.vue   # User dashboard
│   │   │   ├── admindash.vue  # Admin dashboard
│   │   │   ├── adminUsers.vue # User management
│   │   │   ├── adminRec.vue   # Parking records
│   │   │   └── adminfb.vue    # Feedback management
│   │   ├── assets/            # CSS and static files
│   │   ├── utils/             # Utility functions
│   │   ├── router.js          # Vue Router configuration
│   │   └── main.js            # App entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── exports/                    # Generated export files
├── app.py                      # Flask app entry point
├── celery_worker.py           # Celery worker configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Redis Server** - [Download](https://redis.io/download)
  - Windows: Use [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
  - Linux/macOS: `sudo apt install redis-server` or `brew install redis`
- **Git** - [Download](https://git-scm.com/downloads)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Alexx0555/Cyber-Park.git
cd Cyber-Park
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///parking_app.db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here

# Encryption/Decryption
FERNET_SECRET_KEY=your-fernet-secret-key-here

# Email Configuration (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password


# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

```

### 2. Initialize Database

The database will be created automatically on first run. To initialize with an admin user:

```bash
python -c "from backend import create_app, db; from backend.init_admin import create_admin_user; app = create_app(); app.app_context().push(); db.create_all(); create_admin_user()"
```

## 🏃 Running the Application

### Option 1: Using Batch/Shell Scripts (Recommended)

**Windows:**
```bash
# Start all Celery services
start_celery.bat

# In another terminal, start Flask app
python app.py

# In another terminal, start frontend
cd frontend
npm run dev
```

**Linux/macOS:**
```bash
# Make script executable
chmod +x start_celery.sh

# Start Celery services
./start_celery.sh

# In another terminal, start Flask app
python app.py

# In another terminal, start frontend
cd frontend
npm run dev
```

### Option 2: Manual Start (All Platforms)

You need **4 terminal windows**:

**Terminal 1 - Redis Server:**
```bash
redis-server
# Windows: redis-server.exe
```

**Terminal 2 - Celery Worker:**
```bash
# Windows:
celery -A celery_worker.celery_app worker --loglevel=info --pool=solo --concurrency=1

# Linux/macOS:
celery -A celery_worker.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
celery -A celery_worker.celery_app beat --loglevel=info
```

**Terminal 4 - Flask Backend:**
```bash
python app.py
```

**Terminal 5 - Vue Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000

## 👑 Admin Access

### Default Admin Credentials

- **Username:** `Super_admin`
- **Email:** `admin@gmail.com`
- **Password:** `admin123`

**⚠️ Important:** Change the default admin password after first login!

### Admin Features Access

1. Login with admin credentials
2. You'll be redirected to the admin dashboard at `/admin`
3. Access admin-only features:
   - User Management: `/admin/users`
   - Parking Records: `/admin/records`
   - Feedback Management: `/admin/feedback`

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/refresh` - Refresh JWT token

### User Endpoints

- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `GET /api/user/parking-history` - Get parking history
- `POST /api/user/feedback` - Submit feedback

### Parking Endpoints

- `GET /api/parking-lots` - Get all parking lots
- `GET /api/parking-lots/:id/spots` - Get spots for a lot
- `POST /api/parking/book` - Book a parking spot
- `POST /api/parking/end` - End parking session

### Admin Endpoints

- `GET /api/admin/users` - Get all users
- `GET /api/admin/parking-lots` - Manage parking lots
- `POST /api/admin/parking-lots` - Create parking lot
- `PUT /api/admin/parking-lots/:id` - Update parking lot
- `DELETE /api/admin/parking-lots/:id` - Delete parking lot
- `POST /api/admin/export-users` - Export users to CSV
- `POST /api/admin/send-monthly-reports` - Send monthly reports

## 🎨 Features Showcase

### Homepage
- Stunning Three.js animated background with:
  - Floating cars and parking structures
  - Morphing geometric shapes
  - Glowing orbs and shooting stars
  - Wave effects and energy rings
- Dark/Light mode toggle
- Smooth scroll animations

### User Dashboard
- Real-time parking spot availability
- Interactive parking lot visualization
- Booking management
- Loyalty points tracking

### Admin Dashboard
- Revenue and usage analytics with Chart.js
- Interactive parking lot management
- Spot-level control (maintenance mode, EV spots)
- User and feedback management

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Three.js for amazing 3D graphics
- Vue.js community for excellent documentation
- Flask and Celery for robust backend infrastructure
- Chart.js for beautiful data visualization

---
