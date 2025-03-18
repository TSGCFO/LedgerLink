import pytest
import os
from unittest.mock import MagicMock
from django.db import connection
from django.test import TestCase
from orders.models import OrderSKUView, Order
from customers.models import Customer
from products.models import Product

# Skip all tests if not in Docker
pytestmark = pytest.mark.skipif(
    not (os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true'),
    reason="Docker environment not detected"
)

@pytest.mark.django_db
class DockerOrdersTest(TestCase):
    """Tests that verify OrderSKUView works in Docker environment."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Use mock objects instead of database
        # Create mock customer
        cls.customer = MagicMock(spec=Customer)
        cls.customer.id = 888
        cls.customer.company_name = "Docker Order Test Company"
        cls.customer.legal_business_name = "Docker Order Test Company LLC"
        cls.customer.email = "docker@example.com"
        cls.customer.phone = "444-555-6666"
        cls.customer.is_active = True
        
        # Create mock product
        cls.product = MagicMock(spec=Product)
        cls.product.id = 999
        cls.product.customer = cls.customer
        cls.product.sku = "DOCKER-SKU"
        cls.product.description = "Docker test product"
        
        # Create mock order
        cls.order = MagicMock(spec=Order)
        cls.order.id = 777
        cls.order.transaction_id = 88888
        cls.order.customer = cls.customer
        cls.order.reference_number = "REF-DOCKER"
        cls.order.sku_quantity = {"DOCKER-SKU": 50}
        cls.order.total_item_qty = 50
        cls.order.line_items = 1
    
    def test_docker_environment(self):
        """Verify we're running in Docker environment."""
        self.assertTrue(
            os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true',
            "Tests should be running in Docker"
        )
        
        # Check that database settings are for Docker
        self.assertEqual(
            os.environ.get('DB_HOST', ''), 'db',
            "DB_HOST should be 'db' in Docker environment"
        )
    
    def test_materialized_view_in_docker(self):
        """Test that OrderSKUView materialized view was created in Docker."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_matviews WHERE matviewname = 'orders_orderskuview'")
            view_exists = bool(cursor.fetchone())
            self.assertTrue(view_exists, "OrderSKUView materialized view should exist in Docker")
    
    def test_refresh_view_in_docker(self):
        """Test refreshing the materialized view in Docker."""
        # First refresh the view
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW orders_orderskuview")
        
        # Now verify the data is visible
        order_skus = OrderSKUView.objects.filter(order_id=self.order.id)
        self.assertTrue(order_skus.exists(), 
                       "OrderSKUView should contain data from our test order")