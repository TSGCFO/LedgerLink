from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import logging
import json
from unittest.mock import patch, MagicMock

from api.middleware import APILoggingMiddleware


class APILoggingMiddlewareIntegrationTests(TestCase):
    """Integration tests for APILoggingMiddleware with actual API requests"""
    
    def setUp(self):
        """Set up test data and authenticated client"""
        # Create test user
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        
        # Setup API client
        self.client = APIClient()
        
        # Create urls for testing
        self.api_url = reverse('api-root')
        self.non_api_url = reverse('admin:index')
        
        # Use obtain token url if it exists
        try:
            self.token_url = reverse('token_obtain_pair')
        except:
            self.token_url = '/api/v1/auth/token/'
    
    @patch('api.middleware.logger')
    def test_api_request_logging(self, mock_logger):
        """Test that API requests are logged"""
        # Make an API request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.api_url)
        
        # Verify request was logged
        mock_logger.info.assert_called()
        
        # At least one call should contain the API path
        any_api_path_call = False
        for call in mock_logger.info.call_args_list:
            args, kwargs = call
            if args and self.api_url in args[0]:
                any_api_path_call = True
                break
        
        self.assertTrue(any_api_path_call, "API path should be in log messages")
    
    @patch('api.middleware.logger')
    def test_non_api_request_not_logged(self, mock_logger):
        """Test that non-API requests are not logged"""
        # Make a non-API request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.non_api_url)
        
        # No log should contain the non-API path
        any_non_api_path_call = False
        for call in mock_logger.info.call_args_list:
            args, kwargs = call
            if args and self.non_api_url in args[0]:
                any_non_api_path_call = True
                break
        
        self.assertFalse(any_non_api_path_call, "Non-API path should not be in log messages")
    
    @patch('api.middleware.logger')
    def test_sensitive_data_masked(self, mock_logger):
        """Test that sensitive data in requests is masked"""
        # Make a login request with sensitive data
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(
            self.token_url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Check that the password was masked in the logs
        password_was_masked = False
        for call in mock_logger.info.call_args_list:
            args, kwargs = call
            if 'extra' in kwargs and 'request_data' in kwargs['extra']:
                request_data = kwargs['extra']['request_data']
                if 'body' in request_data and isinstance(request_data['body'], dict):
                    # Password should be masked
                    if 'password' in request_data['body'] and request_data['body']['password'] == '********':
                        password_was_masked = True
                        break
        
        self.assertTrue(password_was_masked, "Password should be masked in logs")
    
    @patch('api.middleware.logger')
    def test_error_response_logged_as_warning(self, mock_logger):
        """Test that error responses are logged as warnings"""
        # Make a request that will result in 404
        non_existent_url = '/api/v1/non-existent-endpoint/'
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # The error response should be logged as a warning
        mock_logger.warning.assert_called()
        
        error_was_logged = False
        for call in mock_logger.warning.call_args_list:
            args, kwargs = call
            if 'Error response for' in args[0] and 'non-existent-endpoint' in args[0]:
                error_was_logged = True
                break
        
        self.assertTrue(error_was_logged, "Error response should be logged as warning")
    
    @override_settings(MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'api.middleware.APILoggingMiddleware',  # Add the middleware for this test
    ])
    @patch('api.middleware.logger')
    def test_middleware_in_settings(self, mock_logger):
        """Test that the middleware works when configured in settings"""
        # Make an API request
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.api_url)
        
        # Verify request was logged
        mock_logger.info.assert_called()
    
    @patch('logging.Logger.error')
    def test_middleware_exception_handling(self, mock_error):
        """Test that middleware exceptions don't crash the request"""
        # Create a middleware that will raise an exception
        middleware = APILoggingMiddleware(get_response=lambda request: MagicMock())
        
        # Mock the log_request method to raise an exception
        original_log_request = middleware.log_request
        middleware.log_request = MagicMock(side_effect=Exception("Test exception"))
        
        # Create a test request
        request = self.client.get(self.api_url).wsgi_request
        request.path = '/api/v1/test/'
        
        # Call the middleware - should not raise an exception
        try:
            response = middleware(request)
            exception_handled = True
        except:
            exception_handled = False
        
        self.assertTrue(exception_handled, "Middleware should handle exceptions gracefully")
        
        # Restore the original method
        middleware.log_request = original_log_request