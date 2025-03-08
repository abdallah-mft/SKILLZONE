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