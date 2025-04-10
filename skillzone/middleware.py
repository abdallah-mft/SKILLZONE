import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class DebugRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"""
        ====== Request Debug ======
        Path: {request.path}
        Method: {request.method}
        Scheme: {request.scheme}
        Headers: {dict(request.headers)}
        ========================
        """)
        
        if request.is_secure():
            return HttpResponse(
                "HTTPS connection attempted. Please use HTTP instead.",
                status=400
            )
        
        return self.get_response(request)
