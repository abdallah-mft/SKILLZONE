from django.urls import path
from . import views

urlpatterns = [
    path('', views.courses_list, name='courses_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/unlock/', views.unlock_lesson, name='unlock-lesson'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='complete-lesson'),
    path('<int:course_id>/unlock/', views.unlock_course, name='unlock-course'),
    path('<int:course_id>/statistics/', views.course_statistics, name='course-statistics'),
]
