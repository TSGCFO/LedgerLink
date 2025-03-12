# Direct test file for customer services models
from django.test import TestCase
from decimal import Decimal

from customer_services.models import CustomerService, CustomerServiceView
from customers.models import Customer
from services.models import Service
from products.models import Product

class TestCustomerServiceModel(TestCase):
    """Direct test for CustomerService model"""
    
    def setUp(self):
        """Set up test data."""
        # Create a customer
        self.customer = Customer.objects.create(
            company_name="Test Corp",
            contact_name="Test User",
            email="test@example.com",
            phone="123-456-7890",
            address="123 Test St",
            city="Testville",
            state="TS",
            zip_code="12345"
        )
        
        # Create a service
        self.service = Service.objects.create(
            name="Test Service",
            description="A service for testing",
            price=Decimal('100.00'),
            charge_type='fixed'
        )
        
        # Create a customer service
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
    
    def test_basic_attributes(self):
        """Test basic attributes of CustomerService."""
        self.assertEqual(self.customer_service.customer, self.customer)
        self.assertEqual(self.customer_service.service, self.service)
        self.assertEqual(self.customer_service.unit_price, Decimal('99.99'))
    
    def test_string_representation(self):
        """Test string representation of CustomerService."""
        expected = f"{self.customer} - {self.service}"
        self.assertEqual(str(self.customer_service), expected)
    
class TestCustomerServiceViewModel(TestCase):
    """Test case for the CustomerServiceView model."""
    
    def test_model_options(self):
        """Test the model options of CustomerServiceView."""
        self.assertFalse(CustomerServiceView._meta.managed)
        self.assertEqual(CustomerServiceView._meta.db_table, 'customer_services_customerserviceview')