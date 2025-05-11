from django.urls import path
from . import views

urlpatterns = [
    # Put the inventory endpoint first to avoid conflicts
    path('inventory/', views.user_course_inventory, name='user-course-inventory'),
    
    # Add the upload course endpoint
    path('upload-course/', views.upload_course, name='upload-course'),
    
    # Add the new course lessons endpoint
    path('<int:course_id>/lessons/', views.course_lessons, name='course-lessons'),
    
    # Then the other endpoints
    path('', views.courses_list, name='courses_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/unlock/', views.unlock_lesson, name='unlock-lesson'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='complete-lesson'),
    path('<int:course_id>/unlock/', views.unlock_course, name='unlock-course'),
    path('<int:course_id>/statistics/', views.course_statistics, name='course-statistics'),
]
