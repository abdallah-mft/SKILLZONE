import logging
import json
from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException

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

