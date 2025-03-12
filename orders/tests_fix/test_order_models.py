"""
Basic test for Order models
"""
from django.test import TestCase
import random

from orders.models import Order
from customers.models import Customer


class TestOrderModel(TestCase):
    """Test case for Order model"""
    
    def setUp(self):
        """Set up test data."""
        # Generate a random transaction ID to avoid uniqueness conflicts
        self.transaction_id = random.randint(100000, 999999)
        
        # Create a customer with is_active field
        self.customer = Customer.objects.create(
            company_name="Test Order Corp",
            legal_business_name="Test Order Corp LLC",
            email="testorder@example.com",
            phone="987-654-3210",
            is_active=True
        )
        
        # Create an order
        self.order = Order.objects.create(
            transaction_id=self.transaction_id,
            customer=self.customer,
            reference_number="REF-TEST-999",
            ship_to_name="Order Recipient",
            ship_to_address="456 Order St",
            ship_to_city="Order City", 
            ship_to_state="OS",
            ship_to_zip="54321",
            sku_quantity={"TEST-SKU-A": 10, "TEST-SKU-B": 5},
            total_item_qty=15,
            line_items=2,
            status="draft",
            priority="medium"
        )
    
    def test_basic_attributes(self):
        """Test basic attributes of Order."""
        self.assertEqual(self.order.transaction_id, self.transaction_id)
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.reference_number, "REF-TEST-999")
        self.assertEqual(self.order.status, "draft")
        self.assertEqual(self.order.priority, "medium")
    
    def test_string_representation(self):
        """Test string representation of Order."""
        expected = f"Order {self.order.transaction_id} for {self.customer}"
        self.assertEqual(str(self.order), expected)
    
    def test_sku_quantity(self):
        """Test SKU quantity JSON field."""
        self.assertEqual(self.order.sku_quantity["TEST-SKU-A"], 10)
        self.assertEqual(self.order.sku_quantity["TEST-SKU-B"], 5)
    
    def test_query_filter(self):
        """Test filtering orders by attributes."""
        query_result = Order.objects.filter(
            customer=self.customer,
            status="draft"
        )
        self.assertEqual(query_result.count(), 1)
        self.assertEqual(query_result.first(), self.order)
    
    def test_status_update(self):
        """Test updating order status."""
        self.order.status = "submitted"
        self.order.save()
        
        # Refresh from database
        refreshed_order = Order.objects.get(transaction_id=self.order.transaction_id)
        self.assertEqual(refreshed_order.status, "submitted")
    
    def test_customer_relationship(self):
        """Test relationship with Customer model"""
        # Verify customer attributes through relationship
        self.assertEqual(self.order.customer.company_name, "Test Order Corp")
        self.assertEqual(self.order.customer.is_active, True)
        
        # Update customer is_active
        self.customer.is_active = False
        self.customer.save()
        
        # Refresh and verify changes reflected
        self.order.refresh_from_db()
        self.assertFalse(self.order.customer.is_active)