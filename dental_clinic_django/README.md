# Aura Dental Spa — Full-Stack Django Website & Automated CRM Suite

A modern, luxury, spa-inspired Dental Clinic web application built with **Python (Django 5, Django ORM / SQLite)**, **Tailwind CSS**, and **Vanilla JavaScript**, engineered for high-converting patient acquisition and automated CRM workflows.

## Project Structure (`dental_clinic_django/`)
```text
dental_clinic_django/
├── manage.py                       # Django CLI management script
├── requirements.txt                # Required Python dependencies (Django, requests, dotenv, gunicorn)
├── README.md                       # Complete setup and architecture documentation
├── aura_dental/                    # Django Project Configuration Package
│   ├── __init__.py
│   ├── settings.py                 # Django settings, SQLite DB, Static/Templates, CRM_WEBHOOK_URL
│   ├── urls.py                     # Root URL routing (Django Admin + Clinic App)
│   ├── wsgi.py                     # WSGI deployment entry point
│   └── asgi.py                     # ASGI deployment entry point
├── clinic/                         # Core Dental Clinic & CRM Automation App
│   ├── __init__.py
│   ├── admin.py                    # Built-in Django Admin registrations for Leads, Appointments, Intakes & Logs
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Django ORM Models: Lead, Appointment, PatientIntake, WorkflowLog
│   ├── services.py                 # CRM Webhook dispatcher & 3-Stage SMS/Email/Review Automation Engine
│   ├── urls.py                     # Page routes & REST API endpoints (/api/crm/book, /lead, /intake, /chat)
│   ├── views.py                    # Django Views & JSON API controllers
│   └── migrations/
│       └── 0001_initial.py         # Pre-built initial database migration
├── static/
│   ├── css/
│   │   └── style.css               # Spa-inspired Soft Blue, White & Teal styling
│   └── js/
│       └── main.js                 # Smart Scheduler, Multi-Step Lead Forms, Intake & AI Concierge logic
└── templates/
    ├── base.html                   # Sticky Glass Header, Services Dropdown, Smart Scheduler & AI Chat Widget
    ├── home.html                   # Hero Section, Trust Badges, Services Overview & Patient Testimonials
    ├── services.html               # General, Cosmetic (Invisalign/Veneers), Emergency + Multi-Step CRM Lead Form
    ├── team.html                   # Board-Certified Specialists & Credentials
    ├── portal.html                 # HIPAA Digital Patient Intake & Automated Insurance Verification
    ├── contact.html                # Embedded Google Maps, 24/7 Emergency Hotline & Working Hours
    └── crm_dashboard.html          # Live CRM Pipeline & Automated SMS/Email/Review Workflow Monitor
```

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run database migrations:
   ```bash
   python manage.py migrate
   ```
3. (Optional) Create an admin user for the Django Admin Backoffice (`/admin/`):
   ```bash
   python manage.py createsuperuser
   ```
4. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
5. Open `http://127.0.0.1:8000` in your browser.
