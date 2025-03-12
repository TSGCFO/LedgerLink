# customer_services/tests.py
from django.test import TestCase
from django.db import IntegrityError
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import CustomerService, CustomerServiceView
from customers.models import Customer
from services.models import Service
from products.models import Product


class CustomerServiceModelTest(TestCase):
    """Test case for the CustomerService model using Django's TestCase."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com",
            phone="123-456-7890",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345"
        )
        
        self.service = Service.objects.create(
            name="Test Service",
            description="Test service description",
            price=Decimal('100.00'),
            charge_type='fixed'
        )
        
        self.product1 = Product.objects.create(
            customer=self.customer,
            sku="TEST-SKU-1",
            description="Test product 1",
            upc="123456789012"
        )
        
        self.product2 = Product.objects.create(
            customer=self.customer,
            sku="TEST-SKU-2",
            description="Test product 2",
            upc="123456789013"
        )
        
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
    def test_customer_service_creation(self):
        """Test that a customer service can be created with valid data."""
        self.assertEqual(self.customer_service.customer, self.customer)
        self.assertEqual(self.customer_service.service, self.service)
        self.assertEqual(self.customer_service.unit_price, Decimal('99.99'))
        self.assertIsNotNone(self.customer_service.created_at)
        self.assertIsNotNone(self.customer_service.updated_at)
    
    def test_str_representation(self):
        """Test the __str__ method returns the expected string."""
        expected_str = f"{self.customer} - {self.service}"
        self.assertEqual(str(self.customer_service), expected_str)
    
    def test_unique_constraint(self):
        """Test that a customer can only have one instance of a service."""
        with self.assertRaises(IntegrityError):
            CustomerService.objects.create(
                customer=self.customer,
                service=self.service,
                unit_price=Decimal('149.99')
            )
    
    def test_get_skus_method(self):
        """Test the get_skus method returns the expected SKUs."""
        # Add SKUs to the customer service
        self.customer_service.skus.add(self.product1, self.product2)
        
        skus = self.customer_service.get_skus()
        self.assertEqual(len(skus), 2)
        self.assertIn(self.product1, skus)
        self.assertIn(self.product2, skus)
    
    def test_get_sku_list_method(self):
        """Test the get_sku_list method returns the expected SKU strings."""
        # Add SKUs to the customer service
        self.customer_service.skus.add(self.product1, self.product2)
        
        sku_list = self.customer_service.get_sku_list()
        self.assertEqual(len(sku_list), 2)
        self.assertIn("TEST-SKU-1", sku_list)
        self.assertIn("TEST-SKU-2", sku_list)


class CustomerServiceViewTest(TestCase):
    """Tests for the CustomerServiceView model."""
    
    def test_view_is_unmanaged(self):
        """Test that the view model is unmanaged (no database table creation)."""
        self.assertFalse(CustomerServiceView._meta.managed)
    
    def test_db_table_name(self):
        """Test that the view model uses the correct database table."""
        self.assertEqual(CustomerServiceView._meta.db_table, 'customer_services_customerserviceview')