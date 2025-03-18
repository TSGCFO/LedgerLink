import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from customers.models import Customer
from customers.serializers import CustomerSerializer
from customers.tests.factories import CustomerFactory


@pytest.mark.unit
class CustomerSerializerTests(TestCase):
    """Test suite for the CustomerSerializer."""
    
    def test_serialize_customer(self):
        """Test serializing a customer object."""
        customer = CustomerFactory()
        serializer = CustomerSerializer(customer)
        data = serializer.data
        
        # Test serialized fields match the model
        self.assertEqual(data['id'], str(customer.id))
        self.assertEqual(data['company_name'], customer.company_name)
        self.assertEqual(data['legal_business_name'], customer.legal_business_name)
        self.assertEqual(data['email'], customer.email)
        self.assertEqual(data['phone'], customer.phone)
        self.assertEqual(data['address'], customer.address)
        self.assertEqual(data['city'], customer.city)
        self.assertEqual(data['state'], customer.state)
        self.assertEqual(data['zip'], customer.zip)  # Not zip_code, should match model field name
        self.assertEqual(data['country'], customer.country)
        self.assertEqual(data['business_type'], customer.business_type)
        self.assertEqual(data['is_active'], customer.is_active)
        
        # Check that created_at is included but read-only
        self.assertIn('created_at', data)
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid customer data."""
        valid_data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name LLC',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',  # Not zip_code, should match model field name
            'country': 'US',
            'business_type': 'Retail',
            'is_active': True
        }
        
        serializer = CustomerSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        customer = serializer.save()
        self.assertEqual(customer.company_name, valid_data['company_name'])
        self.assertEqual(customer.legal_business_name, valid_data['legal_business_name'])
        self.assertEqual(customer.email, valid_data['email'])
        self.assertEqual(customer.zip, valid_data['zip'])
    
    def test_company_name_required(self):
        """Test that company_name is required."""
        invalid_data = {
            'legal_business_name': 'Test Legal Name LLC',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',
            'country': 'US'
        }
        
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)
    
    def test_legal_business_name_required(self):
        """Test that legal_business_name is required."""
        invalid_data = {
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',
            'country': 'US'
        }
        
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('legal_business_name', serializer.errors)
    
    def test_email_validation(self):
        """Test email validation."""
        invalid_data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name LLC',
            'email': 'not-an-email',  # Invalid email
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',
            'country': 'US'
        }
        
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_email_uniqueness(self):
        """Test that email must be unique."""
        # Create a customer with a specific email
        existing_email = 'existing@example.com'
        CustomerFactory(email=existing_email)
        
        # Try to create another customer with the same email
        duplicate_data = {
            'company_name': 'Another Company',
            'legal_business_name': 'Another Legal Name LLC',
            'email': existing_email,
            'phone': '555-5678',
            'address': '456 Oak St',
            'city': 'Othertown',
            'state': 'NY',
            'zip': '54321',
            'country': 'US'
        }
        
        serializer = CustomerSerializer(data=duplicate_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_update_customer(self):
        """Test updating a customer with the serializer."""
        customer = CustomerFactory(company_name="Old Company", country="US")
        
        update_data = {
            'company_name': 'New Company Name',
            'country': 'CA'
        }
        
        serializer = CustomerSerializer(customer, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_customer = serializer.save()
        self.assertEqual(updated_customer.company_name, update_data['company_name'])
        self.assertEqual(updated_customer.country, update_data['country'])
        
        # Other fields should remain unchanged
        self.assertEqual(updated_customer.email, customer.email)
        self.assertEqual(updated_customer.legal_business_name, customer.legal_business_name)
    
    def test_deserialize_with_extra_fields(self):
        """Test deserializing with extra fields that shouldn't be saved."""
        valid_data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name LLC',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345',
            'country': 'US',
            'is_active': True,
            'extra_field': 'This should be ignored'
        }
        
        serializer = CustomerSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        customer = serializer.save()
        self.assertFalse(hasattr(customer, 'extra_field'))
    
    def test_created_at_readonly(self):
        """Test that created_at is read-only."""
        # Create a customer
        customer = CustomerFactory()
        original_created_at = customer.created_at
        
        # Try to update created_at
        update_data = {
            'created_at': '2020-01-01T00:00:00Z'
        }
        
        serializer = CustomerSerializer(customer, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_customer = serializer.save()
        self.assertEqual(updated_customer.created_at, original_created_at)