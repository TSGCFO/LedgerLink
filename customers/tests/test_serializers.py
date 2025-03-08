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
        
        self.assertEqual(data['id'], str(customer.id))
        self.assertEqual(data['company_name'], customer.company_name)
        self.assertEqual(data['contact_name'], customer.contact_name)
        self.assertEqual(data['email'], customer.email)
        self.assertEqual(data['phone'], customer.phone)
        self.assertEqual(data['address'], customer.address)
        self.assertEqual(data['city'], customer.city)
        self.assertEqual(data['state'], customer.state)
        self.assertEqual(data['zip_code'], customer.zip_code)
        self.assertEqual(data['country'], customer.country)
        self.assertEqual(data['is_active'], customer.is_active)
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid customer data."""
        valid_data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345',
            'country': 'US',
            'is_active': True
        }
        
        serializer = CustomerSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        customer = serializer.save()
        self.assertEqual(customer.company_name, valid_data['company_name'])
        self.assertEqual(customer.email, valid_data['email'])
    
    def test_company_name_required(self):
        """Test that company_name is required."""
        invalid_data = {
            'contact_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345',
            'country': 'US'
        }
        
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)
    
    def test_email_validation(self):
        """Test email validation."""
        invalid_data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'email': 'not-an-email',  # Invalid email
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345',
            'country': 'US'
        }
        
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_update_customer(self):
        """Test updating a customer with the serializer."""
        customer = CustomerFactory(company_name="Old Company")
        
        update_data = {
            'company_name': 'New Company Name'
        }
        
        serializer = CustomerSerializer(customer, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_customer = serializer.save()
        self.assertEqual(updated_customer.company_name, update_data['company_name'])
        
        # Other fields should remain unchanged
        self.assertEqual(updated_customer.email, customer.email)
        self.assertEqual(updated_customer.contact_name, customer.contact_name)
    
    def test_deserialize_with_extra_fields(self):
        """Test deserializing with extra fields that shouldn't be saved."""
        valid_data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345',
            'country': 'US',
            'is_active': True,
            'extra_field': 'This should be ignored'
        }
        
        serializer = CustomerSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        customer = serializer.save()
        self.assertFalse(hasattr(customer, 'extra_field'))