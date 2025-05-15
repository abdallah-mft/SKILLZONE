<p align="center">
  <img src="assets/logo.png" alt="SkillZone Logo" width="200"/>
</p>

# 🎓 SkillZone Learning Platform

SkillZone is a comprehensive full-stack learning platform built with Django REST Framework and Flutter. It delivers both free (SOFT) and premium (HARD) courses, complete with user achievements, interactive quizzes, detailed progress tracking, and a gamified reward system to enhance the learning experience.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)
[![Flutter](https://img.shields.io/badge/Flutter-Latest-blue.svg)](https://flutter.dev/)

SkillZone Flutter : https://github.com/BrahimBenzekri/SkillZone 
Landing Page : https://skillzoneweb.netlify.app/ 

## 📋 Table of Contents

- [Features](#-features)
- [Technical Stack](#️-technical-stack)
- [API Overview](#-api-overview)
- [Installation](#-installation)
- [Environment Setup](#-environment-setup)
- [Development](#-development)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)
- [Authors](#-authors)
- [Acknowledgments](#-acknowledgments)

## 🚀 Features

### Course System
- **Two-tier Course Types**: SOFT (free) and HARD (premium)
- **Video-based Lessons**: Engaging multimedia content
- **Progress Tracking**: Detailed statistics on course completion
- **Reward System**: Points-based incentives for completing courses
- **Course Categories**: Organized by topics and tags
- **Difficulty Levels**: BEGINNER, INTERMEDIATE, ADVANCED
- **User Course Inventory**: Track unlocked and in-progress courses

### Quiz System
- **Course-specific Quizzes**: Reinforce learning with targeted assessments
- **Timed Attempts**: Challenge users with time-limited quizzes
- **Score Tracking**: Detailed performance analytics
- **Achievement Integration**: Unlock achievements through quiz performance
- **Progress Statistics**: Visual representation of quiz performance

### Achievement System
- **Unlockable Achievements**: Reward system for platform engagement
- **Progress Tracking**: Visual indicators of achievement completion
- **Reward Points**: Convert achievements into platform currency
- **Achievement Categories**: Organized by type and difficulty

### User System
- **Custom User Profiles**: Personalized learning experience
- **Points Economy**: Accumulate and spend points to unlock content
- **Progress Dashboard**: Visual overview of learning journey
- **JWT Authentication**: Secure token-based authentication
- **Device Token Management**: Support for push notifications

## 🛠️ Technical Stack

### Backend
- **Django 5.x**: High-level Python web framework
- **Django REST Framework**: Powerful toolkit for building Web APIs
- **PostgreSQL**: Production-grade relational database
- **JWT Authentication**: Secure token-based authentication
- **Redis Cache**: High-performance caching
- **CORS Support**: Cross-Origin Resource Sharing for frontend integration

### Frontend (Flutter)
- **Flutter SDK**: Cross-platform UI toolkit
- **State Management**: Efficient app state handling
- **HTTP/REST Client**: API integration
- **JWT Token Handling**: Secure authentication
- **Device Token Management**: Push notification support
- **Responsive UI**: Adaptive design for multiple screen sizes
- **Offline Data Persistence**: Local storage for offline functionality
- **Cross-platform Support**: iOS and Android compatibility

## 📚 API Overview

### 🔐 Auth Endpoints

#### Register
```http
POST /api/v1/users/register/
```
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "accept_terms": true
}
```

#### Login
```http
POST /api/v1/users/login/
```
Response:
```json
{
  "success": true,
  "data": {
    "access": "JWT_TOKEN",
    "refresh": "REFRESH_TOKEN"
  }
}
```

#### Refresh Token
```http
POST /api/v1/token/refresh/
```

Request Body:
```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "access": "NEW_ACCESS_TOKEN"
  }
}
```

**Troubleshooting:**
- If you get a 404 error, ensure you've added the TokenRefreshView to your URLs
- Check that you're using the correct URL path (/api/v1/token/refresh/)
- Verify that rest_framework_simplejwt is in your INSTALLED_APPS

### 👤 User Endpoints
- `GET /api/v1/users/profile/` - Get current user profile
- `POST /api/v1/users/update-points/` - Update user points
- `POST /api/v1/users/update-device-token/` - Update device token for notifications

### 📘 Course Endpoints
- `GET /api/v1/courses/` - List all courses
- `GET /api/v1/courses/<id>/` - Get course details
- `GET /api/v1/courses/<id>/lessons/` - Get all lessons for a specific course
- `POST /api/v1/courses/<id>/unlock/` - Unlock a course
- `GET /api/v1/courses/<id>/statistics/` - Get course completion statistics
- `GET /api/v1/courses/inventory/` - Get all courses unlocked by the user
- `POST /api/v1/courses/upload-course/` - Upload a new course (admin only)

### 📗 Lesson Endpoints
- `GET /api/v1/courses/<course_id>/lessons/` - Get all lessons for a specific course
- `POST /api/v1/courses/lessons/<id>/unlock/` - Unlock a lesson by spending points
- `POST /api/v1/courses/lessons/<id>/complete/` - Mark a lesson as completed

### 🧪 Quiz Endpoints
- `GET /api/v1/quizzes/courses/<course_id>/quizzes/` - Get all quizzes for a course
- `GET /api/v1/quizzes/quizzes/<id>/` - Get a specific quiz
- `POST /api/v1/quizzes/quizzes/<id>/start/` - Start a quiz attempt
- `POST /api/v1/quizzes/quizzes/<id>/submit/` - Submit quiz answers
- `GET /api/v1/quizzes/quizzes/<id>/statistics/` - Get quiz statistics
- `GET /api/v1/quizzes/courses/<course_id>/quiz_data/` - Get quiz data in frontend-friendly format

### 🏅 Achievement Endpoints
- `GET /api/v1/achievements/` - List all achievements
- `GET /api/v1/achievements/my_achievements/` - Get user's earned achievements
- `GET /api/v1/achievements/available/` - Get available achievements for the user
- `GET /api/v1/achievements/statistics/` - Get achievement statistics

## 🔐 Authentication Guide

Include the JWT token in all protected request headers:
```http
Authorization: Bearer <your_token>
```

Token lifecycle:
- Access tokens expire after 60 minutes
- Refresh tokens expire after 1 day
- Use the refresh endpoint to get a new access token

## 🚦 Error Handling

All endpoints return a consistent error format:
```json
{
    "success": false,
    "message": "Error description",
    "data": null
}
```

Common HTTP Status Codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Server Error

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/skillzone.git
   cd skillzone
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   Create a `.env` file in the project root with the following variables:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=your-database-url
   CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## 🌐 Environment Setup

### Development Environment
```env
# Debug and Security
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=300
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### Production Environment
```env
# Debug and Security
DEBUG=False
ALLOWED_HOSTS=skillzone-2vs6.onrender.com
SECURE_SSL_REDIRECT=True

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname

# CORS Settings
CORS_ALLOWED_ORIGINS=https://skillzone-2vs6.onrender.com

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

## 💻 Development

### Code Structure
```
skillzone/  📁  (Main Project Folder)
├── skillzone/  📁  (Project Settings)
│   ├── settings.py  # Global Configurations
│   ├── urls.py  # Main URL Routing
│   ├── wsgi.py  # Deployment Entry Point
│   └── asgi.py  # Async Support
│
├── users/  📁  (User Authentication & Profiles)
├── courses/  📁  (Skillzone Courses & Content)
├── quizzes/  📁  (Quiz System)
├── achievements/  📁  (Achievement System)
│
├── templates/  📁  (HTML Templates)
├── static/  📁  (CSS, JS, Images)
├── media/  📁  (User Uploaded Content)
├── manage.py  # Django CLI Commands
```

### Common Development Tasks

**Create a new app**
```bash
python manage.py startapp app_name
```

**Generate migrations**
```bash
python manage.py makemigrations
```

**Apply migrations**
```bash
python manage.py migrate
```

**Create a superuser**
```bash
python manage.py createsuperuser
```

**Run tests**
```bash
python manage.py test
```

## 📦 Deployment

### Render.com Deployment

1. **Create a new Web Service**
   - Connect your GitHub repository
   - Select the Python environment
   - Set build command: `./build.sh`
   - Set start command: `gunicorn skillzone.wsgi:application`

2. **Environment Variables**
   Add all required environment variables in the Render dashboard.

3. **Database Setup**
   - Create a PostgreSQL database in Render
   - Link it to your web service

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t skillzone:latest .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 --env-file .env skillzone:latest
   ```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test users

# Run a specific test case
python manage.py test users.tests.TestUserRegistration
```

### Test Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Coding Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for all functions and classes
- Include unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Meftah Wassim Abdallah -- https://github.com/abdallah-mft

## 🙏 Acknowledgments

- Brahim Benzekri https://github.com/BrahimBenzekri 
- Django REST Framework
- Simple JWT
- Flutter Team
- All contributors who have helped shape this project 

## 📊 Project Status

SkillZone is currently in active development. We welcome contributions and feedback to improve the platform.

## 📞 Contact

For questions or support, please open an issue on GitHub or contact the project maintainers directly.
