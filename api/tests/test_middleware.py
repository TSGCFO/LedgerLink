from django.test import TestCase, RequestFactory
from django.http import JsonResponse
import json
import re
from unittest.mock import patch, MagicMock

from api.middleware import APILoggingMiddleware, get_client_ip


class MockResponse:
    """Mock response object for testing middleware"""
    def __init__(self, content, status_code=200, content_type='application/json'):
        self.content = content
        self.status_code = status_code
        self._headers = {'Content-Type': content_type}
    
    def get(self, key, default=None):
        return self._headers.get(key, default)


class APILoggingMiddlewareTests(TestCase):
    """Test cases for the APILoggingMiddleware class"""
    
    def setUp(self):
        """Set up test data and mock objects"""
        self.factory = RequestFactory()
        self.get_response_mock = MagicMock(return_value=MockResponse(
            json.dumps({"success": True}).encode(),
            200
        ))
        self.middleware = APILoggingMiddleware(self.get_response_mock)
        
        # Create sample requests
        self.api_get_request = self.factory.get('/api/v1/customers/')
        self.api_post_request = self.factory.post(
            '/api/v1/customers/',
            data=json.dumps({"company_name": "Test Company", "email": "test@example.com"}),
            content_type='application/json'
        )
        self.api_post_sensitive_request = self.factory.post(
            '/api/v1/auth/login/',
            data=json.dumps({"username": "testuser", "password": "secretpassword"}),
            content_type='application/json'
        )
        self.non_api_request = self.factory.get('/customers/')
        
        # Setup for authenticated user
        self.api_get_request.user = MagicMock()
        self.api_get_request.user.is_authenticated = True
        self.api_get_request.user.__str__ = lambda self: "testuser"
        
        # Setup for unauthenticated user
        self.api_post_request.user = MagicMock()
        self.api_post_request.user.is_authenticated = False
        
        # Setup special headers
        self.forwarded_request = self.factory.get('/api/v1/customers/')
        self.forwarded_request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        self.forwarded_request.user = self.api_get_request.user
    
    @patch('api.middleware.logger')
    def test_non_api_requests_bypass_middleware(self, mock_logger):
        """Test that non-API requests bypass the middleware logging"""
        self.middleware(self.non_api_request)
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()
    
    @patch('api.middleware.logger')
    def test_log_api_get_request(self, mock_logger):
        """Test logging of API GET requests"""
        self.middleware(self.api_get_request)
        
        # Should log the request
        mock_logger.info.assert_any_call(
            "GET /api/v1/customers/",
            extra={'request_data': self._get_expected_request_data(self.api_get_request)}
        )
        
        # Should log the response
        call_args_list = mock_logger.info.call_args_list
        response_log_call = call_args_list[1]  # Second call should be the response log
        self.assertEqual(response_log_call[0][0], "Success response for GET /api/v1/customers/")
        
        # Check that response data contains expected fields
        response_data = response_log_call[1]['extra']['response_data']
        self.assertEqual(response_data['method'], 'GET')
        self.assertEqual(response_data['path'], '/api/v1/customers/')
        self.assertEqual(response_data['status_code'], 200)
        self.assertIn('duration', response_data)
        self.assertIn('content_length', response_data)
    
    @patch('api.middleware.logger')
    def test_log_api_post_request_with_json_body(self, mock_logger):
        """Test logging of API POST requests with JSON body"""
        self.middleware(self.api_post_request)
        
        # Should log the request with body
        call_args_list = mock_logger.info.call_args_list
        request_log_call = call_args_list[0]
        request_data = request_log_call[1]['extra']['request_data']
        
        self.assertEqual(request_data['method'], 'POST')
        self.assertEqual(request_data['path'], '/api/v1/customers/')
        self.assertEqual(request_data['body'], {
            "company_name": "Test Company", 
            "email": "test@example.com"
        })
    
    @patch('api.middleware.logger')
    def test_mask_sensitive_data(self, mock_logger):
        """Test masking of sensitive data in requests and responses"""
        self.middleware(self.api_post_sensitive_request)
        
        # Check request logging
        call_args_list = mock_logger.info.call_args_list
        request_log_call = call_args_list[0]
        request_data = request_log_call[1]['extra']['request_data']
        
        # Password should be masked
        self.assertEqual(request_data['body']['username'], 'testuser')
        self.assertEqual(request_data['body']['password'], '********')
    
    def test_is_sensitive_value(self):
        """Test the is_sensitive_value method"""
        # Should detect passwords and tokens
        self.assertTrue(self.middleware.is_sensitive_value('secretpassword', 'password'))
        self.assertTrue(self.middleware.is_sensitive_value('api_key_123456789', 'api_key'))
        
        # Should detect values that look like JWT tokens
        self.assertTrue(self.middleware.is_sensitive_value('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'))
        
        # Should not flag regular values
        self.assertFalse(self.middleware.is_sensitive_value('regular string'))
        self.assertFalse(self.middleware.is_sensitive_value('123456'))
    
    def test_mask_sensitive_data(self):
        """Test the mask_sensitive_data method"""
        # Test dictionary with sensitive keys
        data = {
            'username': 'testuser',
            'password': 'secretpassword',
            'email': 'test@example.com',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0',
            'nested': {
                'api_key': 'secretapikey123456',
                'name': 'Test Name'
            },
            'items': [
                {'id': 1, 'secret': 'hidden1'},
                {'id': 2, 'secret': 'hidden2'}
            ]
        }
        
        masked_data = self.middleware.mask_sensitive_data(data)
        
        # Check that sensitive fields are masked
        self.assertEqual(masked_data['username'], 'testuser')  # Should not be masked
        self.assertEqual(masked_data['password'], '********')  # Should be masked
        self.assertEqual(masked_data['email'], 'test@example.com')  # Should not be masked
        self.assertEqual(masked_data['token'], '********')  # Should be masked
        
        # Check nested dictionary
        self.assertEqual(masked_data['nested']['api_key'], '********')  # Should be masked
        self.assertEqual(masked_data['nested']['name'], 'Test Name')  # Should not be masked
        
        # Check list of dictionaries
        self.assertEqual(masked_data['items'][0]['id'], 1)  # Should not be masked
        self.assertEqual(masked_data['items'][0]['secret'], '********')  # Should be masked
        self.assertEqual(masked_data['items'][1]['secret'], '********')  # Should be masked
    
    def test_get_client_ip(self):
        """Test the get_client_ip function"""
        # Test with X-Forwarded-For header
        ip = get_client_ip(self.forwarded_request)
        self.assertEqual(ip, '192.168.1.1')
        
        # Test without X-Forwarded-For header
        ip = get_client_ip(self.api_get_request)
        self.assertEqual(ip, self.api_get_request.META.get('REMOTE_ADDR'))
    
    @patch('api.middleware.logger')
    def test_log_error_response(self, mock_logger):
        """Test logging of error responses"""
        # Create error response
        self.get_response_mock.return_value = MockResponse(
            json.dumps({"error": "Not found"}).encode(),
            404
        )
        
        self.middleware(self.api_get_request)
        
        # Should log the response as a warning
        call_args_list = mock_logger.warning.call_args_list
        response_log_call = call_args_list[0]
        self.assertEqual(response_log_call[0][0], "Error response for GET /api/v1/customers/")
        
        # Check that response data contains expected fields
        response_data = response_log_call[1]['extra']['response_data']
        self.assertEqual(response_data['status_code'], 404)
    
    @patch('api.middleware.logger')
    def test_handle_non_json_response(self, mock_logger):
        """Test handling of non-JSON responses"""
        # Create non-JSON response
        self.get_response_mock.return_value = MockResponse(
            b"Plain text response",
            200,
            content_type='text/plain'
        )
        
        self.middleware(self.api_get_request)
        
        # Should still log the response
        call_args_list = mock_logger.info.call_args_list
        response_log_call = call_args_list[1]  # Second call should be the response log
        
        # Body should be None for non-JSON responses
        response_data = response_log_call[1]['extra']['response_data']
        self.assertIsNone(response_data['body'])
    
    @patch('api.middleware.logger')
    def test_exception_handling_in_request_logging(self, mock_logger):
        """Test exception handling during request logging"""
        # Setup to cause exception during request logging
        with patch.object(self.middleware, 'log_request', side_effect=Exception('Test exception')):
            self.middleware(self.api_get_request)
            
            # Should log the error and continue
            mock_logger.error.assert_called_with('Error logging request: Test exception')
            
            # Should still call get_response and log response
            self.get_response_mock.assert_called_once()
    
    @patch('api.middleware.logger')
    def test_exception_handling_in_response_logging(self, mock_logger):
        """Test exception handling during response logging"""
        # Setup to cause exception during response logging
        with patch.object(self.middleware, 'log_response', side_effect=Exception('Test exception')):
            self.middleware(self.api_get_request)
            
            # Should log the error
            mock_logger.error.assert_called_with('Error logging response: Test exception')
            
            # Should still return the response
            self.assertEqual(self.middleware(self.api_get_request).status_code, 200)
    
    def _get_expected_request_data(self, request):
        """Helper to get expected request data for a request"""
        return {
            'method': request.method,
            'path': request.path,
            'query_params': request.GET.dict(),
            'body': None,
            'headers': dict(request.headers),
            'user': 'testuser' if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            'ip': get_client_ip(request)
        }