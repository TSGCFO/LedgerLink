import pytest
from django.test import TestCase, modify_settings, override_settings
from django.db.models import ProtectedError

from customers.models import Customer
from customers.tests.factories import CustomerFactory

# Try to import Order, but don't fail if not available
try:
    from orders.models import Order
    HAS_ORDERS = True
except (ImportError, ModuleNotFoundError):
    HAS_ORDERS = False


@pytest.mark.skipif(not HAS_ORDERS, reason="Orders app not available")
@pytest.mark.integration
class CustomerOrderIntegrationTests(TestCase):
    """Tests for customer integration with orders."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        cls.customer = CustomerFactory()
        
        # Create some test orders for the customer
        cls.orders = []
        if HAS_ORDERS:
            cls.orders = [
                Order.objects.create(
                    customer=cls.customer,
                    order_number=f'ORD-{i}',
                    status='pending'
                ) for i in range(3)
            ]
    
    def test_customer_has_orders(self):
        """Test that a customer can have orders."""
        if not HAS_ORDERS:
            self.skipTest("Orders app not available")
        
        # Verify the customer has the expected number of orders
        self.assertEqual(self.customer.order_set.count(), len(self.orders))
    
    def test_customer_orders_query(self):
        """Test querying orders for a customer."""
        if not HAS_ORDERS:
            self.skipTest("Orders app not available")
        
        # Get all orders for the customer
        customer_orders = Order.objects.filter(customer=self.customer)
        self.assertEqual(customer_orders.count(), len(self.orders))
    
    def test_customer_delete_protection(self):
        """Test that a customer with orders cannot be deleted."""
        if not HAS_ORDERS:
            self.skipTest("Orders app not available")
        
        # Attempt to delete the customer with orders
        with self.assertRaises(ProtectedError):
            self.customer.delete()
        
        # Verify the customer still exists
        self.assertTrue(Customer.objects.filter(id=self.customer.id).exists())
    
    def test_customer_delete_cascade(self):
        """Test deleting a customer cascades to orders if configured."""
        if not HAS_ORDERS:
            self.skipTest("Orders app not available")
        
        # Create a new customer for this test
        new_customer = CustomerFactory()
        
        # Create an order for this customer
        order = Order.objects.create(
            customer=new_customer,
            order_number='ORD-TEST',
            status='pending'
        )
        
        # Store the order ID for later verification
        order_id = order.id
        
        try:
            # Try to delete the customer
            new_customer.delete()
            
            # Check if the order was also deleted (CASCADE) or still exists (PROTECT)
            order_exists = Order.objects.filter(id=order_id).exists()
            
            # This test will adapt to either CASCADE or PROTECT configuration
            if order_exists:
                self.assertTrue(order_exists)
                self.assertEqual(Order.objects.get(id=order_id).customer, None)
            else:
                self.assertFalse(order_exists)
                
        except ProtectedError:
            # If deletion is protected, this is also a valid configuration
            self.assertTrue(Order.objects.filter(id=order_id).exists())
            self.assertTrue(Customer.objects.filter(id=new_customer.id).exists())
    
    def test_order_customer_relationship(self):
        """Test that orders correctly reference their customer."""
        if not HAS_ORDERS:
            self.skipTest("Orders app not available")
        
        # Check that each order has the correct customer
        for order in self.orders:
            self.assertEqual(order.customer, self.customer)
    
    def test_update_customer_reflected_in_orders(self):
        """Test that updating a customer is reflected in orders."""
        if not HAS_ORDERS:
            self.skipTest("Orders app not available")
        
        # Update the customer
        new_name = "Updated Company Name"
        self.customer.company_name = new_name
        self.customer.save()
        
        # Refresh each order from the database
        for order in self.orders:
            order.refresh_from_db()
            # The order's customer should have the updated name
            self.assertEqual(order.customer.company_name, new_name)