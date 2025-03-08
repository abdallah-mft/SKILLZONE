import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Quiz, Question, Answer, QuizAttempt
from courses.models import Course

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def course():
    return Course.objects.create(
        title='Test Course',
        description='Test Description',
        course_type='SOFT'
    )

@pytest.fixture
def quiz(course):
    return Quiz.objects.create(
        course=course,
        title='Test Quiz',
        description='Test Quiz Description',
        time_limit=300,
        points_reward=10,
        passing_score=70
    )

@pytest.mark.django_db
class TestQuizAPI:
    def test_start_quiz(self, api_client, user, quiz):
        api_client.force_authenticate(user=user)
        url = reverse('start-quiz', kwargs={'quiz_id': quiz.id})
        response = api_client.post(url)
        
        assert response.status_code == 200
        assert 'attempt_id' in response.data
        assert response.data['remaining_time'] == quiz.time_limit

    def test_submit_quiz(self, api_client, user, quiz):
        # Create a question with answers
        question = Question.objects.create(quiz=quiz, text='Test Question', points=5)
        correct_answer = Answer.objects.create(
            question=question,
            text='Correct Answer',
            is_correct=True
        )
        wrong_answer = Answer.objects.create(
            question=question,
            text='Wrong Answer',
            is_correct=False
        )

        # Start quiz attempt
        api_client.force_authenticate(user=user)
        start_url = reverse('start-quiz', kwargs={'quiz_id': quiz.id})
        start_response = api_client.post(start_url)
        
        # Submit answers
        submit_url = reverse('submit-quiz', kwargs={'quiz_id': quiz.id})
        submit_response = api_client.post(submit_url, {
            'answers': {
                str(question.id): correct_answer.id
            }
        })
        
        assert submit_response.status_code == 200
        assert submit_response.data['score'] == 100
        assert submit_response.data['is_passed'] == True

    def test_quiz_statistics(self, api_client, user, quiz):
        api_client.force_authenticate(user=user)
        url = reverse('quiz-statistics', kwargs={'quiz_id': quiz.id})
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert 'user_statistics' in response.data
        assert 'overall_statistics' in response.data