import psycopg2

# Direct database connection string
database_url = "postgresql://skillzonedb_user:OHazYEfPOkEKHP9JNYpTpEcULy6DDKmF@dpg-d0gdq1re5dus73aajen0-a.oregon-postgres.render.com/skillzonedb"

# Connect to the database
print("Connecting to database...")
conn = psycopg2.connect(database_url)
conn.autocommit = True
cursor = conn.cursor()

# Check if the column exists
cursor.execute("""
SELECT EXISTS (
   SELECT FROM information_schema.columns 
   WHERE table_name = 'courses_course'
   AND column_name = 'points_required'
);
""")
column_exists = cursor.fetchone()[0]

if column_exists:
    print("Column 'points_required' already exists!")
else:
    print("Column 'points_required' does not exist. Creating...")
    
    # SQL to add the column
    add_column_sql = """
    ALTER TABLE public.courses_course 
    ADD COLUMN points_required integer NOT NULL DEFAULT 0;
    """

    try:
        cursor.execute(add_column_sql)
        print("Column 'points_required' added successfully!")
    except Exception as e:
        print(f"Error adding column: {e}")

# Update existing HARD courses to have a default points_required value
update_courses_sql = """
UPDATE public.courses_course
SET points_required = 1000
WHERE course_type = 'HARD' AND points_required = 0;
"""

try:
    cursor.execute(update_courses_sql)
    print("Updated points_required for HARD courses!")
except Exception as e:
    print(f"Error updating courses: {e}")

cursor.close()
conn.close()