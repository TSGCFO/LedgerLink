import pytest
from django.urls import reverse, resolve
from django.test import TestCase

from customers.views import CustomerViewSet


@pytest.mark.unit
class CustomerURLTests(TestCase):
    """Test customer app URL patterns."""
    
    def test_customer_list_url(self):
        """Test customer list URL."""
        url = reverse('customer-list')
        self.assertEqual(url, '/api/v1/customers/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            CustomerViewSet.__name__
        )
    
    def test_customer_detail_url(self):
        """Test customer detail URL."""
        url = reverse('customer-detail', kwargs={'pk': 1})
        self.assertEqual(url, '/api/v1/customers/1/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            CustomerViewSet.__name__
        )
    
    def test_customer_stats_url(self):
        """Test customer stats URL."""
        url = reverse('customer-stats')
        self.assertEqual(url, '/api/v1/customers/stats/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            CustomerViewSet.__name__
        )