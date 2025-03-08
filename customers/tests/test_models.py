import pytest
from django.test import TestCase, modify_settings, override_settings
from customers.models import Customer
from customers.tests.factories import CustomerFactory

# Override settings to test only customers app
@modify_settings(INSTALLED_APPS={'remove': [
    'orders',  # Remove orders app to avoid materialized view issues
]})
@pytest.mark.unit


@pytest.mark.unit
class CustomerModelTests(TestCase):
    """Test suite for the Customer model."""
    
    def test_customer_creation(self):
        """Test that a customer can be created with factory."""
        customer = CustomerFactory()
        self.assertIsNotNone(customer.id)
        self.assertTrue(isinstance(customer, Customer))
    
    def test_string_representation(self):
        """Test the string representation of a customer."""
        customer = CustomerFactory(company_name="Test Company")
        self.assertEqual(str(customer), "Test Company")
    
    def test_default_active_status(self):
        """Test that customers are active by default."""
        customer = CustomerFactory()
        self.assertTrue(customer.is_active)
    
    def test_search_by_company_name(self):
        """Test searching customers by company name."""
        # Create test customers
        CustomerFactory(company_name="ABC Corp")
        CustomerFactory(company_name="XYZ Inc")
        CustomerFactory(company_name="ABC Solutions")
        
        # Search for customers with 'ABC' in the name
        results = Customer.objects.filter(company_name__icontains="ABC")
        self.assertEqual(results.count(), 2)
        self.assertIn("ABC Corp", [c.company_name for c in results])
        self.assertIn("ABC Solutions", [c.company_name for c in results])
    
    def test_search_by_legal_name(self):
        """Test searching customers by legal business name."""
        # Create test customers
        CustomerFactory(legal_business_name="Smith Holdings LLC")
        CustomerFactory(legal_business_name="Smith Enterprises LLC")
        CustomerFactory(legal_business_name="Jones Incorporated LLC")
        
        # Search for customers with 'Smith' in the legal business name
        results = Customer.objects.filter(legal_business_name__icontains="Smith")
        self.assertEqual(results.count(), 2)
        self.assertIn("Smith Holdings LLC", [c.legal_business_name for c in results])
        self.assertIn("Smith Enterprises LLC", [c.legal_business_name for c in results])
    
    def test_filter_by_country(self):
        """Test filtering customers by country."""
        # Create test customers
        CustomerFactory(country="US")
        CustomerFactory(country="US")
        CustomerFactory(country="CA")
        CustomerFactory(country="UK")
        
        # Filter for US customers
        us_customers = Customer.objects.filter(country="US")
        ca_customers = Customer.objects.filter(country="CA")
        uk_customers = Customer.objects.filter(country="UK")
        
        self.assertEqual(us_customers.count(), 2)
        self.assertEqual(ca_customers.count(), 1)
        self.assertEqual(uk_customers.count(), 1)
    
    def test_filter_by_active_status(self):
        """Test filtering customers by active status."""
        # Create test customers
        CustomerFactory(is_active=True)
        CustomerFactory(is_active=True)
        CustomerFactory(is_active=False)
        
        # Filter by active status
        active_customers = Customer.objects.filter(is_active=True)
        inactive_customers = Customer.objects.filter(is_active=False)
        
        self.assertEqual(active_customers.count(), 2)
        self.assertEqual(inactive_customers.count(), 1)