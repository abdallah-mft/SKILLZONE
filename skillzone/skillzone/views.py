from django.http import JsonResponse
from django.shortcuts import redirect

def api_root(request):
    """Root endpoint that provides API information or redirects to documentation"""
    return JsonResponse({
        "message": "Welcome to SkillZone API",
        "version": "1.0",
        "documentation": "/api/docs/",  # If you have API docs
        "endpoints": {
            "users": "/api/v1/users/",
            "courses": "/api/v1/courses/",
            "quizzes": "/api/v1/quizzes/",
            "achievements": "/api/v1/achievements/"
        }
    })

# Alternative: Redirect to documentation or admin
def root_redirect(request):
    """Redirect root URL to documentation, admin, or another page"""
    return redirect('/api/v1/')  # or redirect to admin, docs, etc.