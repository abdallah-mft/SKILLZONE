import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
database_url = os.getenv('DATABASE_URL')

# Connect to the database
conn = psycopg2.connect(database_url)
conn.autocommit = True
cursor = conn.cursor()

# SQL to create the table
create_table_sql = """
CREATE TABLE IF NOT EXISTS "courses_unlockedcourse" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "unlocked_at" timestamp with time zone NOT NULL,
    "course_id" bigint NOT NULL REFERENCES "courses_course" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" bigint NOT NULL REFERENCES "users_profile" ("id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "courses_unlockedcourse_user_id_course_id_5a8e5c0c_uniq" UNIQUE ("user_id", "course_id")
);

CREATE INDEX IF NOT EXISTS "courses_unlockedcourse_course_id_a5a0a7f0" ON "courses_unlockedcourse" ("course_id");
CREATE INDEX IF NOT EXISTS "courses_unlockedcourse_user_id_c2a0e1e8" ON "courses_unlockedcourse" ("user_id");
"""

try:
    cursor.execute(create_table_sql)
    print("Table 'courses_unlockedcourse' created successfully!")
except Exception as e:
    print(f"Error creating table: {e}")
finally:
    cursor.close()
    conn.close()