from django.urls import path
from . import views

urlpatterns = [
    path('', views.courses_list, name='courses_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/unlock/', views.unlock_lesson, name='unlock-lesson'),
    path('<int:course_id>/unlock/', views.unlock_course, name='unlock-course'),  # Updated path
]
