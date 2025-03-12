import json
import logging
import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Product
from products.tests.factories import ProductFactory, CustomerFactory

# Try to import pact libraries, but don't fail if not available
try:
    from pact import Verifier
    HAS_PACT = True
except (ImportError, ModuleNotFoundError):
    HAS_PACT = False

logger = logging.getLogger(__name__)

# Paths and configuration for PACT
PACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'pact')
PACT_FILE = os.path.join(PACT_DIR, 'pacts', 'react-app-product-api.json')
PACT_BROKER_URL = os.environ.get('PACT_BROKER_URL', 'http://localhost:9292')
PROVIDER_NAME = 'product-api'
PROVIDER_URL = os.environ.get('PROVIDER_URL', 'http://localhost:8000')


@pytest.mark.skipif(not HAS_PACT, reason="Pact library not available")
@pytest.mark.pact
class TestProductPactProvider:
    """Test the product API as a PACT provider."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class."""
        # Set up API client
        cls.client = APIClient()
        # Authenticate the client (if needed)
        from api.tests.factories import UserFactory
        user = UserFactory(is_staff=True)
        cls.client.force_authenticate(user=user)
        
    def setup_method(self, method):
        """Set up for each test method."""
        # Create test data
        self.customer = CustomerFactory(
            company_name="Test Company",
            email="test@example.com"
        )
        self.product = ProductFactory(
            sku="TEST-SKU-001",
            customer=self.customer,
            labeling_unit_1="BOX",
            labeling_quantity_1=10
        )
        
    def teardown_method(self, method):
        """Clean up after each test method."""
        # Clean up test data
        Product.objects.all().delete()
    
    def test_get_product_list(self):
        """Test GET request to product list endpoint."""
        # Set up test data
        products = [ProductFactory(customer=self.customer) for _ in range(5)]
        
        # Make the request
        url = reverse('product-list')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        
        # The response data should include all products
        for product in products:
            assert any(item['id'] == product.id for item in response.data['data'])
    
    def test_get_product_by_id(self):
        """Test GET request to product detail endpoint."""
        # Make the request
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['id'] == self.product.id
        assert response.data['sku'] == self.product.sku
        assert response.data['customer'] == self.customer.id
        assert response.data['customer_details']['company_name'] == self.customer.company_name
    
    def test_get_products_by_customer(self):
        """Test GET request to filter products by customer."""
        # Create products for different customers
        other_customer = CustomerFactory()
        ProductFactory(customer=other_customer)
        ProductFactory(customer=other_customer)
        customer_products = [
            ProductFactory(customer=self.customer),
            ProductFactory(customer=self.customer)
        ]
        
        # Make the request
        url = f"{reverse('product-list')}?customer={self.customer.id}"
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        
        # Should only include products for the requested customer
        response_products = response.data['data']
        product_ids = [p['id'] for p in response_products]
        
        for product in customer_products:
            assert product.id in product_ids
        
        # Verify product count is correct (including the self.product created in setup)
        assert len(response_products) == len(customer_products) + 1
    
    def test_create_product(self):
        """Test POST request to create a product."""
        # Prepare data for creating a new product
        new_product_data = {
            'sku': 'NEW-TEST-SKU',
            'customer': self.customer.id,
            'labeling_unit_1': 'CASE',
            'labeling_quantity_1': 5
        }
        
        # Make the request
        url = reverse('product-list')
        response = self.client.post(url, new_product_data, format='json')
        
        # Verify the response
        assert response.status_code == 201
        assert response.data['success'] is True
        assert response.data['data']['sku'] == 'NEW-TEST-SKU'
        assert response.data['data']['customer'] == self.customer.id
        
        # Verify the product was created in the database
        assert Product.objects.filter(sku='NEW-TEST-SKU').exists()
    
    def test_update_product(self):
        """Test PUT request to update a product."""
        # Prepare data for updating the product
        update_data = {
            'sku': 'UPDATED-TEST-SKU',
            'customer': self.customer.id,
            'labeling_unit_1': 'PALLET',
            'labeling_quantity_1': 15
        }
        
        # Make the request
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.put(url, update_data, format='json')
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['sku'] == 'UPDATED-TEST-SKU'
        assert response.data['data']['labeling_unit_1'] == 'PALLET'
        
        # Verify the product was updated in the database
        self.product.refresh_from_db()
        assert self.product.sku == 'UPDATED-TEST-SKU'
        assert self.product.labeling_unit_1 == 'PALLET'
    
    def test_patch_product(self):
        """Test PATCH request to partially update a product."""
        # Prepare data for partially updating the product
        patch_data = {
            'labeling_quantity_1': 25
        }
        
        # Make the request
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.patch(url, patch_data, format='json')
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['labeling_quantity_1'] == 25
        
        # Verify the product was updated in the database
        self.product.refresh_from_db()
        assert self.product.labeling_quantity_1 == 25
    
    def test_delete_product(self):
        """Test DELETE request to delete a product."""
        # Create a product to delete (without any dependencies)
        product_to_delete = ProductFactory(customer=self.customer)
        
        # Make the request
        url = reverse('product-detail', kwargs={'pk': product_to_delete.pk})
        response = self.client.delete(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['message'] == 'Product deleted successfully'
        
        # Verify the product was deleted from the database
        assert not Product.objects.filter(id=product_to_delete.id).exists()
    
    def test_product_stats(self):
        """Test GET request to product stats endpoint."""
        # Create additional products 
        for i in range(5):
            ProductFactory(customer=self.customer)
        
        # Make the request
        url = reverse('product-stats')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'total_products' in response.data['data']
        assert 'products_by_customer' in response.data['data']
        
        # Should have stats for the customer
        customer_stats = response.data['data']['products_by_customer']
        customer_found = False
        for stat in customer_stats:
            if stat['customer__company_name'] == self.customer.company_name:
                assert stat['count'] == 6  # The self.product + 5 additional
                customer_found = True
                break
        
        assert customer_found, "Customer stats not found in the response"
    
    @pytest.mark.skip(reason="Full PACT verification requires a running service")
    def test_verify_product_pacts(self):
        """Verify all PACT contracts for the product API."""
        # This test requires a running API service
        if not os.path.exists(PACT_FILE):
            pytest.skip(f"PACT file not found: {PACT_FILE}")
        
        # Use the Pact verifier to validate all contracts
        verifier = Verifier(
            provider="product-api",
            provider_base_url=PROVIDER_URL
        )
        
        # Define provider states and set up the required state
        provider_states = {
            "a product exists": self.setup_product_exists,
            "multiple products exist": self.setup_multiple_products,
            "products for a specific customer exist": self.setup_products_for_customer
        }
        
        # Verify the PACT
        output, _ = verifier.verify_pacts(
            PACT_FILE,
            provider_states=provider_states,
            provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states"
        )
        
        assert output == 0, "PACT verification failed"
    
    def setup_product_exists(self):
        """Set up the 'a product exists' provider state."""
        # Create a test product with predictable data
        customer = CustomerFactory(company_name="PACT Test Company")
        return ProductFactory(
            sku="PACT-TEST-SKU",
            customer=customer,
            labeling_unit_1="BOX",
            labeling_quantity_1=10
        )
    
    def setup_multiple_products(self):
        """Set up the 'multiple products exist' provider state."""
        # Create multiple test products
        customer = CustomerFactory(company_name="PACT Test Company")
        products = []
        for i in range(5):
            products.append(ProductFactory(
                sku=f"PACT-SKU-{i}",
                customer=customer
            ))
        return products
    
    def setup_products_for_customer(self):
        """Set up the 'products for a specific customer exist' provider state."""
        # Create a specific customer with products
        customer = CustomerFactory(company_name="PACT Customer With Products")
        products = []
        for i in range(3):
            products.append(ProductFactory(
                sku=f"PACT-CUSTOMER-SKU-{i}",
                customer=customer
            ))
        return {'customer': customer, 'products': products}