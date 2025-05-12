from django.contrib import admin
from django.urls import path, include
from . import views  # Import the views we just created
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Root URL route
    path('', views.api_root, name='api-root'),  # or use views.root_redirect
    
    # Existing paths
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/courses/', include('courses.urls')),
    path('api/v1/quizzes/', include('quizzes.urls')),
    path('api/v1/achievements/', include('achievements.urls')),
    path('api/v1/', include([
        path('users/', include('users.urls')),
        path('courses/', include('courses.urls')),
        path('quizzes/', include('quizzes.urls')),
        path('achievements/', include('achievements.urls')),
    ])),
]
