import json
import logging
import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from customers.models import Customer
from customers.tests.factories import CustomerFactory

# Try to import pact libraries, but don't fail if not available
try:
    from pact import Verifier
    HAS_PACT = True
except (ImportError, ModuleNotFoundError):
    HAS_PACT = False

logger = logging.getLogger(__name__)

# Paths and configuration for PACT
PACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'pact')
PACT_FILE = os.path.join(PACT_DIR, 'pacts', 'react-app-customer-api.json')
PACT_BROKER_URL = os.environ.get('PACT_BROKER_URL', 'http://localhost:9292')
PROVIDER_NAME = 'customer-api'
PROVIDER_URL = os.environ.get('PROVIDER_URL', 'http://localhost:8000')


@pytest.mark.skipif(not HAS_PACT, reason="Pact library not available")
@pytest.mark.pact
class TestCustomerPactProvider:
    """Test the customer API as a PACT provider."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class."""
        # Set up API client
        cls.client = APIClient()
        # Authenticate the client (if needed)
        # cls.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        
    def setup_method(self, method):
        """Set up for each test method."""
        # Create test data
        self.customer = CustomerFactory(
            company_name="Test Company",
            legal_business_name="Test Legal Name",
            email="test@example.com",
            is_active=True
        )
        
    def teardown_method(self, method):
        """Clean up after each test method."""
        # Clean up test data
        Customer.objects.all().delete()
    
    def test_get_customer_list(self):
        """Test GET request to customer list endpoint."""
        # Set up test data
        customers = [CustomerFactory() for _ in range(5)]
        
        # Make the request
        url = reverse('customer-list')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        for customer in customers:
            # The list endpoint should include all customers
            assert any(item['id'] == str(customer.id) for item in response.data['results'])
    
    def test_get_customer_by_id(self):
        """Test GET request to customer detail endpoint."""
        # Make the request
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['id'] == str(self.customer.id)
        assert response.data['company_name'] == self.customer.company_name
        assert response.data['email'] == self.customer.email
    
    def test_create_customer(self):
        """Test POST request to create a customer."""
        # Prepare data for creating a new customer
        new_customer_data = {
            'company_name': 'New Test Company',
            'legal_business_name': 'New Test Legal Name',
            'email': 'newtest@example.com',
            'is_active': True
        }
        
        # Make the request
        url = reverse('customer-list')
        response = self.client.post(url, new_customer_data, format='json')
        
        # Verify the response
        assert response.status_code == 201
        assert response.data['company_name'] == new_customer_data['company_name']
        assert response.data['email'] == new_customer_data['email']
        
        # Verify the customer was created in the database
        assert Customer.objects.filter(email=new_customer_data['email']).exists()
    
    def test_update_customer(self):
        """Test PUT request to update a customer."""
        # Prepare data for updating the customer
        update_data = {
            'company_name': 'Updated Test Company',
            'legal_business_name': self.customer.legal_business_name,
            'email': self.customer.email,
            'is_active': self.customer.is_active
        }
        
        # Make the request
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.put(url, update_data, format='json')
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['company_name'] == update_data['company_name']
        
        # Verify the customer was updated in the database
        self.customer.refresh_from_db()
        assert self.customer.company_name == update_data['company_name']
    
    def test_patch_customer(self):
        """Test PATCH request to partially update a customer."""
        # Prepare data for partially updating the customer
        patch_data = {
            'company_name': 'Patched Test Company'
        }
        
        # Make the request
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.patch(url, patch_data, format='json')
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['company_name'] == patch_data['company_name']
        
        # Verify the customer was updated in the database
        self.customer.refresh_from_db()
        assert self.customer.company_name == patch_data['company_name']
    
    def test_delete_customer(self):
        """Test DELETE request to delete a customer."""
        # Make the request
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.delete(url)
        
        # Verify the response
        assert response.status_code == 204
        
        # Verify the customer was deleted from the database
        assert not Customer.objects.filter(id=self.customer.id).exists()
    
    @pytest.mark.skip(reason="Full PACT verification requires a running service")
    def test_verify_customer_pacts(self):
        """Verify all PACT contracts for the customer API."""
        # This test requires a running API service
        if not os.path.exists(PACT_FILE):
            pytest.skip(f"PACT file not found: {PACT_FILE}")
        
        # Use the Pact verifier to validate all contracts
        verifier = Verifier(
            provider="customer-api",
            provider_base_url=PROVIDER_URL
        )
        
        # Define provider states and set up the required state
        provider_states = {
            "a customer exists": self.setup_customer_exists,
            "multiple customers exist": self.setup_multiple_customers,
            "no customers exist": self.setup_no_customers
        }
        
        # Verify the PACT
        output, _ = verifier.verify_pacts(
            PACT_FILE,
            provider_states=provider_states,
            provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states"
        )
        
        assert output == 0, "PACT verification failed"
    
    def setup_customer_exists(self):
        """Set up the 'a customer exists' provider state."""
        # Create a test customer with predictable data
        return CustomerFactory(
            id=1,  # Use a fixed ID for predictable testing
            company_name="Test Company",
            legal_business_name="Test Legal Business Name",
            email="test@example.com",
            is_active=True
        )
    
    def setup_multiple_customers(self):
        """Set up the 'multiple customers exist' provider state."""
        # Create multiple test customers
        customers = []
        for i in range(5):
            customers.append(CustomerFactory(
                company_name=f"Test Company {i}",
                email=f"test{i}@example.com"
            ))
        return customers
    
    def setup_no_customers(self):
        """Set up the 'no customers exist' provider state."""
        # Delete all customers
        Customer.objects.all().delete()