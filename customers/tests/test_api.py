import pytest
from django.urls import reverse
from rest_framework import status

from tests.base import BaseAPITestCase
from customers.tests.factories import CustomerFactory
from customers.models import Customer
from customers.serializers import CustomerSerializer


@pytest.mark.api
class CustomerAPITests(BaseAPITestCase):
    """Test suite for Customer API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.customer = CustomerFactory()
        cls.customer_list_url = reverse('customer-list')
        cls.customer_detail_url = reverse('customer-detail', kwargs={'pk': cls.customer.pk})
    
    def test_list_customers(self):
        """Test listing customers."""
        # Create additional customers
        CustomerFactory.create_batch(5)
        
        self.login_as_admin()
        response = self.client.get(self.customer_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Customer.objects.count())
    
    def test_create_customer(self):
        """Test creating a new customer."""
        self.login_as_admin()
        
        customer_data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Testville',
            'state': 'TS',
            'zip_code': '12345',
            'country': 'US',
            'is_active': True
        }
        
        response = self.client.post(self.customer_list_url, customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)  # Original + newly created
        self.assertEqual(response.data['company_name'], customer_data['company_name'])
    
    def test_retrieve_customer(self):
        """Test retrieving a customer by ID."""
        self.login_as_admin()
        
        response = self.client.get(self.customer_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.customer.id))
    
    def test_update_customer(self):
        """Test updating a customer."""
        self.login_as_admin()
        
        updated_data = {
            'company_name': 'Updated Company Name',
            'contact_name': self.customer.contact_name,
            'email': self.customer.email,
            'phone': self.customer.phone,
            'address': self.customer.address,
            'city': self.customer.city,
            'state': self.customer.state,
            'zip_code': self.customer.zip_code,
            'country': self.customer.country,
            'is_active': self.customer.is_active
        }
        
        response = self.client.put(self.customer_detail_url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.company_name, updated_data['company_name'])
    
    def test_delete_customer(self):
        """Test deleting a customer."""
        self.login_as_admin()
        
        response = self.client.delete(self.customer_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.filter(id=self.customer.id).count(), 0)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to customer endpoints."""
        # Unauthenticated access
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Regular user access (assuming admin-only permission)
        self.login_as_user()
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)