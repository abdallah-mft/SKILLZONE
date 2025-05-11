from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
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
