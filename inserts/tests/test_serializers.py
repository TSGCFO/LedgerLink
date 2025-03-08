from django.test import TestCase
from rest_framework.exceptions import ValidationError
from inserts.serializers import InsertSerializer
from inserts.tests.factories import InsertFactory
from customers.tests.factories import CustomerFactory


class InsertSerializerTest(TestCase):
    """Test suite for the InsertSerializer."""

    def setUp(self):
        """Set up test data."""
        self.customer = CustomerFactory()
        self.insert = InsertFactory(
            sku='TEST-SKU-001',
            insert_name='Test Insert',
            insert_quantity=50,
            customer=self.customer
        )
        self.serializer = InsertSerializer(instance=self.insert)

    def test_contains_expected_fields(self):
        """Test that the serialized data contains the expected fields."""
        data = self.serializer.data
        expected_fields = [
            'id', 'sku', 'insert_name', 'insert_quantity',
            'customer', 'customer_details', 'created_at', 'updated_at'
        ]
        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_sku_field_content(self):
        """Test that the SKU field matches the expected value."""
        data = self.serializer.data
        self.assertEqual(data['sku'], 'TEST-SKU-001')

    def test_customer_details_nested_serialization(self):
        """Test that customer_details is properly nested."""
        data = self.serializer.data
        self.assertIn('customer_details', data)
        self.assertEqual(data['customer_details']['id'], self.customer.id)
        self.assertEqual(data['customer_details']['company_name'], self.customer.company_name)

    def test_insert_quantity_validation(self):
        """Test validation for insert_quantity."""
        # Test with invalid (negative) quantity
        serializer = InsertSerializer(data={
            'sku': 'TEST-SKU-002',
            'insert_name': 'Test Insert 2',
            'insert_quantity': -10,
            'customer': self.customer.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('insert_quantity', serializer.errors)

        # Test with valid quantity
        serializer = InsertSerializer(data={
            'sku': 'TEST-SKU-002',
            'insert_name': 'Test Insert 2',
            'insert_quantity': 10,
            'customer': self.customer.id
        })
        self.assertTrue(serializer.is_valid())

    def test_sku_validation(self):
        """Test validation for SKU uniqueness per customer."""
        # Create a serializer with the same SKU (should fail validation)
        serializer = InsertSerializer(data={
            'sku': 'TEST-SKU-001',  # Same as existing
            'insert_name': 'Test Insert 2',
            'insert_quantity': 25,
            'customer': self.customer.id  # Same customer
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku', serializer.errors)

        # Create a serializer with the same SKU but different customer (should be valid)
        new_customer = CustomerFactory()
        serializer = InsertSerializer(data={
            'sku': 'TEST-SKU-001',  # Same SKU
            'insert_name': 'Test Insert 3',
            'insert_quantity': 30,
            'customer': new_customer.id  # Different customer
        })
        self.assertTrue(serializer.is_valid())

    def test_sku_normalization(self):
        """Test that SKUs are normalized to uppercase."""
        serializer = InsertSerializer(data={
            'sku': 'test-sku-002',  # lowercase
            'insert_name': 'Test Insert 2',
            'insert_quantity': 25,
            'customer': self.customer.id
        })
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(serializer.instance.sku, 'TEST-SKU-002')