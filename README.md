# 🎓 SkillZone Learning Platform

A modern learning platform built with Django REST Framework and React, offering both free (SOFT) and premium (HARD) courses with integrated achievements, quizzes, and user progression system.

## 🚀 Features

### Course System
- Two course types: SOFT (free) and HARD (premium)
- Video-based lessons
- Progress tracking
- Course completion statistics
- Points-based reward system
- Course categories and tags
- Difficulty levels (BEGINNER, INTERMEDIATE, ADVANCED)

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
- Django 5.x
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

## 🔍 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/users/register/
```
Request Body:
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
POST /api/users/login/
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
POST /api/token/refresh/
```

### User Endpoints

#### Get Profile
```http
GET /api/users/profile/
```

#### Update Points
```http
POST /api/users/update-points/
```

#### Update Device Token
```http
POST /api/users/update-device-token/
```

### Course Endpoints

#### List Courses
```http
GET /api/v1/courses/
```
Query Parameters:
- `category`: Filter by category
- `difficulty`: BEGINNER, INTERMEDIATE, ADVANCED
- `type`: SOFT, HARD
- `search`: Search in title and description
- `page`: Page number
- `per_page`: Items per page

Response:
```json
{
    "success": true,
    "data": {
        "courses": [...],
        "pagination": {
            "total": 100,
            "page": 1,
            "per_page": 10,
            "total_pages": 10
        },
        "user_points": 500,
        "filters": {
            "categories": [...],
            "tags": [...],
            "difficulties": [...],
            "types": [...]
        }
    }
}
```

#### Get Course Details
```http
GET /api/v1/courses/<id>/
```

#### Unlock Course
```http
POST /api/v1/courses/<id>/unlock/
```

#### Get Course Statistics
```http
GET /api/v1/courses/<id>/statistics/
```
Response:
```json
{
    "success": true,
    "data": {
        "user_stats": {
            "completion_percentage": 75,
            "time_spent_minutes": 120,
            "completed_lessons": 15,
            "completed_quizzes": 3,
            "points_earned": 500
        },
        "course_stats": {
            "total_students": 1000,
            "completion_rate": 68,
            "quiz_scores": {...}
        }
    }
}
```

### Lesson Endpoints

#### Unlock Lesson
```http
POST /api/v1/courses/lessons/<id>/unlock/
```

#### Complete Lesson
```http
POST /api/v1/courses/lessons/<id>/complete/
```

### Quiz Endpoints

#### List Course Quizzes
```http
GET /api/v1/quizzes/<course_id>/
```

#### Get Quiz Details
```http
GET /api/v1/quizzes/<id>/
```

#### Start Quiz Attempt
```http
POST /api/v1/quizzes/<id>/attempt/
```

#### Submit Quiz
```http
POST /api/v1/quizzes/<id>/submit/
```

### Achievement Endpoints

#### List Achievements
```http
GET /api/v1/achievements/
```

#### My Achievements
```http
GET /api/v1/achievements/my_achievements/
```

#### Available Achievements
```http
GET /api/v1/achievements/available/
```

## 🔐 Authentication

The API uses JWT authentication. Include the token in all requests:
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



## 🙏 Acknowledgments

- Django REST Framework
- Simple JWT
- Bootstrap
- All contributors
