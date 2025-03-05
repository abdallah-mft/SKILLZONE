from django.urls import path
from . import views

urlpatterns = [
    path('', views.courses_list, name='courses_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
]
