import logging
import json
from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from django.core.cache import cache
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger(__name__)

class FlutterErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.process_exception(request, e)

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exception, APIException):
            status_code = exception.status_code
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        error_message = str(exception)
        logger.error(f"Error processing request: {error_message}")

        return JsonResponse({
            'success': False,
            'message': error_message,
            'data': None
        }, status=status_code)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request
        logger.info(f"Request {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        
        response = self.get_response(request)
        
        # Log the response
        logger.info(f"Response {response.status_code}")
        return response

    def process_exception(self, request, exception):
        logger.error(f"Exception in {request.method} {request.path}: {str(exception)}")
        return None

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/v1/users/login/'):
            ip = self.get_client_ip(request)
            key = f'login_attempts_{ip}'
            attempts = cache.get(key, 0)

            if attempts >= 5:
                return Response({
                    'success': False,
                    'message': 'Too many login attempts. Please try again later.'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

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

