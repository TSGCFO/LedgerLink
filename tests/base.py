import json
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from api.tests.factories import UserFactory


class BaseTestCase(TestCase):
    """Base test case for standard Django view tests."""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.admin_user = UserFactory(is_staff=True, is_superuser=True)
        cls.regular_user = UserFactory()
    
    def login_as_admin(self):
        self.client.force_login(self.admin_user)
        
    def login_as_user(self):
        self.client.force_login(self.regular_user)


class BaseAPITestCase(APITestCase):
    """Base test case for API endpoint tests."""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.admin_user = UserFactory(is_staff=True, is_superuser=True)
        cls.regular_user = UserFactory()
    
    def login_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        
    def login_as_user(self):
        self.client.force_authenticate(user=self.regular_user)
    
    def api_get(self, url_name, kwargs=None, data=None):
        """
        Helper method to perform GET request.
        
        Args:
            url_name: The URL name to reverse
            kwargs: URL kwargs
            data: Query parameters
            
        Returns:
            Response object with parsed data
        """
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.get(url, data=data)
        return self._parse_response(response)
    
    def api_post(self, url_name, kwargs=None, data=None, format='json'):
        """
        Helper method to perform POST request.
        
        Args:
            url_name: The URL name to reverse
            kwargs: URL kwargs
            data: Request data
            format: Data format (json, multipart, etc.)
            
        Returns:
            Response object with parsed data
        """
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.post(url, data, format=format)
        return self._parse_response(response)
    
    def api_put(self, url_name, kwargs=None, data=None, format='json'):
        """
        Helper method to perform PUT request.
        
        Args:
            url_name: The URL name to reverse
            kwargs: URL kwargs
            data: Request data
            format: Data format (json, multipart, etc.)
            
        Returns:
            Response object with parsed data
        """
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.put(url, data, format=format)
        return self._parse_response(response)
    
    def api_patch(self, url_name, kwargs=None, data=None, format='json'):
        """
        Helper method to perform PATCH request.
        
        Args:
            url_name: The URL name to reverse
            kwargs: URL kwargs
            data: Request data
            format: Data format (json, multipart, etc.)
            
        Returns:
            Response object with parsed data
        """
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.patch(url, data, format=format)
        return self._parse_response(response)
    
    def api_delete(self, url_name, kwargs=None):
        """
        Helper method to perform DELETE request.
        
        Args:
            url_name: The URL name to reverse
            kwargs: URL kwargs
            
        Returns:
            Response object
        """
        url = reverse(url_name, kwargs=kwargs)
        return self.client.delete(url)
    
    def _parse_response(self, response):
        """
        Parse JSON response data if possible.
        
        Args:
            response: Response object
            
        Returns:
            Response object with parsed data if JSON
        """
        if response.get('content-type') == 'application/json':
            try:
                response.data = json.loads(response.content)
            except:
                pass
        return response