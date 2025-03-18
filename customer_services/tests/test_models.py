"""
Unit tests for CustomerService models.
"""
import unittest
import psycopg2
import os
from decimal import Decimal
from datetime import datetime


# Import our factory test pattern
from test_scripts.factory_test import (
    ModelFactory, 
    CustomerFactory, 
    ServiceFactory, 
    CustomerServiceFactory
)


class TestCustomerServiceModel(unittest.TestCase):
    """Test CustomerService model behavior."""
    
    def setUp(self):
        """Set up test data using factories."""
        # Connect to database
        self.conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'db'),
            database=os.environ.get('DB_NAME', 'ledgerlink_test'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        self.conn.autocommit = True
        
        # Initialize factories
        self.customer_factory = CustomerFactory(self.conn)
        self.service_factory = ServiceFactory(self.conn)
        self.cs_factory = CustomerServiceFactory(self.conn)
        
        # Clear existing data
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        
        # Create test data
        self.customer = self.customer_factory.create(
            company_name="Test Company",
            legal_business_name="Legal Test Company",
            email="test@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.service = self.service_factory.create(
            name="Test Service",
            description="Test Description",
            price=Decimal('100.00'),
            charge_type="fixed"
        )

    def test_create_customer_service(self):
        """Test creating a CustomerService with valid data."""
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Verify with database query
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT customer_id, service_id, unit_price 
            FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            result = cursor.fetchone()
        
        self.assertEqual(result[0], self.customer['id'])
        self.assertEqual(result[1], self.service['id'])
        self.assertEqual(Decimal(result[2]), Decimal('99.99'))
    
    def test_unique_constraint(self):
        """Test that (customer_id, service_id) has a unique constraint."""
        # Create first instance
        self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Try to create a duplicate
        with self.assertRaises(Exception):
            self.cs_factory.create(
                customer=self.customer,
                service=self.service,
                unit_price=Decimal('149.99')
            )
    
    def test_update_customer_service(self):
        """Test updating a CustomerService."""
        # Create instance
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Update unit_price
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE customer_services_customerservice
            SET unit_price = %s
            WHERE id = %s
            """, (Decimal('149.99'), cs['id']))
            
            # Verify update
            cursor.execute("""
            SELECT unit_price FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            result = cursor.fetchone()
        
        self.assertEqual(Decimal(result[0]), Decimal('149.99'))
    
    def test_delete_customer_service(self):
        """Test deleting a CustomerService."""
        # Create instance
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Delete
        with self.conn.cursor() as cursor:
            cursor.execute("""
            DELETE FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            
            # Verify deletion
            cursor.execute("""
            SELECT COUNT(*) FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            count = cursor.fetchone()[0]
        
        self.assertEqual(count, 0)
    
    def test_zero_unit_price(self):
        """Test CustomerService with zero unit_price."""
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('0.00')
        )
        
        # Verify with database query
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT unit_price FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            result = cursor.fetchone()
        
        self.assertEqual(Decimal(result[0]), Decimal('0.00'))
    
    def test_negative_unit_price(self):
        """Test CustomerService with negative unit_price."""
        # This should be allowed at the database level but might be
        # restricted by application logic
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('-10.00')
        )
        
        # Verify with database query
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT unit_price FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            result = cursor.fetchone()
        
        self.assertEqual(Decimal(result[0]), Decimal('-10.00'))
    
    def test_extremely_large_unit_price(self):
        """Test CustomerService with a very large unit_price."""
        large_price = Decimal('9999999.99')
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=large_price
        )
        
        # Verify with database query
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT unit_price FROM customer_services_customerservice
            WHERE id = %s
            """, (cs['id'],))
            result = cursor.fetchone()
        
        self.assertEqual(Decimal(result[0]), large_price)
    
    def tearDown(self):
        """Clean up test data."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        self.conn.close()


if __name__ == '__main__':
    unittest.main()