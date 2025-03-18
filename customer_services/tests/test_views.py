# customer_services/tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
import json

from django.contrib.auth.models import User
from customer_services.models import CustomerService
from customer_services.serializers import CustomerServiceSerializer
from customer_services.tests.factories import CustomerServiceFactory
from customers.tests.factories import CustomerFactory
from services.tests.factories import ServiceFactory
from products.tests.factories import ProductFactory

class CustomerServiceViewSetTest(TestCase):
    """Test case for the CustomerServiceViewSet."""
    
    def setUp(self):
        """Set up test data."""
        # Create user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create customers
        self.customer1 = CustomerFactory(company_name="Test Company 1")
        self.customer2 = CustomerFactory(company_name="Test Company 2")
        
        # Create services
        self.service1 = ServiceFactory(service_name="Test Service 1")
        self.service2 = ServiceFactory(service_name="Test Service 2")
        
        # Create customer services
        self.customer_service1 = CustomerServiceFactory(
            customer=self.customer1,
            service=self.service1,
            unit_price=Decimal('99.99')
        )
        self.customer_service2 = CustomerServiceFactory(
            customer=self.customer1,
            service=self.service2,
            unit_price=Decimal('149.99')
        )
        self.customer_service3 = CustomerServiceFactory(
            customer=self.customer2,
            service=self.service1,
            unit_price=Decimal('89.99')
        )
        
        # Create products (SKUs)
        self.product1 = ProductFactory(customer=self.customer1, sku="SKU-001")
        self.product2 = ProductFactory(customer=self.customer1, sku="SKU-002")
        self.product3 = ProductFactory(customer=self.customer2, sku="SKU-003")
        
        # Add SKUs to customer services
        self.customer_service1.skus.add(self.product1)
        self.customer_service2.skus.add(self.product1, self.product2)
        self.customer_service3.skus.add(self.product3)
        
        # Setup URLs for testing API endpoints
        self.list_url = reverse('customerservice-list')
        self.detail_url_cs1 = reverse('customerservice-detail', args=[self.customer_service1.id])
        self.detail_url_cs2 = reverse('customerservice-detail', args=[self.customer_service2.id])
        self.add_skus_url_cs1 = reverse('customerservice-add-skus', args=[self.customer_service1.id])
        self.remove_skus_url_cs1 = reverse('customerservice-remove-skus', args=[self.customer_service1.id])
    
    def test_list_customer_services(self):
        """Test listing all customer services."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 3)
    
    def test_filter_by_customer(self):
        """Test filtering customer services by customer."""
        response = self.client.get(f"{self.list_url}?customer={self.customer1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 2)
        
        # Check that all returned customer services belong to customer1
        for cs in response.data['data']:
            self.assertEqual(cs['customer'], self.customer1.id)
    
    def test_filter_by_service(self):
        """Test filtering customer services by service."""
        response = self.client.get(f"{self.list_url}?service={self.service1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 2)
        
        # Check that all returned customer services use service1
        for cs in response.data['data']:
            self.assertEqual(cs['service'], self.service1.id)
    
    def test_search_by_name(self):
        """Test searching customer services by customer or service name."""
        # Search by partial customer name
        response = self.client.get(f"{self.list_url}?search=Company 1")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 2)
        
        # Search by partial service name
        response = self.client.get(f"{self.list_url}?search=Service 2")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['service'], self.service2.id)
    
    def test_retrieve_customer_service(self):
        """Test retrieving a single customer service."""
        response = self.client.get(self.detail_url_cs1)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.customer_service1.id)
        self.assertEqual(response.data['customer'], self.customer1.id)
        self.assertEqual(response.data['service'], self.service1.id)
        self.assertEqual(response.data['unit_price'], '99.99')
        
        # Check nested data
        self.assertEqual(response.data['customer_details']['id'], self.customer1.id)
        self.assertEqual(response.data['service_details']['id'], self.service1.id)
        
        # Check SKU list
        self.assertEqual(len(response.data['sku_list']), 1)
        self.assertIn(self.product1.sku, response.data['sku_list'])
    
    def test_create_customer_service(self):
        """Test creating a new customer service."""
        data = {
            'customer': self.customer2.id,
            'service': self.service2.id,
            'unit_price': '129.99'
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['customer'], self.customer2.id)
        self.assertEqual(response.data['data']['service'], self.service2.id)
        self.assertEqual(response.data['data']['unit_price'], '129.99')
        
        # Check that the customer service was created in the database
        self.assertTrue(
            CustomerService.objects.filter(
                customer=self.customer2,
                service=self.service2,
                unit_price=Decimal('129.99')
            ).exists()
        )
    
    def test_create_duplicate_customer_service(self):
        """Test that creating a duplicate customer service fails."""
        data = {
            'customer': self.customer1.id,
            'service': self.service1.id,
            'unit_price': '129.99'
        }
        
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_customer_service(self):
        """Test updating a customer service."""
        data = {
            'customer': self.customer1.id,
            'service': self.service1.id,
            'unit_price': '119.99'
        }
        
        response = self.client.put(
            self.detail_url_cs1,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['unit_price'], '119.99')
        
        # Check that the customer service was updated in the database
        self.customer_service1.refresh_from_db()
        self.assertEqual(self.customer_service1.unit_price, Decimal('119.99'))
    
    def test_delete_customer_service(self):
        """Test deleting a customer service."""
        response = self.client.delete(self.detail_url_cs1)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Check that the customer service was deleted from the database
        self.assertFalse(
            CustomerService.objects.filter(id=self.customer_service1.id).exists()
        )
    
    def test_add_skus_action(self):
        """Test adding SKUs to a customer service."""
        # First, check that customer_service1 has only one SKU
        self.assertEqual(self.customer_service1.skus.count(), 1)
        
        # Prepare data for adding SKUs
        data = {
            'sku_ids': [self.product2.sku]
        }
        
        response = self.client.post(
            self.add_skus_url_cs1,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Check that the SKU was added
        self.customer_service1.refresh_from_db()
        self.assertEqual(self.customer_service1.skus.count(), 2)
        self.assertIn(self.product2, self.customer_service1.skus.all())
    
    def test_add_invalid_skus_action(self):
        """Test adding invalid SKUs to a customer service."""
        # Prepare data with a SKU that doesn't belong to the customer
        data = {
            'sku_ids': [self.product3.sku]  # product3 belongs to customer2, not customer1
        }
        
        response = self.client.post(
            self.add_skus_url_cs1,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        
        # Check that the SKU was not added
        self.customer_service1.refresh_from_db()
        self.assertEqual(self.customer_service1.skus.count(), 1)
        self.assertNotIn(self.product3, self.customer_service1.skus.all())
    
    def test_remove_skus_action(self):
        """Test removing SKUs from a customer service."""
        # First, check that customer_service2 has two SKUs
        self.assertEqual(self.customer_service2.skus.count(), 2)
        
        # Prepare data for removing a SKU
        data = {
            'sku_ids': [self.product1.id]
        }
        
        response = self.client.post(
            reverse('customerservice-remove-skus', args=[self.customer_service2.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Check that the SKU was removed
        self.customer_service2.refresh_from_db()
        self.assertEqual(self.customer_service2.skus.count(), 1)
        self.assertNotIn(self.product1, self.customer_service2.skus.all())
        self.assertIn(self.product2, self.customer_service2.skus.all())