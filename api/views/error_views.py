from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

def custom_404(request, exception=None):
    """
    Custom handler for 404 Not Found errors.
    Returns a consistent JSON response format.
    """
    error_data = {
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'The requested resource was not found.',
            'details': {
                'path': request.path,
                'method': request.method,
            }
        }
    }

    # Log the 404 error if debug is disabled
    if not settings.DEBUG:
        logger.warning(
            f"404 Not Found: {request.method} {request.path}",
            extra={
                'status_code': 404,
                'request': request,
            }
        )

    return JsonResponse(error_data, status=status.HTTP_404_NOT_FOUND)

def custom_500(request, *args, **kwargs):
    """
    Custom handler for 500 Internal Server Error.
    Returns a consistent JSON response format and logs the error.
    """
    error_data = {
        'success': False,
        'error': {
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'An unexpected error occurred.',
        }
    }

    # Add debug information if DEBUG is enabled
    if settings.DEBUG:
        import traceback
        error_data['error']['details'] = {
            'traceback': traceback.format_exc(),
        }

    # Log the error
    logger.error(
        'Internal Server Error',
        exc_info=True,
        extra={
            'status_code': 500,
            'request': request,
        }
    )

    return JsonResponse(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ErrorPreviewView(APIView):
    """
    View for testing error responses in development.
    Only available when DEBUG is True.
    """
    def get(self, request, error_code):
        """
        Trigger various error responses for testing.
        Usage: /api/error-preview/<error_code>/
        """
        if not settings.DEBUG:
            return custom_404(request)

        if error_code == '404':
            return custom_404(request)
        elif error_code == '500':
            return custom_500(request)
        elif error_code == 'validation':
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Validation failed.',
                        'details': {
                            'field1': ['This field is required.'],
                            'field2': ['Invalid value.'],
                        }
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif error_code == 'permission':
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': 'You do not have permission to perform this action.',
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        elif error_code == 'throttled':
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'THROTTLED',
                        'message': 'Request was throttled.',
                        'details': {
                            'wait': 60,
                        }
                    }
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'INVALID_ERROR_CODE',
                        'message': f'Invalid error code: {error_code}',
                        'details': {
                            'available_codes': ['404', '500', 'validation', 'permission', 'throttled'],
                        }
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )