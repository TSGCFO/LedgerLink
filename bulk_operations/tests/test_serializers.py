from django.test import TestCase
from decimal import Decimal
from bulk_operations.serializers import (
    BulkSerializerFactory, BulkImportResponseSerializer,
    CustomerBulkSerializer, OrderBulkSerializer, MaterialBulkSerializer, InsertBulkSerializer
)
from customers.tests.factories import CustomerFactory


class BulkSerializerFactoryTest(TestCase):
    """Test suite for the BulkSerializerFactory."""

    def test_get_serializer_valid_types(self):
        """Test that the factory returns the correct serializer for valid template types."""
        # Test customer serializer
        serializer_class = BulkSerializerFactory.get_serializer('customers')
        self.assertEqual(serializer_class, CustomerBulkSerializer)
        
        # Test order serializer
        serializer_class = BulkSerializerFactory.get_serializer('orders')
        self.assertEqual(serializer_class, OrderBulkSerializer)
        
        # Test material serializer
        serializer_class = BulkSerializerFactory.get_serializer('materials')
        self.assertEqual(serializer_class, MaterialBulkSerializer)
        
        # Test insert serializer
        serializer_class = BulkSerializerFactory.get_serializer('inserts')
        self.assertEqual(serializer_class, InsertBulkSerializer)

    def test_get_serializer_invalid_type(self):
        """Test that the factory raises an exception for invalid template types."""
        with self.assertRaises(KeyError):
            BulkSerializerFactory.get_serializer('invalid_type')


class BulkImportResponseSerializerTest(TestCase):
    """Test suite for the BulkImportResponseSerializer."""

    def test_valid_response_data(self):
        """Test that the serializer validates correct response data."""
        # Success response
        data = {
            'success': True,
            'message': 'Import completed successfully',
            'import_summary': {
                'total_rows': 10,
                'successful': 8,
                'failed': 2
            }
        }
        
        serializer = BulkImportResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Error response
        data = {
            'success': False,
            'message': 'Import failed',
            'errors': [
                {'row': 2, 'field': 'name', 'error': 'Required field is empty'},
                {'row': 5, 'field': 'price', 'error': 'Invalid decimal value'}
            ]
        }
        
        serializer = BulkImportResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_response_data(self):
        """Test that the serializer rejects invalid response data."""
        # Missing required fields
        data = {
            'success': True
            # 'message' is missing
        }
        
        serializer = BulkImportResponseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('message', serializer.errors)


class CustomerBulkSerializerTest(TestCase):
    """Test suite for the CustomerBulkSerializer."""

    def test_valid_customer_data(self):
        """Test that the serializer validates correct customer data."""
        data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Company Legal Name',
            'email': 'test@example.com',
            'phone': '555-123-4567',
            'address': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'zip': '12345',
            'country': 'Test Country',
            'business_type': 'Corporation'
        }
        
        serializer = CustomerBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_customer_data(self):
        """Test that the serializer rejects invalid customer data."""
        # Missing required fields
        data = {
            'company_name': 'Test Company',
            # 'legal_business_name' is missing
            # 'email' is missing
            'phone': '555-123-4567'
        }
        
        serializer = CustomerBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('legal_business_name', serializer.errors)
        self.assertIn('email', serializer.errors)
        
        # Invalid email
        data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Company Legal Name',
            'email': 'invalid-email',
            'phone': '555-123-4567'
        }
        
        serializer = CustomerBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class MaterialBulkSerializerTest(TestCase):
    """Test suite for the MaterialBulkSerializer."""

    def test_valid_material_data(self):
        """Test that the serializer validates correct material data."""
        data = {
            'name': 'Test Material',
            'description': 'Test Description',
            'unit_price': '10.50'
        }
        
        serializer = MaterialBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_material_data(self):
        """Test that the serializer rejects invalid material data."""
        # Missing required fields
        data = {
            'name': 'Test Material',
            'description': 'Test Description'
            # 'unit_price' is missing
        }
        
        serializer = MaterialBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('unit_price', serializer.errors)
        
        # Invalid unit_price (non-decimal)
        data = {
            'name': 'Test Material',
            'description': 'Test Description',
            'unit_price': 'not-a-decimal'
        }
        
        serializer = MaterialBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('unit_price', serializer.errors)


class InsertBulkSerializerTest(TestCase):
    """Test suite for the InsertBulkSerializer."""

    def setUp(self):
        """Set up test data."""
        self.customer = CustomerFactory()

    def test_valid_insert_data(self):
        """Test that the serializer validates correct insert data."""
        data = {
            'sku': 'TEST-SKU-001',
            'insert_name': 'Test Insert',
            'insert_quantity': 50,
            'customer': self.customer.id
        }
        
        serializer = InsertBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_insert_data(self):
        """Test that the serializer rejects invalid insert data."""
        # Missing required fields
        data = {
            'sku': 'TEST-SKU-001',
            # 'insert_name' is missing
            'insert_quantity': 50,
            'customer': self.customer.id
        }
        
        serializer = InsertBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('insert_name', serializer.errors)
        
        # Invalid customer ID
        data = {
            'sku': 'TEST-SKU-001',
            'insert_name': 'Test Insert',
            'insert_quantity': 50,
            'customer': 9999  # Non-existent customer ID
        }
        
        serializer = InsertBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer', serializer.errors)
        
        # Invalid quantity (non-integer)
        data = {
            'sku': 'TEST-SKU-001',
            'insert_name': 'Test Insert',
            'insert_quantity': 'not-an-integer',
            'customer': self.customer.id
        }
        
        serializer = InsertBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('insert_quantity', serializer.errors)