# SmartOrder - Smart Ordering System

A comprehensive smart ordering platform built with Django, featuring multi-layer architecture for order management, billing, customer profiles, and integrated payment processing.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

SmartOrder is a full-featured ordering system designed for restaurants, cafes, and food delivery services. It provides a seamless experience for customers to place orders, manage payments, and for administrators to track orders and manage menus.

## 🏗️ System Architecture

The project follows a **layered architecture pattern** with the following components:

### Presentation Layer
- **Create**: Order creation interface
- **Kitchen**: Kitchen display system for order preparation
- **Admin**: Administrative dashboard for management
- **Public**: Customer-facing interface
- **View**: Order tracking and view components

### Application Layer
- **Order Management**: Core order processing logic
- **Billing & Payment**: Payment handling and invoice generation
- **Menu Management**: Menu items and catalog management
- **Customer Profiles**: User account and profile management

### Event Driven Layer
- **Amazon SES**: Email notifications for order confirmations and updates
- **Stripe Payment**: Secure payment processing integration

### Data Layer
- **Django ORM**: Object-relational mapping
- **AWS RDS MySQL**: Cloud-based database for production deployment

## ✨ Features

- ✅ Order placement and management
- ✅ Real-time order tracking
- ✅ Kitchen display system (KDS)
- ✅ Menu management
- ✅ Customer profile management
- ✅ Secure payment processing (Stripe integration)
- ✅ Email notifications (AWS SES)
- ✅ Admin dashboard and analytics
- ✅ Order history and reporting
- ✅ Role-based access control

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django (Python) |
| **Database** | AWS RDS MySQL |
| **Email Service** | AWS SES (Simple Email Service) |
| **Payment Gateway** | Stripe |
| **Cloud Platform** | AWS |

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- MySQL (or AWS RDS MySQL connection)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/SmartOrderProject.git
cd SmartOrderProject
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=smartorder_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com

# Stripe Configuration
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### Step 5: Apply Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

## 🚀 Usage

### Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Access Admin Panel
Navigate to `http://localhost:8000/admin` and login with your superuser credentials.


## 📁 Project Structure

```
SmartOrderProject/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── smartorder/                     # Main project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── orders/                         # Orders app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   └── tests.py
│
├── menu/                           # Menu management app
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── customers/                      # Customer profiles app
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── billing/                        # Billing & Payment app
│   ├── models.py
│   ├── views.py
│   ├── payment_gateway.py
│   └── urls.py
│
├── notifications/                  # Email notifications
│   ├── email_service.py
│   └── tasks.py
│
└── static/                         # Static files
    ├── css/
    ├── js/
    └── images/
```

## 🔐 Security Considerations

- Store sensitive data in `.env` file (never commit to version control)
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Validate all user inputs
- Use Django's built-in CSRF protection
- Regular security updates for dependencies


