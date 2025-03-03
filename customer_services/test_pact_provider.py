"""
CustomerService Provider Pact Tests for LedgerLink
"""
from django.urls import reverse
from pact_test import ProviderPactTest
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from django.contrib.auth.models import User

from .models import CustomerService
from customers.models import Customer
from services.models import Service


class CustomerServiceProviderTest(ProviderPactTest, APITestCase):
    """Provider pact tests for CustomerService API"""
    
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
        
        # Create test data
        cls.customer1 = Customer.objects.create(
            company_name="Pact Test Company 1",
            legal_business_name="Pact Test Company 1 LLC",
            email="pact1@example.com",
            phone="555-1111",
            address="111 Pact St",
            city="Test City",
            state="TS",
            zip_code="11111",
            country="US"
        )
        
        cls.customer2 = Customer.objects.create(
            company_name="Pact Test Company 2",
            legal_business_name="Pact Test Company 2 LLC",
            email="pact2@example.com",
            phone="555-2222",
            address="222 Pact Ave",
            city="Test City",
            state="TS",
            zip_code="22222",
            country="US"
        )
        
        cls.service1 = Service.objects.create(
            service_name="Pact Standard Service",
            description="Standard service for pact testing",
            base_rate=Decimal('50.00'),
            charge_type="flat_rate"
        )
        
        cls.service2 = Service.objects.create(
            service_name="Pact Premium Service",
            description="Premium service for pact testing",
            base_rate=Decimal('100.00'),
            charge_type="flat_rate"
        )
        
        # Create customer services
        cls.customer_service1 = CustomerService.objects.create(
            id=1,  # Set ID explicitly for consistent testing
            customer=cls.customer1,
            service=cls.service1,
            unit_price=Decimal('45.00')
        )
        
        cls.customer_service2 = CustomerService.objects.create(
            id=2,
            customer=cls.customer1,
            service=cls.service2,
            unit_price=Decimal('95.00')
        )
        
        cls.customer_service3 = CustomerService.objects.create(
            id=3,
            customer=cls.customer2,
            service=cls.service1,
            unit_price=Decimal('48.00')
        )
    
    def setup_customer_services_exist(self):
        """Provider state for when customer services exist"""
        # Data already created in setUpTestData
        return None
    
    def setup_customer_service_with_id_1_exists(self):
        """Provider state for when a specific customer service exists"""
        # Data already created in setUpTestData
        return None
    
    def setup_can_create_customer_service(self):
        """Provider state for when a customer service can be created"""
        # No specific setup needed
        return None
    
    def setup_can_filter_by_customer(self):
        """Provider state for filtering by customer"""
        # Data already created in setUpTestData
        return None
    
    def setup_can_filter_by_service(self):
        """Provider state for filtering by service"""
        # Data already created in setUpTestData
        return None
    
    def get_customerservice_list(self, request, **kwargs):
        """Get customer services list endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.get(reverse('customerservice-list'), **kwargs)
    
    def get_customerservice_detail(self, request, **kwargs):
        """Get specific customer service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.get(
            reverse('customerservice-detail', args=[kwargs.get('id', 1)]), 
            **kwargs
        )
    
    def post_customerservice(self, request, **kwargs):
        """Create customer service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.post(
            reverse('customerservice-list'),
            data=request.body,
            content_type='application/json',
            **kwargs
        )
    
    def put_customerservice(self, request, **kwargs):
        """Update customer service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.put(
            reverse('customerservice-detail', args=[kwargs.get('id', 1)]),
            data=request.body,
            content_type='application/json',
            **kwargs
        )
    
    def delete_customerservice(self, request, **kwargs):
        """Delete customer service endpoint for pact testing"""
        self.client.force_authenticate(user=self.user)
        return self.client.delete(
            reverse('customerservice-detail', args=[kwargs.get('id', 1)]),
            **kwargs
        )
    
    def test_get_all_customer_services(self):
        """Test that all customer services can be retrieved"""
        response = self.get_customerservice_list({})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
    
    def test_get_specific_customer_service(self):
        """Test that a specific customer service can be retrieved"""
        response = self.get_customerservice_detail({}, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['customer'], self.customer1.id)
        self.assertEqual(response.data['service'], self.service1.id)
    
    def test_create_customer_service(self):
        """Test that a customer service can be created"""
        data = {
            'customer': self.customer2.id,
            'service': self.service2.id,
            'unit_price': '90.00'
        }
        response = self.post_customerservice({'body': data})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['customer'], self.customer2.id)
        self.assertEqual(response.data['data']['service'], self.service2.id)
    
    def test_update_customer_service(self):
        """Test that a customer service can be updated"""
        data = {
            'customer': self.customer1.id,
            'service': self.service1.id,
            'unit_price': '55.00'
        }
        response = self.put_customerservice({'body': data}, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['unit_price'], '55.00')
    
    def test_delete_customer_service(self):
        """Test that a customer service can be deleted"""
        response = self.delete_customerservice({}, id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])