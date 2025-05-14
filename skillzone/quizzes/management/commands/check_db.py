from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Run SQL queries to check database state'

    def handle(self, *args, **options):
        # Check courses
        self.stdout.write(self.style.SUCCESS("Checking courses table:"))
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title FROM courses_course LIMIT 10")
            courses = cursor.fetchall()
            for course in courses:
                self.stdout.write(f"Course ID: {course[0]}, Title: {course[1]}")
        
        # Check quizzes
        self.stdout.write(self.style.SUCCESS("\nChecking quizzes table:"))
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, course_id, title FROM quizzes_quiz LIMIT 10")
            quizzes = cursor.fetchall()
            for quiz in quizzes:
                self.stdout.write(f"Quiz ID: {quiz[0]}, Course ID: {quiz[1]}, Title: {quiz[2]}")
        
        # Check questions
        self.stdout.write(self.style.SUCCESS("\nChecking questions table:"))
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, quiz_id, text FROM quizzes_question LIMIT 10")
            questions = cursor.fetchall()
            for question in questions:
                self.stdout.write(f"Question ID: {question[0]}, Quiz ID: {question[1]}, Text: {question[2][:50]}...")
        
        # Check answers
        self.stdout.write(self.style.SUCCESS("\nChecking answers table:"))
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, question_id, text, is_correct FROM quizzes_answer LIMIT 10")
            answers = cursor.fetchall()
            for answer in answers:
                self.stdout.write(f"Answer ID: {answer[0]}, Question ID: {answer[1]}, Text: {answer[2][:30]}..., Correct: {answer[3]}")
        
        # Check specifically for course ID 17
        self.stdout.write(self.style.SUCCESS("\nChecking specifically for course ID 17:"))
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title FROM courses_course WHERE id = 17")
            course = cursor.fetchone()
            if course:
                self.stdout.write(f"Found course: {course[1]} (ID: {course[0]})")
                
                # Check quizzes for this course
                cursor.execute("SELECT id, title FROM quizzes_quiz WHERE course_id = 17")
                quizzes = cursor.fetchall()
                if quizzes:
                    for quiz in quizzes:
                        self.stdout.write(f"  Quiz: {quiz[1]} (ID: {quiz[0]})")
                        
                        # Check questions for this quiz
                        cursor.execute("SELECT COUNT(*) FROM quizzes_question WHERE quiz_id = %s", [quiz[0]])
                        question_count = cursor.fetchone()[0]
                        self.stdout.write(f"    Questions: {question_count}")
                        
                        # Check if any questions have no answers
                        cursor.execute("""
                            SELECT q.id FROM quizzes_question q
                            LEFT JOIN quizzes_answer a ON q.id = a.question_id
                            WHERE q.quiz_id = %s AND a.id IS NULL
                        """, [quiz[0]])
                        questions_without_answers = cursor.fetchall()
                        if questions_without_answers:
                            self.stdout.write(self.style.ERROR(f"    Questions without answers: {len(questions_without_answers)}"))
                            for q in questions_without_answers[:5]:
                                self.stdout.write(self.style.ERROR(f"      Question ID: {q[0]}"))
                        
                        # Check if any questions have no correct answers
                        cursor.execute("""
                            SELECT q.id FROM quizzes_question q
                            LEFT JOIN quizzes_answer a ON q.id = a.question_id AND a.is_correct = true
                            WHERE q.quiz_id = %s
                            GROUP BY q.id
                            HAVING COUNT(a.id) = 0
                        """, [quiz[0]])
                        questions_without_correct = cursor.fetchall()
                        if questions_without_correct:
                            self.stdout.write(self.style.ERROR(f"    Questions without correct answers: {len(questions_without_correct)}"))
                            for q in questions_without_correct[:5]:
                                self.stdout.write(self.style.ERROR(f"      Question ID: {q[0]}"))
                else:
                    self.stdout.write(self.style.ERROR("  No quizzes found for this course"))
            else:
                self.stdout.write(self.style.ERROR("Course with ID 17 not found"))