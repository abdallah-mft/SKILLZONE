import json
import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Import quizzes directly using SQL queries'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing quizzes')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"File not found: {json_file}"))
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            with transaction.atomic():
                self.import_quizzes(data.get('quizzes', []))
                
            self.stdout.write(self.style.SUCCESS('Successfully imported quizzes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing quizzes: {str(e)}'))
    
    def import_quizzes(self, quizzes_data):
        # Map course IDs to titles for matching
        course_map = {
            's1': 'Communication',  # Adjust these to match your actual course titles
            'h1': 'Flutter'
        }
        
        # Get all courses
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title FROM courses_course")
            all_courses = cursor.fetchall()
            
        self.stdout.write(f"Available courses: {', '.join([c[1] for c in all_courses])}")
        
        for quiz_data in quizzes_data:
            # Get course by ID mapping to title
            course_id = quiz_data.get('courseId')
            course_title_keyword = course_map.get(course_id)
            
            if not course_title_keyword:
                self.stdout.write(self.style.WARNING(f'No title mapping for course ID {course_id}, skipping quiz'))
                continue
            
            # Find matching course
            matching_course = None
            for course_db_id, course_title in all_courses:
                if course_title_keyword.lower() in course_title.lower():
                    matching_course = (course_db_id, course_title)
                    break
            
            if not matching_course:
                self.stdout.write(self.style.WARNING(f'No courses found with title containing "{course_title_keyword}", skipping quiz'))
                continue
            
            course_db_id, course_title = matching_course
            self.stdout.write(f'Found matching course: {course_title} (ID: {course_db_id})')
            
            # Calculate time limit from timePerQuestion
            time_per_question = quiz_data.get('timePerQuestion', 30)
            question_count = len(quiz_data.get('questions', []))
            time_limit = time_per_question * question_count
            total_points = sum(q.get('points', 0) for q in quiz_data.get('questions', []))
            
            # Check quiz table structure using PostgreSQL syntax
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'quizzes_quiz'
                """)
                quiz_columns = [(col[0], col[1]) for col in cursor.fetchall()]
                self.stdout.write(f"Quiz table columns: {', '.join([f'{col[0]}(nullable:{col[1]})' for col in quiz_columns])}")
            
            # Create quiz using appropriate columns
            with connection.cursor() as cursor:
                # Adjust this SQL based on the actual columns in your quizzes_quiz table
                cursor.execute("""
                    INSERT INTO quizzes_quiz (
                        course_id, title, description, time_limit, points_reward, passing_score,
                        difficulty, category, is_randomized, max_attempts
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, [
                    course_db_id,
                    quiz_data.get('title'),
                    f"Imported quiz: {quiz_data.get('title')}",
                    time_limit,
                    total_points,
                    70,  # Default passing score
                    'MEDIUM',  # Default difficulty
                    'General',  # Default category
                    False,  # Default is_randomized
                    0  # Default max_attempts (0 = unlimited)
                ])
                
                quiz_id = cursor.fetchone()[0]
            
            self.stdout.write(f'Created quiz: {quiz_data.get("title")} for course: {course_title}')
            
            # Check question table structure using PostgreSQL syntax
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'quizzes_question'
                """)
                question_columns = [(col[0], col[1]) for col in cursor.fetchall()]
                self.stdout.write(f"Question table columns: {', '.join([f'{col[0]}(nullable:{col[1]})' for col in question_columns])}")
            
            # Create questions and answers
            for question_data in quiz_data.get('questions', []):
                with connection.cursor() as cursor:
                    # Adjust this SQL based on the actual columns in your quizzes_question table
                    cursor.execute("""
                        INSERT INTO quizzes_question (
                            quiz_id, text, points, question_type, explanation
                        ) VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, [
                        quiz_id,
                        question_data.get('question'),
                        question_data.get('points', 1),
                        'MCQ',
                        ''  # Empty explanation
                    ])
                    
                    question_id = cursor.fetchone()[0]
                
                # Create answers
                options = question_data.get('options', [])
                correct_index = question_data.get('correctOptionIndex', 0)
                
                for i, option_text in enumerate(options):
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO quizzes_answer (
                                question_id, text, is_correct
                            ) VALUES (%s, %s, %s)
                        """, [
                            question_id,
                            option_text,
                            (i == correct_index)
                        ])
                
            self.stdout.write(f'Added {question_count} questions to quiz: {quiz_data.get("title")}')

