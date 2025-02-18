"""
API Logging Middleware
"""

import json
import logging
import time
from django.conf import settings

logger = logging.getLogger('api')

class APILoggingMiddleware:
    """Middleware to log API requests and responses"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip logging for non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Start timing the request
        start_time = time.time()

        # Log the request
        self.log_request(request)

        # Get the response
        response = self.get_response(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Log the response
        self.log_response(request, response, duration)

        return response

    def log_request(self, request):
        """Log the API request details"""
        try:
            # Get request body for POST/PUT/PATCH
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.content_type == 'application/json':
                    body = json.loads(request.body) if request.body else None
                else:
                    body = request.POST.dict()

            # Mask sensitive data
            if body and any(key in str(body).lower() for key in ['password', 'token', 'secret', 'key']):
                body = self.mask_sensitive_data(body)

            log_data = {
                'method': request.method,
                'path': request.path,
                'query_params': request.GET.dict(),
                'body': body,
                'headers': dict(request.headers),
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'ip': self.get_client_ip(request)
            }

            logger.info(f"{request.method} {request.path}", extra={'request_data': log_data})

        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")

    def log_response(self, request, response, duration):
        """Log the API response details"""
        try:
            # Get response body for JSON responses
            body = None
            if 'application/json' in response.get('Content-Type', ''):
                try:
                    body = json.loads(response.content)
                    # Mask sensitive data in response
                    if any(key in str(body).lower() for key in ['password', 'token', 'secret', 'key']):
                        body = self.mask_sensitive_data(body)
                except:
                    body = '<Unable to parse JSON response>'

            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': f"{duration:.3f}s",
                'content_length': len(response.content) if response.content else 0,
                'body': body
            }

            if 200 <= response.status_code < 300:
                logger.info(
                    f"Success response for {request.method} {request.path}",
                    extra={'response_data': log_data}
                )
            else:
                logger.warning(
                    f"Error response for {request.method} {request.path}",
                    extra={'response_data': log_data}
                )

        except Exception as e:
            logger.error(f"Error logging response: {str(e)}")

    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def mask_sensitive_data(self, data):
        """Mask sensitive information in logs"""
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                    masked_data[key] = '********'
                else:
                    masked_data[key] = self.mask_sensitive_data(value)
            return masked_data
        elif isinstance(data, list):
            return [self.mask_sensitive_data(item) for item in data]
        return data