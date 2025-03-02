#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillzone.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()



"""
===========================================
🔥 DJANGO PROJECT WORKFLOW (Skillzone) 🔥
===========================================

1️⃣ **SETUP & INSTALLATION**  
   - Install Django: `pip install django djangorestframework`
   - Create a project: `django-admin startproject skillzone`
   - Navigate to project folder: `cd skillzone`
   - Run the server: `python manage.py runserver`

2️⃣ **CREATE APPS** (Each app manages a specific feature)  
   - Create a new app: `python manage.py startapp app_name`
   - Register the app in `settings.py` under `INSTALLED_APPS`
   
3️⃣ **PROJECT STRUCTURE**
   skillzone/  📁  (Main Project Folder)
   ├── skillzone/  📁  (Project Settings)
   │   ├── settings.py  # Global Configurations
   │   ├── urls.py  # Main URL Routing
   │   ├── wsgi.py  # Deployment Entry Point
   │   └── asgi.py  # Async Support
   │
   ├── users/  📁  (User Authentication & Profiles)
   │   ├── models.py  # Database Schema
   │   ├── views.py  # API Logic
   │   ├── urls.py  # App-Specific Routing
   │   ├── serializers.py  # DRF Data Serialization
   │   ├── tests.py  # Automated Testing
   │   ├── admin.py  # Django Admin Panel
   │   └── apps.py  # App Configuration
   │
   ├── courses/  📁  (Skillzone Courses & Content)
   │   ├── models.py  # Course Structure
   │   ├── views.py  # Course API
   │   ├── urls.py  # Course Endpoints
   │   └── serializers.py  # API Response Formatting
   │
   ├── templates/  📁  (HTML Templates for Admin Panel)
   ├── static/  📁  (CSS, JS, Images)
   ├── manage.py  # Django CLI Commands

4️⃣ **DATABASE MANAGEMENT**
   - Define models in `models.py`
   - Apply changes: `python manage.py makemigrations`
   - Update database: `python manage.py migrate`
   - Create admin user: `python manage.py createsuperuser`
   - Access admin panel: `http://127.0.0.1:8000/admin/`

5️⃣ **API DEVELOPMENT**
   - Use Django REST Framework (DRF)
   - Create API endpoints in `views.py`
   - Define API routes in `urls.py`
   - Use `serializers.py` to format JSON responses

6️⃣ **AUTHENTICATION & SECURITY**
   - Use Django's built-in `User` model
   - Implement Token Authentication:
     `pip install djangorestframework-simplejwt`
   - Enable CORS for frontend connection:
     `pip install django-cors-headers`

7️⃣ **DEPLOYMENT**
   - Collect static files: `python manage.py collectstatic`
   - Use `gunicorn` or `daphne` for production server
   - Deploy using **Docker, AWS, or Heroku**

8️⃣ **TESTING & DEBUGGING**
   - Debugging: `print()` or `import pdb; pdb.set_trace()`
   - Run tests: `python manage.py test`
   - Check migrations: `python manage.py showmigrations`

===========================================
✅ FOLLOW THIS WORKFLOW FOR EFFICIENT DEVELOPMENT ✅
===========================================
"""
