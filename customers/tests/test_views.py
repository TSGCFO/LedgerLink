import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from customers.tests.factories import CustomerFactory

User = get_user_model()


@pytest.mark.integration
class CustomerViewTests(APITestCase):
    """Test suite for the Customer views."""
    
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        cls.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword'
        )
        
        # Create test customers
        cls.customers = [CustomerFactory() for _ in range(3)]
        cls.customer = cls.customers[0]
    
    def setUp(self):
        # Clear any authentication before each test
        self.client.force_authenticate(user=None)
    
    def test_list_customers_authenticated(self):
        """Test listing customers when authenticated."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])  # Check for success flag in response
        self.assertIn('data', response.data)  # Check for data key in response
        
        # The response structure now has a data array
        customer_data = response.data['data']
        self.assertEqual(len(customer_data), len(self.customers))
    
    def test_list_customers_unauthenticated(self):
        """Test listing customers when unauthenticated."""
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_customer_authenticated(self):
        """Test retrieving a single customer when authenticated."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.customer.id))
        self.assertEqual(response.data['company_name'], self.customer.company_name)
    
    def test_retrieve_customer_unauthenticated(self):
        """Test retrieving a single customer when unauthenticated."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_customer_authenticated(self):
        """Test creating a customer when authenticated."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-list')
        
        new_customer_data = {
            'company_name': 'New Test Company',
            'legal_business_name': 'New Test Legal Business LLC',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',  # Use zip instead of zip_code to match model
            'country': 'US',
            'business_type': 'Retail',
            'is_active': True
        }
        
        response = self.client.post(url, new_customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])  # Check for success flag
        self.assertIn('data', response.data)  # Check for data key in response
        self.assertEqual(response.data['data']['company_name'], new_customer_data['company_name'])
        
        # Verify the customer was created in the database
        new_customer_id = response.data['data']['id']
        self.assertTrue(Customer.objects.filter(id=new_customer_id).exists())
    
    def test_create_customer_unauthenticated(self):
        """Test creating a customer when unauthenticated."""
        url = reverse('customer-list')
        
        new_customer_data = {
            'company_name': 'New Test Company',
            'legal_business_name': 'New Test Legal Business LLC',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',
            'country': 'US',
            'business_type': 'Retail',
            'is_active': True
        }
        
        response = self.client.post(url, new_customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Customer.objects.count(), len(self.customers))
    
    def test_update_customer_authenticated(self):
        """Test updating a customer when authenticated."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        
        update_data = {
            'company_name': 'Updated Company Name'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['company_name'], update_data['company_name'])
        
        # Refresh from database
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.company_name, update_data['company_name'])
    
    def test_update_customer_unauthenticated(self):
        """Test updating a customer when unauthenticated."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        
        update_data = {
            'company_name': 'Updated Company Name'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Refresh from database
        self.customer.refresh_from_db()
        self.assertNotEqual(self.customer.company_name, update_data['company_name'])
    
    def test_delete_customer_authenticated(self):
        """Test deleting a customer when authenticated."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        
        response = self.client.delete(url)
        
        # API returns 200 OK with success message instead of 204
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('message', response.data)
        
        # Verify the customer was deleted
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())
    
    def test_delete_customer_unauthenticated(self):
        """Test deleting a customer when unauthenticated."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Customer.objects.count(), len(self.customers))
    
    def test_filter_customers_by_active_status(self):
        """Test filtering customers by active status."""
        # Create additional customers with specific active status
        CustomerFactory(is_active=True)
        CustomerFactory(is_active=False)
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-list')
        
        # Filter for active customers
        response = self.client.get(f"{url}?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Count active customers directly from DB to verify
        active_count = Customer.objects.filter(is_active=True).count()
        self.assertEqual(len(response.data['data']), active_count)
        
        # Filter for inactive customers
        response = self.client.get(f"{url}?is_active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Count inactive customers directly from DB to verify
        inactive_count = Customer.objects.filter(is_active=False).count()
        self.assertEqual(len(response.data['data']), inactive_count)
    
    def test_search_customers_by_company_name(self):
        """Test searching customers by company name."""
        # Create customers with specific company names
        CustomerFactory(company_name="Acme Corporation")
        CustomerFactory(company_name="Acme Services")
        CustomerFactory(company_name="Other Company")
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-list')
        
        # Search for "Acme"
        response = self.client.get(f"{url}?search=Acme")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should find the two Acme companies
        search_results = response.data['data']
        self.assertEqual(len(search_results), 2)
        
        # Verify the correct companies were found
        company_names = [result['company_name'] for result in search_results]
        self.assertIn("Acme Corporation", company_names)
        self.assertIn("Acme Services", company_names)
        self.assertNotIn("Other Company", company_names)
    
    def test_stats_endpoint(self):
        """Test the stats endpoint returns correct customer statistics."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('customer-stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('total_customers', response.data['data'])
        
        # Verify the correct count is returned
        self.assertEqual(response.data['data']['total_customers'], Customer.objects.count())