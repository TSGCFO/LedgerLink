"""
Basic tests for orders that will definitely run in Docker environment.
"""
from django.test import TestCase
from decimal import Decimal

from orders.models import Order
from customers.models import Customer


class OrderBasicTest(TestCase):
    """Basic tests for Order model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Company LLC",
            email="test@example.com",
            phone="123-456-7890",
            is_active=True
        )
    
    def test_create_order(self):
        """Test creating an order."""
        order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF-001",
            sku_quantity={"SKU1": 10, "SKU2": 5},
            total_item_qty=15,
            line_items=2
        )
        
        self.assertEqual(order.transaction_id, 12345)
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.reference_number, "REF-001")
    
    def test_string_representation(self):
        """Test the string representation."""
        order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF-001"
        )
        
        expected = f"Order {order.transaction_id} for {self.customer}"
        self.assertEqual(str(order), expected)