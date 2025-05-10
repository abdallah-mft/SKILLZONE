import json
from django.core.management.base import BaseCommand
from django.db import transaction
from courses.models import Course
from quizzes.models import Quiz, Question, Answer

class Command(BaseCommand):
    help = 'Import quizzes from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing quiz data')

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
            self._import_quizzes(data.get('quizzes', []))
            
        self.stdout.write(self.style.SUCCESS('Successfully imported all quizzes!'))
    
    def _import_quizzes(self, quizzes_data):
        for quiz_data in quizzes_data:
            # Find the course by external ID
            course_id = quiz_data.get('courseId')
            course = Course.objects.filter(title__contains=course_id.upper()).first()
            
            if not course:
                self.stdout.write(self.style.WARNING(f'Course not found for ID: {course_id}'))
                continue
            
            # Calculate time limit (seconds per question * number of questions)
            time_per_question = quiz_data.get('timePerQuestion', 30)
            questions_count = len(quiz_data.get('questions', []))
            time_limit = time_per_question * questions_count
            
            # Create the quiz
            quiz = Quiz.objects.create(
                course=course,
                title=quiz_data.get('title', ''),
                description=f"Quiz for {course.title}",
                time_limit=time_limit,
                points_reward=sum(q.get('points', 0) for q in quiz_data.get('questions', [])),
                passing_score=70,  # Default passing score
                difficulty='MEDIUM',  # Default difficulty
                is_randomized=True
            )
            
            self.stdout.write(f'Created quiz: {quiz.title}')
            
            # Create questions and answers
            for question_data in quiz_data.get('questions', []):
                question = Question.objects.create(
                    quiz=quiz,
                    text=question_data.get('question', ''),
                    points=question_data.get('points', 1),
                    question_type='MCQ'  # Multiple choice
                )
                
                # Create answers
                options = question_data.get('options', [])
                correct_index = question_data.get('correctOptionIndex', 0)
                
                for i, option_text in enumerate(options):
                    Answer.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=(i == correct_index)
                    )
                
                self.stdout.write(f'  Created question: {question.text[:30]}...')