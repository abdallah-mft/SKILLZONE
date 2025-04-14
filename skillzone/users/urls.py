from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.get_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('update-points/', views.update_points, name='update-points'),
    path('update-device-token/', views.update_device_token, name='update-device-token'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify-email-token'),
]
