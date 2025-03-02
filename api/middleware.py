"""
API Logging Middleware
"""

import json
import logging
import time
import re
from django.conf import settings

logger = logging.getLogger('api')

def get_client_ip(request):
    """Get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

class APILoggingMiddleware:
    """Middleware to log API requests and responses"""

    def __init__(self, get_response):
        self.get_response = get_response
        
        # Precompile regex patterns for better performance
        self.jwt_pattern = re.compile(r'^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$')
        self.api_key_pattern = re.compile(r'^[A-Za-z0-9]{20,}$')
        self.base64_pattern = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')
        
        # List of sensitive keywords to check
        self.sensitive_keywords = [
            'password', 'token', 'secret', 'key', 'auth', 'credential', 
            'private', 'api_key', 'apikey', 'access_key', 'access_token'
        ]

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
            if body and any(key in str(body).lower() for key in self.sensitive_keywords):
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
                    if any(key in str(body).lower() for key in self.sensitive_keywords):
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
        return get_client_ip(request)

    def is_sensitive_value(self, value, key=None):
        """
        Check if a value contains sensitive information
        """
        if not isinstance(value, str):
            return False
        
        # Check if key contains sensitive keywords
        if key and any(keyword in key.lower() for keyword in self.sensitive_keywords):
            return True
        
        # Check if the value looks like a token/key (long alphanumeric with special chars)
        if len(value) > 8 and any(c.isalpha() for c in value) and any(c.isdigit() for c in value):
            # Check if the value matches common token/key patterns
            if (self.jwt_pattern.match(value) or 
                self.api_key_pattern.match(value) or 
                self.base64_pattern.match(value)):
                return True
        
        return False

    def mask_sensitive_data(self, data):
        """
        Recursively mask sensitive information in all nested structures
        """
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_keywords):
                    # Mask values with sensitive keys
                    masked_data[key] = '********'
                elif isinstance(value, (dict, list)):
                    # Recursively process nested structures
                    masked_data[key] = self.mask_sensitive_data(value)
                elif self.is_sensitive_value(value, key):
                    # Mask sensitive values
                    masked_data[key] = '********'
                else:
                    masked_data[key] = value
            return masked_data
            
        elif isinstance(data, list):
            # Process each item in the list
            return [self.mask_sensitive_data(item) for item in data]
            
        elif isinstance(data, str) and self.is_sensitive_value(data):
            # Mask sensitive strings
            return '********'
            
        return data