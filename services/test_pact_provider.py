"""
Service Provider Pact Tests for LedgerLink
"""
from django.urls import reverse
from pact_test import ProviderPactTest
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from .models import Service


class ServiceProviderTest(ProviderPactTest, APITestCase):
    """Provider pact tests for Service API"""
    
    provider_name = 'LedgerLinkAPI'
    consumer_name = 'LedgerLinkFrontend'
    pact_dir = 'pacts'
    
    @classmethod
    def setUpTestData(cls):
        # Create test user for authentication
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test services
        cls.service1 = Service.objects.create(
            id=1,  # Set ID explicitly for consistent testing
            service_name="Standard Shipping",
            description="Standard shipping service",
            charge_type="quantity"
        )
        
        cls.service2 = Service.objects.create(
            id=2,
            service_name="Express Shipping",
            description="Express shipping service",
            charge_type="single"
        )
    
    def setup_services_exist(self):
        """Provider state for when services exist"""
        # Data already created in setUpTestData
        return None
    
    def setup_service_with_id_1_exists(self):
        """Provider state for when a specific service exists"""
        # Data already created in setUpTestData
        return None
    
    def setup_can_create_service(self):
        """Provider state for when a service can be created"""
        # No specific setup needed
        return None
    
    def get_service_list(self, request, **kwargs):
        """Get services list endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.get(reverse('service-list'), **kwargs)
    
    def get_service_detail(self, request, **kwargs):
        """Get specific service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.get(
            reverse('service-detail', args=[kwargs.get('id', 1)]), 
            **kwargs
        )
    
    def post_service(self, request, **kwargs):
        """Create service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.post(
            reverse('service-list'),
            data=request.body,
            content_type='application/json',
            **kwargs
        )
    
    def put_service(self, request, **kwargs):
        """Update service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.put(
            reverse('service-detail', args=[kwargs.get('id', 1)]),
            data=request.body,
            content_type='application/json',
            **kwargs
        )
    
    def delete_service(self, request, **kwargs):
        """Delete service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.delete(
            reverse('service-detail', args=[kwargs.get('id', 1)]),
            **kwargs
        )
    
    def get_service_charge_types(self, request, **kwargs):
        """Get service charge types endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.get(reverse('service-charge-types'), **kwargs)
    
    def test_get_all_services(self):
        """Test that all services can be retrieved"""
        response = self.get_service_list({})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
    
    def test_get_specific_service(self):
        """Test that a specific service can be retrieved"""
        response = self.get_service_detail({}, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['service_name'], 'Standard Shipping')
    
    def test_create_service(self):
        """Test that a service can be created"""
        data = {
            'service_name': 'New Pact Service',
            'description': 'A service created by Pact test',
            'charge_type': 'quantity'
        }
        response = self.post_service({'body': data})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['service_name'], 'New Pact Service')
    
    def test_update_service(self):
        """Test that a service can be updated"""
        data = {
            'service_name': 'Updated Standard Shipping',
            'description': 'Updated by Pact test',
            'charge_type': 'quantity'
        }
        response = self.put_service({'body': data}, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['service_name'], 'Updated Standard Shipping')
    
    def test_get_charge_types(self):
        """Test getting all charge types"""
        response = self.get_service_charge_types({})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Should have at least 2 charge types
        self.assertGreaterEqual(len(response.data['data']), 2)