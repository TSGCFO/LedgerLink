import pytest
from django.test import TestCase, modify_settings, override_settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import connection

from customers.models import Customer
from customers.tests.factories import CustomerFactory

# Override settings to test only customers app
@modify_settings(INSTALLED_APPS={'remove': [
    'orders',  # Remove orders app to avoid materialized view issues
]})
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
    
    def test_email_uniqueness_constraint(self):
        """Test email uniqueness constraint."""
        # Create a customer with a specific email
        email = "unique@example.com"
        CustomerFactory(email=email)
        
        # Attempt to create another customer with the same email
        with self.assertRaises(IntegrityError):
            CustomerFactory(email=email)
    
    def test_required_fields(self):
        """Test that required fields cannot be null."""
        # Create a customer with the factory
        customer = CustomerFactory()
        
        # Try to set required fields to None
        customer.company_name = None
        customer.legal_business_name = None
        customer.email = None
        
        # Should raise ValidationError when saving
        with self.assertRaises(ValidationError):
            customer.full_clean()
    
    def test_non_required_fields(self):
        """Test that non-required fields can be null."""
        # Create a customer with non-required fields set to None
        customer = CustomerFactory(
            phone=None,
            address=None,
            city=None,
            state=None,
            zip=None,
            country=None,
            business_type=None
        )
        
        # Should save successfully
        customer.full_clean()
        customer.save()
        
        # Retrieve from database to verify
        db_customer = Customer.objects.get(id=customer.id)
        self.assertIsNone(db_customer.phone)
        self.assertIsNone(db_customer.address)
        self.assertIsNone(db_customer.city)
        self.assertIsNone(db_customer.state)
        self.assertIsNone(db_customer.zip)
        self.assertIsNone(db_customer.country)
        self.assertIsNone(db_customer.business_type)
    
    def test_auto_timestamps(self):
        """Test that created_at and updated_at are automatically set."""
        customer = CustomerFactory()
        
        # Timestamps should be set
        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)
        
        # Initially, created_at and updated_at should be the same
        self.assertEqual(customer.created_at, customer.updated_at)
        
        # After updating, updated_at should change but created_at should not
        original_created_at = customer.created_at
        original_updated_at = customer.updated_at
        
        # Wait a short period to ensure time difference
        import time
        time.sleep(0.001)
        
        # Update the customer
        customer.company_name = "Updated Company Name"
        customer.save()
        
        # created_at should remain the same, updated_at should change
        self.assertEqual(customer.created_at, original_created_at)
        self.assertNotEqual(customer.updated_at, original_updated_at)
    
    def test_field_max_lengths(self):
        """Test that field max_lengths are enforced."""
        # Create a customer with field values at max length
        customer = Customer(
            company_name="X" * 100,  # Max length 100
            legal_business_name="X" * 100,  # Max length 100
            email="x" * 245 + "@example.com",  # Max length 254
            phone="X" * 20,  # Max length 20
            address="X" * 200,  # Max length 200
            city="X" * 50,  # Max length 50
            state="X" * 50,  # Max length 50
            zip="X" * 20,  # Max length 20
            country="X" * 50,  # Max length 50
            business_type="X" * 50  # Max length 50
        )
        
        # Should validate successfully
        customer.full_clean()
        
        # Create a customer with field values exceeding max length
        customer = Customer(
            company_name="X" * 101,  # Exceeds max length
            legal_business_name="X" * 100,
            email="test@example.com",
            phone="X" * 20,
            address="X" * 200,
            city="X" * 50,
            state="X" * 50,
            zip="X" * 20,
            country="X" * 50,
            business_type="X" * 50
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            customer.full_clean()
    
    def test_index_creation(self):
        """Test that indexes are created properly."""
        # Get table information from the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'customers_customer'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
        
        # Check that indexes exist
        self.assertIn('company_name_idx', indexes)
        self.assertIn('email_idx', indexes)