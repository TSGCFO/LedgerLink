#!/usr/bin/env python
"""
A direct test runner script for CustomerService models
that bypasses complex test environments and Django's test runner
"""
import os
import sys
import django
import unittest
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
os.environ['SKIP_MATERIALIZED_VIEWS'] = 'True'
django.setup()

# Import models
from django.db import connection
from customer_services.models import CustomerService 
from customers.models import Customer
from services.models import Service

class CustomerServiceTest(unittest.TestCase):
    """Direct tests for CustomerService"""
    
    def setUp(self):
        """Set up test data."""
        # Make sure tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('customer_services_customerservice')")
            if cursor.fetchone()[0] is None:
                print("Creating customer_services_customerservice table...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers_customer (
                    id SERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    contact_name VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(255)
                )
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS services_service (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL
                )
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_services_customerservice (
                    id SERIAL PRIMARY KEY,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    customer_id INTEGER REFERENCES customers_customer(id),
                    service_id INTEGER REFERENCES services_service(id),
                    CONSTRAINT unique_customer_service UNIQUE (customer_id, service_id)
                )
                """)
        
        # Create test data directly
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com",
            phone="123-456-7890"
        )
        
        self.service = Service.objects.create(
            name="Test Service",
            description="Test service description",
            price=Decimal('100.00')
        )
    
    def test_customer_service_creation(self):
        """Test that a customer service is created."""
        cs = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Retrieve the customer service by ID
        retrieved_cs = CustomerService.objects.get(id=cs.id)
        
        self.assertEqual(retrieved_cs.customer.id, self.customer.id)
        self.assertEqual(retrieved_cs.service.id, self.service.id)
        self.assertEqual(retrieved_cs.unit_price, Decimal('99.99'))
    
    def tearDown(self):
        """Clean up after tests."""
        CustomerService.objects.all().delete()
        Service.objects.all().delete()
        Customer.objects.all().delete()


if __name__ == '__main__':
    print("Running CustomerService tests directly...")
    unittest.main()