"""
Basic tests for customer_services that will definitely run in Docker environment.
"""
from django.test import TestCase
from decimal import Decimal

from customer_services.models import CustomerService
from customers.models import Customer
from services.models import Service


class CustomerServiceBasicTest(TestCase):
    """Basic tests for CustomerService model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com",
            phone="123-456-7890"
        )
        
        # Create a service
        self.service = Service.objects.create(
            name="Test Service",
            description="A test service",
            price=Decimal('100.00')
        )
    
    def test_create_customer_service(self):
        """Test creating a customer service."""
        cs = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        self.assertEqual(cs.customer, self.customer)
        self.assertEqual(cs.service, self.service)
        self.assertEqual(cs.unit_price, Decimal('99.99'))
    
    def test_string_representation(self):
        """Test the string representation."""
        cs = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        expected = f"{self.customer} - {self.service}"
        self.assertEqual(str(cs), expected)