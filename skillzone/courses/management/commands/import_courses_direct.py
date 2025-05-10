import json
from django.core.management.base import BaseCommand
from django.db import transaction, connection

class Command(BaseCommand):
    help = 'Import courses and lessons directly using SQL'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing course data')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in file: {json_file}'))
            return
        
        with transaction.atomic():
            # Process soft skills courses
            self.stdout.write('Importing soft skills courses...')
            self._process_courses(data.get('softSkillsCourses', []), 'SOFT')
            
            # Process hard skills courses
            self.stdout.write('Importing hard skills courses...')
            self._process_courses(data.get('hardSkillsCourses', []), 'HARD')
            
        self.stdout.write(self.style.SUCCESS('Successfully imported all courses and lessons!'))
    
    def _process_courses(self, courses_data, course_type):
        for course_data in courses_data:
            # Map difficulty level based on points
            points_value = course_data.get('points', 0)
            if course_type == 'HARD':
                if points_value >= 700:
                    difficulty = 'ADVANCED'
                elif points_value >= 400:
                    difficulty = 'INTERMEDIATE'
                else:
                    difficulty = 'BEGINNER'
            else:
                if points_value >= 150:
                    difficulty = 'ADVANCED'
                elif points_value >= 100:
                    difficulty = 'INTERMEDIATE'
                else:
                    difficulty = 'BEGINNER'
            
            # Insert course using raw SQL
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO courses_course (
                        title, description, course_type, points_required, category, 
                        tags, difficulty_level, points_reward, duration, price, rating
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, [
                    course_data.get('title', ''),
                    course_data.get('description', ''),
                    course_type,
                    points_value if course_type == 'HARD' else 0,
                    'Technology' if course_type == 'HARD' else 'Professional Development',
                    ','.join([course_data.get('title', ''), course_type.lower(), difficulty.lower()]),
                    difficulty,
                    points_value,
                    course_data.get('duration', 0),
                    course_data.get('price', 0.00) if course_type == 'HARD' else 0.00,
                    course_data.get('rating', 0.0)
                ])
                
                course_id = cursor.fetchone()[0]
            
            self.stdout.write(f'  Created course: {course_data.get("title", "")}')
            
            # Create lessons for this course
            lessons_data = course_data.get('lessons', [])
            for i, lesson_data in enumerate(lessons_data, 1):
                # Calculate points required for each lesson
                # For simplicity, we'll divide course points by number of lessons
                # or set a default value if there are no lessons
                lesson_points = 0
                if course_type == 'HARD':
                    total_lessons = len(lessons_data) or 1
                    lesson_points = points_value // total_lessons
                
                # Insert lesson using raw SQL
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO courses_lesson (
                            course_id, title, video_url, number, duration, points_required
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        course_id,
                        lesson_data.get('title', ''),
                        lesson_data.get('videoUrl', ''),
                        i,
                        lesson_data.get('duration', 0),
                        lesson_points  # Add points_required value
                    ])
                
                self.stdout.write(f'    Created lesson: {lesson_data.get("title", "")}')
