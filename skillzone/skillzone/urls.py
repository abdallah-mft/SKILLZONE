from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    # Root URL route
    path('', views.api_root, name='api-root'),
    
    # JWT Token endpoints
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Existing paths
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/users/', include('users.urls')),
    path('api/v1/courses/', include('courses.urls')),
    path('api/v1/quizzes/', include('quizzes.urls')),
    path('api/v1/achievements/', include('achievements.urls')),
]
