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
        
        # Return a friendly message for HTTPS attempts
        if request.is_secure():
            return JsonResponse({
                "error": "Please use HTTP instead of HTTPS",
                "message": "For development, access the API via http://127.0.0.1:8000"
            }, status=400)
        
        return self.get_response(request)

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if not settings.DEBUG:  # Now settings is properly imported
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "connect-src 'self';"
            )
        
        return response

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/v1/users/login/'):
            ip = self.get_client_ip(request)
            key = f'login_attempts_{ip}'
            attempts = cache.get(key, 0)

            if attempts >= 5:
                return JsonResponse({
                    'success': False,
                    'message': 'Too many login attempts. Please try again later.'
                }, status=429)

            cache.set(key, attempts + 1, 900)  # 15 minutes timeout

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "connect-src 'self';"
            )
            
        return response

