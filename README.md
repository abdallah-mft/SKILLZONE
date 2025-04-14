# 🎓 SkillZone Learning Platform

SkillZone is a full-stack learning platform using Django REST Framework and Flutter. It delivers free (SOFT) and premium (HARD) courses, complete with user achievements, quizzes, progress tracking, and a gamified reward system.

---


NOTE : Make sure to add v1 in all urls ( api/v1/....)

## 🚀 Core Features

### 🧠 Courses
- Two types: **SOFT (free)** & **HARD (premium)**
- Video-based lessons with progress sync
- Course completion stats + reward points
- Filter by categories, tags, and difficulty (BEGINNER → ADVANCED)

### 📝 Quizzes
- Linked directly to course content
- Timed attempts + scoring system
- Achievement unlocks based on quiz performance
- Tracks quiz progress

### 🏆 Achievements
- Unlockable by completing lessons, quizzes, and challenges
- Categorized + visual progress indicators
- Grant XP/points for reward system

### 👤 User System
- JWT-based auth
- Custom profile with XP and unlockables
- Points for course unlocks & progress
- Device token handling for push notifications

---

## 🛠️ Tech Stack

### Backend
- Django 5.x + Django REST Framework
- SQLite (dev), PostgreSQL (prod)
- Redis for caching
- JWT via SimpleJWT
- CORS setup

### Frontend (Flutter)
- Flutter SDK (iOS + Android)
- REST API integration
- Local persistence + state management
- JWT auth & token refresh
- Fully responsive components

#### 🔧 Flutter CORS Setup (Backend)
```python
CORS_ALLOW_ALL_ORIGINS = True  # Dev only
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://skillzone-2vs6.onrender.com",
]

CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOW_HEADERS = [
    "accept", "authorization", "content-type", "x-requested-with",
    "origin", "user-agent", "x-csrftoken"
]
```

#### 🔒 JWT Token Config
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

## 📋 Requirements

- Python 3.8+
- pip + virtualenv
- Git

---

## 📚 API Overview

### 🔐 Auth

#### Register
```http
POST /api/users/register/
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
POST /api/users/login/
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
POST /api/token/refresh/
```

### 👤 Users
- `GET /api/users/profile/`
- `POST /api/users/update-points/`
- `POST /api/users/update-device-token/`

### 📘 Courses

- `GET /api/v1/courses/` — Filters: `category`, `difficulty`, `type`, `search`, `page`, `per_page`
- `GET /api/v1/courses/<id>/`
- `POST /api/v1/courses/<id>/unlock/`
- `GET /api/v1/courses/<id>/statistics/`

```json
{
  "success": true,
  "data": {
    "user_stats": { ... },
    "course_stats": { ... }
  }
}
```

### 📗 Lessons
- `POST /api/v1/courses/lessons/<id>/unlock/`
- `POST /api/v1/courses/lessons/<id>/complete/`

### 🧪 Quizzes
- `GET /api/v1/quizzes/<course_id>/`
- `GET /api/v1/quizzes/<id>/`
- `POST /api/v1/quizzes/<id>/attempt/`
- `POST /api/v1/quizzes/<id>/submit/`

### 🏅 Achievements
- `GET /api/v1/achievements/`
- `GET /api/v1/achievements/my_achievements/`
- `GET /api/v1/achievements/available/`

---

## 🔐 Auth Instructions

Include token in all protected requests:
```http
Authorization: Bearer <your_token>
```

---

## 🚨 API Error Format
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

### Common Status Codes
- `200`: OK
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

---

## 🧰 Local Dev Setup

1. Clone repo
```bash
git clone https://github.com/yourusername/skillzone.git
cd skillzone
```

2. Virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env`
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Setup DB
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Start dev server
```bash
python manage.py runserver
```

---

## 🚀 Deployment Steps

1. Update settings
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

2. Collect static files
```bash
python manage.py collectstatic
```

3. Set env vars
```env
DEBUG=False
SECRET_KEY=your-prod-secret
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://...
```

---

## 🧪 Run Tests
```bash
python manage.py test
```

---

## 🙌 Thanks To
- Django REST Framework
- Simple JWT
- Bootstrap
- Every contributor & tester
