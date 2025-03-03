"""
Test mixins and utilities for LedgerLink tests.
"""

import json
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

User = get_user_model()

def create_test_client(user=None):
    """
    Create a test client with optional authentication.
    
    Args:
        user: Optional user to authenticate the client with
        
    Returns:
        Django test client instance
    """
    client = Client()
    if user:
        client.force_login(user)
    return client


def create_api_client(user=None):
    """
    Create an API test client with optional authentication.
    
    Args:
        user: Optional user to authenticate the client with
        
    Returns:
        DRF API client instance
    """
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


class APITestMixin:
    """Mixin for API tests with common utilities."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
    
    def get_json_response(self, url, method='get', data=None, status_code=200, **kwargs):
        """
        Make a request to an API endpoint and return JSON response.
        
        Args:
            url: Endpoint URL
            method: HTTP method (get, post, put, patch, delete)
            data: Request data
            status_code: Expected status code
            **kwargs: Additional arguments for the request
            
        Returns:
            JSON response data
        """
        method_func = getattr(self.client, method.lower())
        kwargs_to_use = {'format': 'json'}
        kwargs_to_use.update(kwargs)
        
        if data and method.lower() != 'get':
            response = method_func(url, data, **kwargs_to_use)
        elif data and method.lower() == 'get':
            response = method_func(f"{url}?{self._dict_to_query_params(data)}", **kwargs_to_use)
        else:
            response = method_func(url, **kwargs_to_use)
        
        self.assertEqual(response.status_code, status_code, 
                         f"Expected {status_code}, got {response.status_code}. Response: {getattr(response, 'data', '')}")
        
        if response.get('content-type') == 'application/json':
            return response.json()
        return response
    
    def _dict_to_query_params(self, data_dict):
        """Convert dictionary to URL query parameters."""
        return '&'.join([f"{key}={value}" for key, value in data_dict.items()])


class ViewTestMixin:
    """Mixin for view tests with common utilities."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.force_login(self.user)
    
    def get_url(self, url_name, *args, **kwargs):
        """Get a URL by its name."""
        return reverse(url_name, args=args, kwargs=kwargs)
    
    def get_response(self, url, method='get', data=None, follow=False, **kwargs):
        """Make a request to a view and return the response."""
        method_func = getattr(self.client, method.lower())
        
        if data and method.lower() in ['post', 'put', 'patch']:
            response = method_func(url, data=data, follow=follow, **kwargs)
        else:
            response = method_func(url, follow=follow, **kwargs)
        
        return response