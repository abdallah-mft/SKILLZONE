import json
from django.core.management.base import BaseCommand
from quizzes.models import Quiz, Question, Answer
from courses.models import Course
from django.db import transaction

class Command(BaseCommand):
    help = 'Import quizzes from JSON data'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing quizzes')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                
            with transaction.atomic():
                self.import_quizzes(data.get('quizzes', []))
                
            self.stdout.write(self.style.SUCCESS('Successfully imported quizzes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing quizzes: {str(e)}'))
    
    def import_quizzes(self, quizzes_data):
        for quiz_data in quizzes_data:
            # Get course by external ID
            course_id = quiz_data.get('courseId')
            try:
                course = Course.objects.get(external_id=course_id)
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Course with external_id {course_id} not found, skipping quiz'))
                continue
            
            # Calculate time limit from timePerQuestion
            time_per_question = quiz_data.get('timePerQuestion', 30)
            question_count = len(quiz_data.get('questions', []))
            time_limit = time_per_question * question_count
            
            # Create quiz
            quiz = Quiz.objects.create(
                course=course,
                title=quiz_data.get('title'),
                description=f"Imported quiz: {quiz_data.get('title')}",
                time_limit=time_limit,
                points_reward=sum(q.get('points', 0) for q in quiz_data.get('questions', [])),
                passing_score=70  # Default passing score
            )
            
            self.stdout.write(f'Created quiz: {quiz.title}')
            
            # Create questions and answers
            for question_data in quiz_data.get('questions', []):
                question = Question.objects.create(
                    quiz=quiz,
                    text=question_data.get('question'),
                    points=question_data.get('points', 1),
                    question_type='MCQ'
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
                
            self.stdout.write(f'Added {question_count} questions to quiz: {quiz.title}')