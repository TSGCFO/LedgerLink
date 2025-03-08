"""
Direct test for Order model that specifically tests the is_active field.
"""
from django.test import TransactionTestCase
from django.db import connection
from customers.models import Customer
from orders.models import Order

class DirectOrderModelTest(TransactionTestCase):
    """Tests Order model directly with minimal dependencies."""
    
    def setUp(self):
        """Set up test data."""
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Company LLC",
            email="test@example.com",
            is_active=True
        )
    
    def test_customer_is_active_field(self):
        """Test that the is_active field exists and works properly."""
        # Verify initial value
        self.assertTrue(self.customer.is_active)
        
        # Update and verify
        self.customer.is_active = False
        self.customer.save()
        
        # Refresh from DB
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)
    
    def test_order_creation(self):
        """Test that we can create an order."""
        order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="TEST-REF",
            ship_to_name="Test Recipient",
            ship_to_address="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            sku_quantity={"TEST-SKU": 10},
            total_item_qty=10,
            line_items=1,
            status="draft",
            priority="medium"
        )
        
        # Verify order was created
        self.assertEqual(order.transaction_id, 12345)
        self.assertEqual(order.customer, self.customer)
        
        # Verify we can query it back
        order_from_db = Order.objects.get(transaction_id=12345)
        self.assertEqual(order_from_db.reference_number, "TEST-REF")
        self.assertEqual(order_from_db.status, "draft")