from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses across the API.
    
    Format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {} // Optional additional error details
        }
    }
    """
    
    # First, get the standard DRF exception response
    response = exception_handler(exc, context)
    
    # If this is a Django validation error, convert it to DRF validation error
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(detail=exc.messages)
    
    # If there's no response, create one for unhandled exceptions
    if response is None:
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'An unexpected error occurred.',
                    'details': str(exc) if str(exc) else None
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Format the error response
    error_data = {
        'success': False,
        'error': {
            'code': _get_error_code(exc, response.status_code),
            'message': _get_error_message(exc, response.data),
            'details': _get_error_details(response.data)
        }
    }
    
    response.data = error_data
    return response

def _get_error_code(exc, status_code):
    """
    Get a standardized error code based on the exception type and status code.
    """
    if hasattr(exc, 'code'):
        return exc.code
    
    if hasattr(exc, 'default_code'):
        return exc.default_code.upper()
    
    # Map status codes to default error codes
    status_code_map = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        409: 'CONFLICT',
        429: 'TOO_MANY_REQUESTS',
        500: 'INTERNAL_SERVER_ERROR',
    }
    
    return status_code_map.get(status_code, 'UNKNOWN_ERROR')

def _get_error_message(exc, data):
    """
    Get a human-readable error message.
    """
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, (list, dict)):
            return "Validation error occurred."
        return str(exc.detail)
    
    if isinstance(data, dict) and 'detail' in data:
        return str(data['detail'])
    
    return str(exc)

def _get_error_details(data):
    """
    Extract detailed error information from the response data.
    """
    if isinstance(data, dict):
        if 'detail' in data and isinstance(data['detail'], (list, dict)):
            return data['detail']
        # Remove any 'detail' key as it's already used in the message
        details = data.copy()
        details.pop('detail', None)
        return details if details else None
    
    if isinstance(data, list):
        return {'errors': data}
    
    return None

class APIError(Exception):
    """
    Base exception class for custom API errors.
    """
    def __init__(self, message, code=None, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.status_code = status_code
        self.details = details
    
    @property
    def detail(self):
        return self.message

class ValidationError(APIError):
    """
    Exception for validation errors.
    """
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='VALIDATION_ERROR',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class NotFoundError(APIError):
    """
    Exception for resource not found errors.
    """
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='NOT_FOUND',
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

class ConflictError(APIError):
    """
    Exception for conflict errors (e.g., duplicate entries).
    """
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='CONFLICT',
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )

# api/exceptions.py
# Add these exception classes

class BulkOperationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred during bulk operation.'
    default_code = 'bulk_operation_error'

class BulkValidationError(BulkOperationError):
    default_detail = 'Validation failed for bulk operation.'
    default_code = 'bulk_validation_error'

class BulkFileError(BulkOperationError):
    default_detail = 'Error processing bulk operation file.'
    default_code = 'bulk_file_error'