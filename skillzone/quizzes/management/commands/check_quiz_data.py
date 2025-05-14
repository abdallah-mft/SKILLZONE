import json
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check quiz data in the database'

    def add_arguments(self, parser):
        parser.add_argument('course_id', type=int, help='Course ID to check')

    def handle(self, *args, **options):
        course_id = options['course_id']
        
        self.stdout.write(f"Checking quiz data for course ID: {course_id}")
        
        # Check if course exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title FROM courses_course WHERE id = %s", [course_id])
            course = cursor.fetchone()
            
            if not course:
                self.stdout.write(self.style.ERROR(f"Course with ID {course_id} not found"))
                return
                
            self.stdout.write(self.style.SUCCESS(f"Found course: {course[1]} (ID: {course[0]})"))
        
        # Check quizzes for this course
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, time_limit, points_reward, passing_score
                FROM quizzes_quiz
                WHERE course_id = %s
            """, [course_id])
            
            quizzes = cursor.fetchall()
            
            if not quizzes:
                self.stdout.write(self.style.ERROR(f"No quizzes found for course ID {course_id}"))
                return
                
            for quiz in quizzes:
                self.stdout.write(self.style.SUCCESS(
                    f"Found quiz: {quiz[1]} (ID: {quiz[0]}, Time: {quiz[2]}s, Points: {quiz[3]}, Passing: {quiz[4]}%)"
                ))
                
                # Check questions for this quiz
                cursor.execute("""
                    SELECT id, text, points, question_type
                    FROM quizzes_question
                    WHERE quiz_id = %s
                """, [quiz[0]])
                
                questions = cursor.fetchall()
                
                if not questions:
                    self.stdout.write(self.style.WARNING(f"No questions found for quiz ID {quiz[0]}"))
                    continue
                    
                self.stdout.write(f"Found {len(questions)} questions for quiz ID {quiz[0]}")
                
                # Check first 3 questions and their answers
                for i, question in enumerate(questions[:3]):
                    self.stdout.write(f"  Question {i+1}: {question[1]} (ID: {question[0]}, Points: {question[2]}, Type: {question[3]})")
                    
                    # Check answers for this question
                    cursor.execute("""
                        SELECT id, text, is_correct
                        FROM quizzes_answer
                        WHERE question_id = %s
                    """, [question[0]])
                    
                    answers = cursor.fetchall()
                    
                    if not answers:
                        self.stdout.write(self.style.WARNING(f"    No answers found for question ID {question[0]}"))
                        continue
                        
                    for answer in answers:
                        correct_mark = "✓" if answer[2] else " "
                        self.stdout.write(f"    Answer: [{correct_mark}] {answer[1]} (ID: {answer[0]})")
                
                if len(questions) > 3:
                    self.stdout.write(f"  ... and {len(questions) - 3} more questions")