import logging
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class DebugRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only log in debug mode
        if settings.DEBUG:
            logger.info(f"""
            ====== Request Debug ======
            Path: {request.path}
            Method: {request.method}
            Scheme: {request.scheme}
            Headers: {dict(request.headers)}
            ========================
            """)
        
        # Remove this check in production or handle it differently
        # if request.is_secure():
        #     return HttpResponse(
        #         "HTTPS connection attempted. Please use HTTP instead.",
        #         status=400
        #     )
        
        return self.get_response(request)

