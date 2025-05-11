import psycopg2

# Direct database connection string
database_url = "postgresql://skillzonedb_user:OHazYEfPOkEKHP9JNYpTpEcULy6DDKmF@dpg-d0gdq1re5dus73aajen0-a.oregon-postgres.render.com/skillzonedb"

# Connect to the database
print("Connecting to database...")
conn = psycopg2.connect(database_url)
conn.autocommit = True
cursor = conn.cursor()

# First, check if the table exists
cursor.execute("""
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_schema = 'public'
   AND table_name = 'courses_unlockedcourse'
);
""")
table_exists = cursor.fetchone()[0]

if table_exists:
    print("Table 'courses_unlockedcourse' already exists!")
else:
    print("Table 'courses_unlockedcourse' does not exist. Creating...")
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE public.courses_unlockedcourse (
        id bigserial NOT NULL PRIMARY KEY,
        unlocked_at timestamp with time zone NOT NULL,
        course_id bigint NOT NULL,
        user_id bigint NOT NULL,
        CONSTRAINT courses_unlockedcourse_user_id_course_id_5a8e5c0c_uniq UNIQUE (user_id, course_id)
    );

    ALTER TABLE public.courses_unlockedcourse 
    ADD CONSTRAINT courses_unlockedcourse_course_id_fkey 
    FOREIGN KEY (course_id) REFERENCES public.courses_course(id) DEFERRABLE INITIALLY DEFERRED;

    ALTER TABLE public.courses_unlockedcourse 
    ADD CONSTRAINT courses_unlockedcourse_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users_profile(id) DEFERRABLE INITIALLY DEFERRED;

    CREATE INDEX courses_unlockedcourse_course_id_a5a0a7f0 ON public.courses_unlockedcourse(course_id);
    CREATE INDEX courses_unlockedcourse_user_id_c2a0e1e8 ON public.courses_unlockedcourse(user_id);
    """

    try:
        cursor.execute(create_table_sql)
        print("Table 'courses_unlockedcourse' created successfully!")
    except Exception as e:
        print(f"Error creating table: {e}")
        
# List all tables to verify
cursor.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
""")

tables = cursor.fetchall()
print("\nExisting tables in the database:")
for table in tables:
    print(f"- {table[0]}")

cursor.close()
conn.close()