# Skillzone

## Database Setup

The project supports both SQLite and PostgreSQL:

### SQLite (Default)
No additional setup required. The project will use SQLite by default.

### PostgreSQL
1. Install PostgreSQL and pgAdmin
2. Copy `.env.example` to `.env`
3. Set `USE_POSTGRES=True` in `.env`
4. Update database credentials in `.env`
5. Run migrations:
   ```bash
   python manage.py migrate
   ```

## Project Structure
```bash
skillzone/
├── skillzone/          # Project Settings
├── users/             # User Authentication & Profiles
├── courses/           # Course Management
├── quizzes/           # Quiz System
├── achievements/      # Achievement System
└── manage.py         # Django CLI
```

## Setup Instructions
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints
- Users: `/api/users/`
- Courses: `/api/courses/`
- Quizzes: `/api/quizzes/`
- Achievements: `/api/achievements/`


# SKILLZONE API DOCUMENTATION

## Base URL
```
https://skillzone-4ewv.onrender.com/api/v1
```

## Authentication
- Type: JWT (JSON Web Token)
- Headers: `Authorization: Bearer <access_token>`

## API Endpoints

### 1. Authentication Endpoints

#### 1.1 Register
- **URL**: `/users/register/`
- **Method**: POST
- **Body**:
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password",
    "first_name": "First",
    "last_name": "Last"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Registration successful. Please check your email to verify your account.",
    "data": {
        "tokens": {
            "access": "access_token_here",
            "refresh": "refresh_token_here"
        },
        "user": {
            "user": {
                "id": 1,
                "username": "username",
                "email": "user@example.com",
                "first_name": "First",
                "last_name": "Last"
            },
            "points": 0,
            "full_name": "First Last",
            "level": null,
            "next_level": null,
            "points_to_next_level": null
        }
    }
}
```

#### 1.2 Login
- **URL**: `/users/login/`
- **Method**: POST
- **Body**:
```json
{
    "email": "user@example.com",  // Can use email or username
    "password": "password"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "tokens": {
            "access": "access_token_here",
            "refresh": "refresh_token_here"
        },
        "user": {
            // Same user object as register response
        }
    }
}
```

#### 1.3 Logout
- **URL**: `/users/logout/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "refresh_token": "refresh_token_here"
}
```

#### 1.4 Refresh Token
- **URL**: `/api/token/refresh/`
- **Method**: POST
- **Body**:
```json
{
    "refresh": "refresh_token_here"
}
```

#### 1.5 Update Device Token
- **URL**: `/users/update-device-token/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "device_token": "firebase_device_token"
}
```

### 2. Profile Endpoints

#### 2.1 Get Profile
- **URL**: `/users/profile/`
- **Method**: GET
- **Auth**: Required

#### 2.2 Update Profile
- **URL**: `/users/profile/update/`
- **Method**: POST
- **Auth**: Required
- **Body**: FormData (multipart/form-data)
```json
{
    "first_name": "New First",
    "last_name": "New Last",
    "bio": "New bio",
    "avatar": "file_upload"
}
```

#### 2.3 Update Points
- **URL**: `/users/update-points/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "points": 100
}
```

### 3. Password Management

#### 3.1 Request Password Reset
- **URL**: `/users/password-reset/`
- **Method**: POST
- **Body**:
```json
{
    "email": "user@example.com"
}
```

#### 3.2 Change Password
- **URL**: `/users/profile/change-password/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "old_password": "old_password",
    "new_password": "new_password"
}
```

## Important Implementation Notes

### 1. Error Handling
All endpoints return consistent error format:
```json
{
    "success": false,
    "message": "Error message here",
    "data": null
}
```

### 2. Authentication Headers
Add access token to all authenticated requests:
```dart
headers: {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json'
}
```

### 3. Token Management
- Store both access and refresh tokens securely
- Implement token refresh logic when getting 401 errors
- Use the refresh token endpoint to get new access token

### 4. File Upload Guidelines
- Use multipart/form-data for avatar uploads
- Maximum file size: 5MB
- Supported formats: JPG, PNG, GIF

### 5. Rate Limiting
- API requests are limited to 100 requests per minute per user
- Exceeding this limit will return a 429 Too Many Requests error

### 6. Best Practices
- Always validate user input before sending to API
- Implement proper error handling for network issues
- Cache appropriate responses to minimize API calls
- Implement proper logout flow by clearing stored tokens