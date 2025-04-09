from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse

def test_view(request):
    return JsonResponse({"message": "API is working!"})

urlpatterns = [
    path('', test_view, name='test'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('users/', include('users.urls')),
        path('courses/', include('courses.urls')),
        path('quizzes/', include('quizzes.urls')),
        path('achievements/', include('achievements.urls')),
    ])),
]
