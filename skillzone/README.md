# 🎓 SkillZone Learning Platform

SkillZone is a full-stack learning platform using Django REST Framework and Flutter. It delivers free (SOFT) and premium (HARD) courses, complete with user achievements, quizzes, progress tracking, and a gamified reward system.

## 🚀 Features

### Course System
- Two course types: SOFT (free) and HARD (premium)
- Video-based lessons
- Progress tracking
- Course completion statistics
- Points-based reward system
- Course categories and tags
- Difficulty levels (BEGINNER, INTERMEDIATE, ADVANCED)
- User course inventory for tracking unlocked courses

### Quiz System
- Course-specific quizzes
- Time-limited attempts
- Score tracking
- Achievement integration
- Progress statistics

### Achievement System
- Unlockable achievements
- Progress tracking
- Reward points
- Achievement categories

### User System
- Custom user profiles
- Points accumulation
- Course unlocking mechanism
- Progress tracking
- JWT Authentication
- Device token management

## 🛠️ Technical Stack

### Backend
- Django 4.x
- Django REST Framework
- SQLite (Development) / PostgreSQL (Production)
- JWT Authentication
- Redis Cache
- CORS support

### Frontend (Flutter)
- Flutter SDK
- State Management
- HTTP/REST Client for API integration
- JWT Token handling
- Device Token Management for Notifications
- Responsive UI components
- Offline data persistence
- Cross-platform support (iOS/Android)

### Frontend Setup Requirements
1. Flutter SDK installation
2. Configure CORS in Django for Flutter:
   ```python
   # For development
   CORS_ALLOW_ALL_ORIGINS = True
   CORS_ALLOW_CREDENTIALS = True

   # For production
   CORS_ALLOWED_ORIGINS = [
       "https://skillzone-2vs6.onrender.com",
       # Add your Flutter app domain
   ]

   CORS_ALLOW_METHODS = [
       "DELETE",
       "GET",
       "OPTIONS",
       "PATCH",
       "POST",
       "PUT",
   ]

   CORS_ALLOW_HEADERS = [
       "accept",
       "accept-encoding",
       "authorization",
       "content-type",
       "dnt",
       "origin",
       "user-agent",
       "x-csrftoken",
       "x-requested-with",
   ]
   ```

3. JWT Token Configuration:
   ```python
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
       'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
       'ROTATE_REFRESH_TOKENS': True,
       'BLACKLIST_AFTER_ROTATION': True,
   }
   ```

## 📋 Prerequisites

- Python 3.8+
- pip
- virtualenv
- Git

## 📚 API Overview

### 🔐 Auth

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
```json
{
  "success": true,
  "data": {
    "access": "JWT_TOKEN",
    "refresh": "REFRESH_TOKEN"
  }
}
```

#### Refresh
```http
POST /api/v1/token/refresh/
```

### 👤 Users
- `GET /api/v1/users/profile/`
- `POST /api/v1/users/update-points/`
- `POST /api/v1/users/update-device-token/`

### 📘 Courses
- `GET /api/v1/courses/`
- `GET /api/v1/courses/<id>/`
- `GET /api/v1/courses/<id>/lessons/` - Get all lessons for a specific course
- `POST /api/v1/courses/<id>/unlock/`
- `GET /api/v1/courses/<id>/statistics/`
- `GET /api/v1/courses/inventory/` - Get all courses unlocked by the user
- `POST /api/v1/courses/upload-course/` - Upload a new course (admin only)

### 📗 Lessons
- `POST /api/v1/courses/lessons/<id>/unlock/`
- `POST /api/v1/courses/lessons/<id>/complete/`

### 🧪 Quizzes
- `GET /api/v1/quizzes/courses/<course_id>/quizzes/` - Get all quizzes for a course
- `GET /api/v1/quizzes/quizzes/<id>/` - Get a specific quiz
- `POST /api/v1/quizzes/quizzes/<id>/start/` - Start a quiz attempt
- `POST /api/v1/quizzes/quizzes/<id>/submit/` - Submit quiz answers
- `GET /api/v1/quizzes/quizzes/<id>/statistics/` - Get quiz statistics

### 🏅 Achievements
- `GET /api/v1/achievements/`
- `GET /api/v1/achievements/my_achievements/`
- `GET /api/v1/achievements/available/`

## 🔐 Auth Instructions

Include token in all protected requests:
```http
Authorization: Bearer <your_token>
```

## 🚦 Error Handling

All endpoints return consistent error format:
```json
{
    "success": false,
    "message": "Error description",
    "data": null
}
```

Common HTTP Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

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

4. **Environment Variables**
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
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

## 📦 Deployment

1. **Update settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

3. **Set production environment variables**
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=your-domain.com
   DATABASE_URL=your-database-url
   ```

## 🧪 Running Tests

```bash
python manage.py test
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work - [YourGithub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Django REST Framework
- Simple JWT
- Bootstrap
- All contributors
