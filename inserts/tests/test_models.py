from django.test import TestCase
from django.db.utils import IntegrityError
from inserts.models import Insert
from inserts.tests.factories import InsertFactory
from customers.tests.factories import CustomerFactory


class InsertModelTest(TestCase):
    """Test suite for the Insert model."""

    def setUp(self):
        """Set up test data."""
        self.customer = CustomerFactory()
        self.insert = InsertFactory(
            sku='TEST-SKU-001',
            insert_name='Test Insert',
            insert_quantity=50,
            customer=self.customer
        )

    def test_insert_creation(self):
        """Test that an Insert instance can be created."""
        self.assertIsInstance(self.insert, Insert)
        self.assertEqual(self.insert.sku, 'TEST-SKU-001')
        self.assertEqual(self.insert.insert_name, 'Test Insert')
        self.assertEqual(self.insert.insert_quantity, 50)
        self.assertEqual(self.insert.customer, self.customer)
        self.assertIsNotNone(self.insert.created_at)
        self.assertIsNotNone(self.insert.updated_at)

    def test_string_representation(self):
        """Test the string representation of an Insert."""
        self.assertEqual(str(self.insert), 'Test Insert (TEST-SKU-001)')

    def test_customer_cascade_delete(self):
        """Test that when a customer is deleted, its inserts are also deleted."""
        # Count inserts before deletion
        initial_count = Insert.objects.count()
        self.assertEqual(initial_count, 1)
        
        # Delete the customer
        self.customer.delete()
        
        # Check that the insert is also deleted
        self.assertEqual(Insert.objects.count(), 0)

    def test_insert_quantity_constraints(self):
        """Test that insert_quantity must be a positive integer."""
        # Try to create an insert with a negative quantity
        with self.assertRaises(Exception):
            InsertFactory(
                sku='TEST-SKU-002',
                insert_name='Test Insert 2',
                insert_quantity=-10,
                customer=self.customer
            )

    def test_multiple_inserts_for_same_customer(self):
        """Test that a customer can have multiple inserts."""
        # Create a second insert for the same customer
        insert2 = InsertFactory(
            sku='TEST-SKU-002',
            insert_name='Test Insert 2',
            insert_quantity=25,
            customer=self.customer
        )
        
        # Verify both inserts exist
        self.assertEqual(Insert.objects.count(), 2)
        self.assertEqual(self.customer.insert_set.count(), 2)
        
        # Verify the second insert's properties
        self.assertEqual(insert2.sku, 'TEST-SKU-002')
        self.assertEqual(insert2.insert_name, 'Test Insert 2')
        self.assertEqual(insert2.insert_quantity, 25)
        self.assertEqual(insert2.customer, self.customer)