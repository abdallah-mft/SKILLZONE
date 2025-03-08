from django.urls import path
from . import views

urlpatterns = [
    path('courses/<int:course_id>/quizzes/', views.quiz_list),
    path('quizzes/<int:quiz_id>/', views.quiz_detail),
    path('quizzes/<int:quiz_id>/start/', views.start_quiz),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz),
]