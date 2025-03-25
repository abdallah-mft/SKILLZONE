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
