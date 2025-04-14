from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def test_view(request):
    logger.info(f"Request received: {request.scheme}://{request.get_host()}{request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    return JsonResponse({
        "message": "API is working!",
        "scheme": request.scheme,
        "host": request.get_host(),
        "path": request.path
    })

urlpatterns = [
    path('', test_view, name='test'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # Make sure this exists
    path('api/v1/', include([
        path('users/', include('users.urls')),
        path('courses/', include('courses.urls')),
        path('quizzes/', include('quizzes.urls')),
        path('achievements/', include('achievements.urls')),
    ])),
]
