from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # This line is important
    path('api/courses/', include('courses.urls')),
    path('api/', include('quizzes.urls')),
]
