# Vehicle Parking Management System

A comprehensive web-based parking management application built with Flask, SQLite, and Bootstrap. This system provides separate interfaces for administrators and users to efficiently manage parking operations.

## 🚗 Features

### Admin Features
- **Dashboard Overview**: Real-time statistics of parking lots, spots, and users
- **Parking Lot Management**: Create, edit, and delete parking lots
- **Spot Monitoring**: Visual layout and detailed status of all parking spots
- **User Management**: View all registered users and their activity
- **Analytics**: Visual charts and statistics for parking utilization

### User Features
- **Account Management**: Secure registration and login system
- **Parking Booking**: Browse available lots and book parking spots
- **Active Sessions**: Monitor current parking with real-time cost calculation
- **Parking History**: Complete history of past parking sessions
- **Cost Tracking**: Transparent pricing with detailed billing

### Technical Features
- **RESTful APIs**: JSON endpoints for parking data integration
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Real-time Updates**: Live parking spot availability
- **Secure Authentication**: Password hashing and session management
- **Database Relationships**: Proper foreign key constraints and data integrity

## 🏗️ System Architecture

### Database Schema
\`\`\`
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │ Reservation  │    │ParkingSpot  │    │ParkingLot   │
├─────────────┤    ├──────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │───▶│ user_id (FK) │    │ id (PK)     │───▶│ id (PK)     │
│ username    │    │ spot_id (FK) │◀───│ lot_id (FK) │    │ location    │
│ email       │    │ vehicle_no   │    │ spot_number │    │ address     │
│ password    │    │ start_time   │    │ status      │    │ price/hour  │
│ phone       │    │ end_time     │    └─────────────┘    │ max_spots   │
│ is_admin    │    │ cost         │                       └─────────────┘
│ created_at  │    │ status       │
└─────────────┘    └──────────────┘
\`\`\`

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 + HTML5 + CSS3
- **Authentication**: Werkzeug password hashing
- **Session Management**: Flask sessions
- **Icons**: Font Awesome 6

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Download and Setup**
   \`\`\`bash
   # Create project directory
   mkdir vehicle_parking_app
   cd vehicle_parking_app
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   \`\`\`

2. **Install Dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Create Templates Directory**
   \`\`\`bash
   mkdir templates
   \`\`\`

4. **Add Application Files**
   - Copy `app.py` to the project root
   - Copy all HTML files to the `templates/` directory
   - Copy `requirements.txt` to the project root

5. **Run the Application**
   \`\`\`bash
   python app.py
   \`\`\`

6. **Access the System**
   - Open browser and navigate to `http://localhost:5000`
   - Database will be created automatically on first run

## 👤 Default Credentials

### Administrator Access
- **Username**: `admin`
- **Password**: `admin123`

### User Access
- Register a new account through the registration page

## 📖 User Guide

### For Administrators

#### Initial Setup
1. Login with admin credentials
2. Create your first parking lot:
   - Click "Create New Parking Lot"
   - Enter location details (name, address, pin code)
   - Set pricing (₹ per hour)
   - Specify number of parking spots
   - System automatically creates numbered spots (S001, S002, etc.)

#### Managing Operations
- **Dashboard**: Monitor real-time statistics and occupancy
- **View Spots**: Visual layout showing available/occupied spots
- **Edit Lots**: Modify pricing, add/remove spots
- **User Management**: View registered users and their activity
- **Delete Lots**: Remove lots (only when all spots are empty)

### For Users

#### Getting Started
1. Register a new account with username, email, phone, and password
2. Login to access the user dashboard

#### Booking Parking
1. Click "Book New Parking" from dashboard
2. Browse available parking lots
3. Select a lot with available spots
4. Enter your vehicle registration number
5. Confirm booking - system assigns first available spot
6. Receive confirmation with spot number

#### Managing Reservations
- **Active Sessions**: View current parking with live duration and cost
- **Release Parking**: End session and get final bill
- **History**: Review all past parking sessions
- **Statistics**: Track total sessions, hours, and spending

## 🔧 Configuration

### Environment Variables
```python
# app.py configuration
SECRET_KEY = 'your-secret-key-here'  # Change for production
SQLALCHEMY_DATABASE_URI = 'sqlite:///parking_app.db'
DEBUG = True  # Set to False for production
