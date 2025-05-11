import logging
import traceback
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Log the full exception with traceback
    logger.error(f"Exception in {context['view'].__class__.__name__}: {str(exc)}")
    logger.error(traceback.format_exc())
    
    response = exception_handler(exc, context)

    if response is None:
        return Response({
            'success': False,
            'message': str(exc),
            'data': None,
            'error_type': exc.__class__.__name__
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Modify the response format to match our standard
    return Response({
        'success': False,
        'message': str(exc),
        'data': response.data if hasattr(response, 'data') else None,
        'error_type': exc.__class__.__name__
    }, status=response.status_code)
