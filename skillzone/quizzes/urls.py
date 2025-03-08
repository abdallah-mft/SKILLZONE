from django.urls import path
from . import views

urlpatterns = [
    path('debug/urls/', views.list_urls, name='list-urls'),
    path('courses/<int:course_id>/quizzes/', views.quiz_list, name='quiz-list'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz-detail'),
    path('quizzes/<int:quiz_id>/start/', views.start_quiz, name='start-quiz'),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='submit-quiz'),
    path('quizzes/<int:quiz_id>/statistics/', views.quiz_statistics, name='quiz-statistics'),
]
