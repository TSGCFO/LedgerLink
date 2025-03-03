from django.test import TestCase
from customers.models import Customer
from products.models import Product
from django.db import connection
import pytest

class TestDatabaseSetup(TestCase):
    """Test that the database is set up correctly."""
    
    def test_table_creation(self):
        """Test that tables are created correctly."""
        # Check that the customer table exists and we can create records
        customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Legal Business Name",
            email="test@example.com"
        )
        self.assertEqual(customer.company_name, "Test Company")
        
        # Check that the product table exists and we can create records
        product = Product.objects.create(
            sku="TEST-SKU",
            customer=customer,
            labeling_unit_1="BOX",
            labeling_quantity_1=10
        )
        self.assertEqual(product.sku, "TEST-SKU")
        
        # Verify constraints
        with self.assertRaises(Exception):
            # Should fail due to unique constraint
            Product.objects.create(
                sku="TEST-SKU",
                customer=customer,
                labeling_unit_1="CASE",
                labeling_quantity_1=20
            )
        
        # List all tables in the database
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()
            print(f"Tables in database: {', '.join(tables)}")