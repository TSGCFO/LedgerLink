import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import BaseAPITestCase
from products.models import Product
from .factories import ProductFactory, CustomerFactory


@pytest.mark.api
class TestProductViewSet:
    """Test suite for the ProductViewSet."""
    
    @pytest.fixture
    def api_client(self):
        """Create and return an authenticated API client."""
        from api.tests.factories import UserFactory
        client = APIClient()
        user = UserFactory(is_staff=True)
        client.force_authenticate(user=user)
        return client
    
    @pytest.fixture
    def customer(self, db):
        """Create and return a test customer."""
        return CustomerFactory()
    
    @pytest.fixture
    def products(self, db, customer):
        """Create and return a list of test products."""
        return [
            ProductFactory(customer=customer, sku=f'TEST-SKU-{i}')
            for i in range(5)
        ]
    
    def test_list_products(self, db, api_client, products):
        """Test listing all products."""
        url = reverse('product-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 5
    
    def test_list_products_filter_by_customer(self, db, api_client, customer, products):
        """Test filtering products by customer."""
        # Create additional products for a different customer
        other_customer = CustomerFactory()
        for i in range(3):
            ProductFactory(customer=other_customer, sku=f'OTHER-SKU-{i}')
        
        url = reverse('product-list')
        response = api_client.get(url, {'customer': customer.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 5  # Only the original 5 products
    
    def test_list_products_search(self, db, api_client, products):
        """Test searching products."""
        url = reverse('product-list')
        response = api_client.get(url, {'search': 'TEST-SKU-3'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['sku'] == 'TEST-SKU-3'
    
    def test_create_product(self, db, api_client, customer):
        """Test creating a new product."""
        url = reverse('product-list')
        data = {
            'sku': 'NEW-TEST-SKU',
            'customer': customer.id,
            'labeling_unit_1': 'BOX',
            'labeling_quantity_1': 10
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['sku'] == 'NEW-TEST-SKU'
        
        # Verify the product was actually created in the database
        assert Product.objects.filter(sku='NEW-TEST-SKU').exists()
    
    def test_retrieve_product(self, db, api_client, products):
        """Test retrieving a specific product."""
        product = products[0]
        url = reverse('product-detail', args=[product.id])
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
        assert response.data['sku'] == product.sku
    
    def test_update_product(self, db, api_client, products):
        """Test updating a product."""
        product = products[0]
        url = reverse('product-detail', args=[product.id])
        data = {
            'sku': 'UPDATED-SKU',
            'customer': product.customer.id,
            'labeling_unit_1': 'PALLET',
            'labeling_quantity_1': 15
        }
        
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['sku'] == 'UPDATED-SKU'
        assert response.data['data']['labeling_unit_1'] == 'PALLET'
        assert response.data['data']['labeling_quantity_1'] == 15
        
        # Verify the product was actually updated in the database
        product.refresh_from_db()
        assert product.sku == 'UPDATED-SKU'
        assert product.labeling_unit_1 == 'PALLET'
        assert product.labeling_quantity_1 == 15
    
    def test_partial_update_product(self, db, api_client, products):
        """Test partially updating a product."""
        product = products[0]
        original_sku = product.sku
        url = reverse('product-detail', args=[product.id])
        data = {
            'labeling_quantity_1': 25  # Only update one field
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['sku'] == original_sku  # SKU didn't change
        assert response.data['data']['labeling_quantity_1'] == 25
        
        # Verify the product was actually updated in the database
        product.refresh_from_db()
        assert product.sku == original_sku
        assert product.labeling_quantity_1 == 25
    
    def test_delete_product(self, db, api_client, products):
        """Test deleting a product."""
        product = products[0]
        url = reverse('product-detail', args=[product.id])
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Product deleted successfully'
        
        # Verify the product was actually deleted from the database
        assert not Product.objects.filter(id=product.id).exists()
    
    def test_delete_product_in_use(self, db, api_client, products, monkeypatch):
        """Test attempting to delete a product that is in use."""
        product = products[0]
        url = reverse('product-detail', args=[product.id])
        
        # Mock the customerservice_set.exists method to return True
        def mock_exists():
            return True
        
        monkeypatch.setattr(
            product.customerservice_set,
            'exists',
            mock_exists
        )
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert "Cannot delete product as it is used in customer services" in response.data['message']
        
        # Verify the product was not deleted from the database
        assert Product.objects.filter(id=product.id).exists()
    
    def test_stats_endpoint(self, db, api_client, customer, products):
        """Test the stats endpoint."""
        # Create products for another customer
        other_customer = CustomerFactory(company_name="Other Company")
        for i in range(3):
            ProductFactory(customer=other_customer)
        
        url = reverse('product-stats')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['total_products'] == 8  # 5 + 3
        
        # Check products_by_customer list
        products_by_customer = response.data['data']['products_by_customer']
        assert len(products_by_customer) == 2  # Two customers
        
        # Products should be grouped by customer
        customer_counts = {item['customer__company_name']: item['count'] for item in products_by_customer}
        assert customer_counts[customer.company_name] == 5
        assert customer_counts[other_customer.company_name] == 3


class ProductViewSetIntegrationTest(BaseAPITestCase):
    """Integration tests for ProductViewSet using BaseAPITestCase."""
    
    def setUp(self):
        super().setUp()
        self.login_as_admin()
        self.customer = CustomerFactory()
        self.products = [
            ProductFactory(customer=self.customer, sku=f'TEST-SKU-{i}')
            for i in range(3)
        ]
    
    def test_list_products(self):
        """Test listing all products."""
        response = self.api_get('product-list')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)
    
    def test_create_product(self):
        """Test creating a new product."""
        data = {
            'sku': 'INTEGRATION-SKU',
            'customer': self.customer.id,
            'labeling_unit_1': 'BOX',
            'labeling_quantity_1': 5
        }
        
        response = self.api_post('product-list', data=data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['sku'], 'INTEGRATION-SKU')