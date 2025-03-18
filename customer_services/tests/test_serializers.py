# customer_services/tests/test_serializers.py

from django.test import TestCase
from decimal import Decimal
from rest_framework.exceptions import ValidationError

from customer_services.models import CustomerService
from customer_services.serializers import CustomerServiceSerializer
from customer_services.tests.factories import CustomerServiceFactory
from customers.tests.factories import CustomerFactory
from services.tests.factories import ServiceFactory
from products.tests.factories import ProductFactory

class CustomerServiceSerializerTest(TestCase):
    """Test case for the CustomerServiceSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = CustomerFactory()
        self.service = ServiceFactory()
        self.customer_service = CustomerServiceFactory(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        self.product1 = ProductFactory(customer=self.customer)
        self.product2 = ProductFactory(customer=self.customer)
        self.customer_service.skus.add(self.product1, self.product2)
        
        self.serializer = CustomerServiceSerializer(instance=self.customer_service)
    
    def test_contains_expected_fields(self):
        """Test that serialized data contains all expected fields."""
        data = self.serializer.data
        expected_fields = [
            'id', 'customer', 'customer_details',
            'service', 'service_details', 'unit_price',
            'sku_list', 'created_at', 'updated_at'
        ]
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_customer_field_content(self):
        """Test that customer field contains the correct ID."""
        data = self.serializer.data
        self.assertEqual(data['customer'], self.customer.id)
    
    def test_service_field_content(self):
        """Test that service field contains the correct ID."""
        data = self.serializer.data
        self.assertEqual(data['service'], self.service.id)
    
    def test_unit_price_field_content(self):
        """Test that unit_price field contains the correct value."""
        data = self.serializer.data
        self.assertEqual(data['unit_price'], '99.99')
    
    def test_customer_details_field_content(self):
        """Test that customer_details field contains nested customer data."""
        data = self.serializer.data
        self.assertEqual(data['customer_details']['id'], self.customer.id)
        self.assertEqual(data['customer_details']['company_name'], self.customer.company_name)
    
    def test_service_details_field_content(self):
        """Test that service_details field contains nested service data."""
        data = self.serializer.data
        self.assertEqual(data['service_details']['id'], self.service.id)
        self.assertEqual(data['service_details']['service_name'], self.service.service_name)
    
    def test_sku_list_field_content(self):
        """Test that sku_list field contains all SKUs."""
        data = self.serializer.data
        self.assertEqual(len(data['sku_list']), 2)
        self.assertIn(self.product1.sku, data['sku_list'])
        self.assertIn(self.product2.sku, data['sku_list'])
    
    def test_creation_with_valid_data(self):
        """Test that a customer service can be created with valid data."""
        # Create a new customer and service
        new_customer = CustomerFactory()
        new_service = ServiceFactory()
        
        # Serialize data for creation
        data = {
            'customer': new_customer.id,
            'service': new_service.id,
            'unit_price': '129.99'
        }
        serializer = CustomerServiceSerializer(data=data)
        
        # Check that serializer is valid
        self.assertTrue(serializer.is_valid())
        
        # Save the serializer to create a new customer service
        instance = serializer.save()
        
        # Check that the customer service was created correctly
        self.assertEqual(instance.customer, new_customer)
        self.assertEqual(instance.service, new_service)
        self.assertEqual(instance.unit_price, Decimal('129.99'))
    
    def test_validation_prevents_duplicate_customer_service(self):
        """Test that serializer prevents duplicate customer-service combinations."""
        # Try to create a duplicate customer service
        data = {
            'customer': self.customer.id,
            'service': self.service.id,
            'unit_price': '79.99'
        }
        serializer = CustomerServiceSerializer(data=data)
        
        # Check that serializer is invalid
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('This service is already assigned to this customer.', serializer.errors['non_field_errors'][0])
    
    def test_update_with_valid_data(self):
        """Test that a customer service can be updated with valid data."""
        # Update data
        data = {
            'customer': self.customer.id,
            'service': self.service.id,
            'unit_price': '149.99'
        }
        serializer = CustomerServiceSerializer(instance=self.customer_service, data=data)
        
        # Check that serializer is valid
        self.assertTrue(serializer.is_valid())
        
        # Save the serializer to update the customer service
        instance = serializer.save()
        
        # Check that the customer service was updated correctly
        self.assertEqual(instance.unit_price, Decimal('149.99'))
    
    def test_invalid_unit_price(self):
        """Test validation with invalid unit price."""
        # Try to create a customer service with an invalid unit price
        new_customer = CustomerFactory()
        new_service = ServiceFactory()
        
        # Test with negative unit price
        data = {
            'customer': new_customer.id,
            'service': new_service.id,
            'unit_price': '-10.00'
        }
        serializer = CustomerServiceSerializer(data=data)
        
        # Check that serializer is invalid
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        # Test with missing customer
        data = {
            'service': self.service.id,
            'unit_price': '99.99'
        }
        serializer = CustomerServiceSerializer(data=data)
        
        # Check that serializer is invalid
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer', serializer.errors)
        
        # Test with missing service
        data = {
            'customer': self.customer.id,
            'unit_price': '99.99'
        }
        serializer = CustomerServiceSerializer(data=data)
        
        # Check that serializer is invalid
        self.assertFalse(serializer.is_valid())
        self.assertIn('service', serializer.errors)
        
        # Test with missing unit_price
        data = {
            'customer': self.customer.id,
            'service': self.service.id
        }
        serializer = CustomerServiceSerializer(data=data)
        
        # Check that serializer is invalid
        self.assertFalse(serializer.is_valid())
        self.assertIn('unit_price', serializer.errors)