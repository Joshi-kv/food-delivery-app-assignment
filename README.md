# Food Delivery App Assignment

A comprehensive Django-based food delivery platform with real-time features, role-based access control, and WebSocket support for live chat functionality.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
- [AWS Deployment Guide](#aws-deployment-guide)
- [User Roles & Test Credentials](#user-roles--test-credentials)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Project Overview

Food Delivery App is a full-featured food delivery platform built with Django 5.2.7. The application supports three distinct user roles (Customers, Delivery Partners, and Administrators) with role-based access control, OTP-based authentication, real-time chat via WebSockets, and comprehensive booking management.

### Key Features

- **Multi-Role Authentication System**
  - OTP-based authentication for customers and delivery partners
  - Email/password authentication for administrators
  - Role-based access control (RBAC) with dynamic menu system

- **Booking Management**
  - Create and track food delivery bookings
  - Real-time status updates (pending → assigned → started → reached → collected → delivered)
  - Booking assignment and reassignment for administrators
  - Status history logging

- **Real-Time Chat**
  - WebSocket-based chat between customers and delivery partners
  - Message persistence in database
  - Connection status indicators
  - Auto-reconnection on connection loss

- **Admin Panel**
  - Custom administrator dashboard with statistics
  - User management (customers, delivery partners)
  - Booking management and assignment
  - Reports and analytics

- **Additional Features**
  - Activity logging for audit trails
  - Redis-based caching and session management
  - Celery for asynchronous task processing
  - Responsive UI with Bootstrap 5

---

## 🛠 Technology Stack

### Backend
- **Django 5.2.7** - Web framework
- **Django Channels 4.0.0** - WebSocket support
- **Daphne 4.0.0** - ASGI server
- **Celery** - Asynchronous task queue
- **PostgreSQL** - Primary database
- **Redis** - Cache, session storage, and channel layer

### Frontend
- **Bootstrap 5** - UI framework
- **jQuery** - JavaScript library
- **Font Awesome** - Icons
- **WebSocket API** - Real-time communication

### Deployment
- **Nginx** - Reverse proxy
- **Supervisor/systemd** - Process management
- **AWS Services** - EC2

---

## 📁 Project Structure

```
food-delivery-app-assignment/
├── food_delivery_app/          # Project settings
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── asgi.py                 # ASGI configuration for WebSockets
│   └── wsgi.py                 # WSGI configuration
├── core/                       # Core app (authentication, models, shared functionality)
│   ├── models.py               # User, Booking, ChatMessage, etc.
│   ├── views.py                # Authentication views
│   ├── consumers.py            # WebSocket consumers
│   ├── routing.py              # WebSocket URL routing
│   ├── helpers.py              # Helper functions
│   ├── validators.py           # Custom validators
│   └── management/commands/    # Custom management commands
├── customer/                   # Customer app
│   ├── views.py                # Customer-specific views
│   └── urls.py                 # Customer URL patterns
├── delivery_partner/           # Delivery partner app
│   ├── views.py                # Delivery partner views
│   └── urls.py                 # Delivery partner URL patterns
├── administrator/              # Administrator app
│   ├── views.py                # Admin panel views
│   └── urls.py                 # Admin URL patterns
├── templates/                  # HTML templates
│   ├── auth/                   # Authentication templates
│   ├── customer/               # Customer templates
│   ├── delivery_partner/       # Delivery partner templates
│   └── administrator/          # Admin panel templates
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── media/                      # User-uploaded files
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── start_server.sh             # Server startup script
└── README.md                   # This file
```

---

## 🚀 Local Development Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 14+** ([Download](https://www.postgresql.org/download/))
- **Redis 6+** ([Download](https://redis.io/download))
- **Git** ([Download](https://git-scm.com/downloads))

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd food-delivery-app-assignment
```

#### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root (optional, or set directly in `settings.py`):

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```
#### 5. Start Redis

```bash
# macOS (with Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Or run Redis directly
redis-server
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

#### 6. Run Database Migrations

```bash
python manage.py migrate
```

#### 7. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

#### 8. Assign admin user to Admin User Group (Admin Account)

```bash
python manage.py add_user_to_group {{user_id}} {{group_id}} 

#example
python manage.py add_user_to_group 1 3(for admin)
```

#### 9. Set Up RBAC (Role-Based Access Control)

```bash
python manage.py setup_rbac
```

This creates the necessary groups, permissions, and dynamic menus.

#### 10. Create Test Users (Optional)

```bash
# Create test delivery partners
python manage.py shell
```

```python
from core.models import User
from django.contrib.auth.models import Group

dp_group = Group.objects.get(name='Delivery Partners')

# Create delivery partner
dp = User.objects.create_user(
    mobile_number='+919876543211',
    password='delivery123',
    first_name='John',
    last_name='Doe',
    email='john@delivery.com',
    role='delivery_partner',
    is_active=True
)
dp.groups.add(dp_group)
print(f"Created: {dp.get_full_name()}")
```

#### 11. Run the Development Server

**Important:** Use Daphne (ASGI server) instead of `runserver` for WebSocket support.

```bash
# Option 1: Use the startup script (recommended)
./start_server.sh

# Option 2: Run Daphne manually with environment variable
AUTOBAHN_USE_NVX=0 daphne -b 127.0.0.1 -p 8000 food_delivery_app.asgi:application
```

The application will be available at: **http://127.0.0.1:8000**

#### 12. Access the Application

- **Customer Signup:** http://127.0.0.1:8000/signup/
- **Delivery Partner Signup:** http://127.0.0.1:8000/delivery/signup/
- **Admin Login:** http://127.0.0.1:8000/admin/login/
- **Django Admin:** http://127.0.0.1:8000/django-admin/

---