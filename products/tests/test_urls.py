import pytest
from django.urls import reverse, resolve
from django.test import TestCase

from products.views import ProductViewSet


@pytest.mark.unit
class ProductURLTests(TestCase):
    """Test product app URL patterns."""
    
    def test_product_list_url(self):
        """Test product list URL."""
        url = reverse('product-list')
        self.assertEqual(url, '/api/v1/products/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            ProductViewSet.__name__
        )
    
    def test_product_detail_url(self):
        """Test product detail URL."""
        url = reverse('product-detail', kwargs={'pk': 1})
        self.assertEqual(url, '/api/v1/products/1/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            ProductViewSet.__name__
        )
    
    def test_product_stats_url(self):
        """Test product stats URL."""
        url = reverse('product-stats')
        self.assertEqual(url, '/api/v1/products/stats/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            ProductViewSet.__name__
        )