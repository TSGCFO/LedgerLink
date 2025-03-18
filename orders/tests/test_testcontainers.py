import pytest
import os
import sys
from unittest.mock import MagicMock

from django.db import connection
from django.test import TestCase
from orders.models import OrderSKUView, Order
from customers.models import Customer
from products.models import Product

# Skip all tests if not using TestContainers
pytestmark = pytest.mark.skipif(
    os.environ.get('USE_TESTCONTAINERS', 'False').lower() != 'true',
    reason="TestContainers not enabled"
)

@pytest.mark.django_db
class TestContainersOrdersTest(TestCase):
    """Tests that verify OrderSKUView works with TestContainers setup."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create mock customer
        cls.customer = MagicMock(spec=Customer)
        cls.customer.id = 777
        cls.customer.company_name = "TestContainers Order Test Company"
        cls.customer.legal_business_name = "TestContainers Order Test Company LLC"
        cls.customer.email = "testcontainers@example.com"
        cls.customer.phone = "111-222-3333"
        cls.customer.is_active = True
        
        # Create mock product
        cls.product = MagicMock(spec=Product)
        cls.product.id = 888
        cls.product.customer = cls.customer
        cls.product.sku = "TESTCONTAINERS-SKU"
        cls.product.description = "TestContainers test product"
        
        # Create mock order
        cls.order = MagicMock(spec=Order)
        cls.order.id = 999
        cls.order.transaction_id = 99999
        cls.order.customer = cls.customer
        cls.order.reference_number = "REF-TESTCONTAINERS"
        cls.order.sku_quantity = {"TESTCONTAINERS-SKU": 25}
        cls.order.total_item_qty = 25
        cls.order.line_items = 1
    
    def test_postgresql_connection(self):
        """Test that we're connected to a PostgreSQL database."""
        # Get the database engine
        db_engine = connection.vendor
        self.assertEqual(db_engine, 'postgresql', 
                        "TestContainers should be using PostgreSQL")
    
    def test_testcontainers_environment(self):
        """Test TestContainers environment variables are properly set."""
        self.assertEqual(os.environ.get('USE_TESTCONTAINERS', '').lower(), 'true',
                        "USE_TESTCONTAINERS should be 'true'")
        
        # Verify we have TestContainers connection details
        tc_vars = [
            'TC_DB_NAME', 'TC_DB_USER', 'TC_DB_PASSWORD', 
            'TC_DB_HOST', 'TC_DB_PORT'
        ]
        
        for var in tc_vars:
            self.assertIsNotNone(os.environ.get(var), 
                               f"TestContainers environment variable {var} should be set")
    
    def test_materialized_view_creation(self):
        """Test that OrderSKUView materialized view was created in TestContainers."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_matviews WHERE matviewname = 'orders_orderskuview'")
            view_exists = bool(cursor.fetchone())
            self.assertTrue(view_exists, "OrderSKUView materialized view should exist")
    
    def test_refresh_view_in_testcontainers(self):
        """Test refreshing the materialized view in TestContainers."""
        # First refresh the view
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW orders_orderskuview")
        
        # Now verify the data is visible
        order_skus = OrderSKUView.objects.filter(order_id=self.order.id)
        self.assertTrue(order_skus.exists(), 
                       "OrderSKUView should contain data from our test order")