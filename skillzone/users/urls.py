from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.get_profile, name='profile'),
    path('update-points/', views.update_points, name='update-points'),
    path('update-device-token/', views.update_device_token, name='update-device-token'),
    path('', views.users_index, name='users_index'),
]
