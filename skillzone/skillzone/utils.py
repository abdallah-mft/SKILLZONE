from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response({
            'success': False,
            'message': str(exc),
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Modify the response format to match our standard
    return Response({
        'success': False,
        'message': str(exc),
        'data': response.data if hasattr(response, 'data') else None
    }, status=response.status_code)