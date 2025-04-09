from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='users_index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.get_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('update-points/', views.update_points, name='update-points'),
    path('update-device-token/', views.update_device_token, name='update-device-token'),
    path('verify-email/<str:token>/', views.verify_email, name='verify-email'),
    path('password-reset/', views.password_reset_request, name='password-reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', 
         views.password_reset_confirm, name='password-reset-confirm'),
    path('deactivate-account/', views.deactivate_account, name='deactivate-account'),
    path('profile/avatar/', views.update_avatar, name='update-avatar'),
]
