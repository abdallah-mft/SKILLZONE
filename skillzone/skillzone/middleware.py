import logging
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)

class DebugRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.info(f"""
        ====== Request Debug ======
        Path: {request.path}
        Method: {request.method}
        Scheme: {request.scheme}
        Headers: {dict(request.headers)}
        Client IP: {request.META.get('REMOTE_ADDR')}
        Is Secure: {request.is_secure()}
        ========================
        """)
        
        return self.get_response(request)

