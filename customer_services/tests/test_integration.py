"""
Integration tests for CustomerService.
Tests interactions with other components like billing system.
"""
import unittest
import psycopg2
import os
import json
from decimal import Decimal
from datetime import datetime

# Import our factory test pattern
from test_scripts.factory_test import (
    ModelFactory, 
    CustomerFactory, 
    ServiceFactory, 
    CustomerServiceFactory
)


class TestCustomerServiceIntegration(unittest.TestCase):
    """Test CustomerService integration with other components."""
    
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
            
            # Also delete from billing tables if they exist
            cursor.execute("SELECT to_regclass('billing_billingreport')")
            if cursor.fetchone()[0] is not None:
                cursor.execute("DELETE FROM billing_billingreport")
        
        # Create test data
        self.customer = self.customer_factory.create(
            company_name="Integration Test Company",
            legal_business_name="Legal Test Company",
            email="test@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create multiple services
        self.service1 = self.service_factory.create(
            name="Service 1",
            description="First Service",
            price=Decimal('100.00'),
            charge_type="fixed"
        )
        
        self.service2 = self.service_factory.create(
            name="Service 2",
            description="Second Service",
            price=Decimal('200.00'),
            charge_type="per_unit"
        )
        
        # Create customer services
        self.cs1 = self.cs_factory.create(
            customer=self.customer,
            service=self.service1,
            unit_price=Decimal('99.99')
        )
        
        self.cs2 = self.cs_factory.create(
            customer=self.customer,
            service=self.service2,
            unit_price=Decimal('199.99')
        )
        
        # Check if billing tables exist and create test billing report
        self._create_billing_tables_if_needed()
    
    def _create_billing_tables_if_needed(self):
        """Create billing tables if they don't exist."""
        with self.conn.cursor() as cursor:
            # Check if billing tables exist
            cursor.execute("SELECT to_regclass('billing_billingreport')")
            if cursor.fetchone()[0] is None:
                print("Creating billing_billingreport table for integration testing...")
                cursor.execute("""
                CREATE TABLE billing_billingreport (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers_customer(id),
                    total_amount DECIMAL(10, 2) NOT NULL,
                    details JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    created_by VARCHAR(255),
                    updated_by VARCHAR(255),
                    period_start DATE,
                    period_end DATE
                )
                """)
    
    def test_create_billing_report_from_customer_services(self):
        """Test creating a billing report from customer services."""
        # Calculate total amount from customer services
        total_amount = Decimal('99.99') + Decimal('199.99')
        
        # Create billing report details - mock what the billing system would do
        details = {
            "services": [
                {
                    "service_id": self.service1["id"],
                    "service_name": self.service1["name"],
                    "unit_price": float(Decimal('99.99')),
                    "quantity": 1,
                    "subtotal": float(Decimal('99.99'))
                },
                {
                    "service_id": self.service2["id"],
                    "service_name": self.service2["name"],
                    "unit_price": float(Decimal('199.99')),
                    "quantity": 1,
                    "subtotal": float(Decimal('199.99'))
                }
            ],
            "total": float(total_amount)
        }
        
        # Insert billing report
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO billing_billingreport (
                customer_id, total_amount, details, 
                created_at, updated_at, period_start, period_end
            )
            VALUES (%s, %s, %s, NOW(), NOW(), NOW(), NOW())
            RETURNING id
            """, (
                self.customer["id"], 
                total_amount,
                json.dumps(details)
            ))
            billing_id = cursor.fetchone()[0]
            
            # Verify the report was created
            cursor.execute("""
            SELECT customer_id, total_amount FROM billing_billingreport
            WHERE id = %s
            """, (billing_id,))
            result = cursor.fetchone()
        
        # Verify billing report
        self.assertEqual(result[0], self.customer["id"])
        self.assertEqual(Decimal(result[1]), total_amount)
    
    def test_query_customer_services_by_service_type(self):
        """Test querying customer services by service type."""
        # Create additional services and customer services
        service3 = self.service_factory.create(
            name="Service 3",
            description="Third Service",
            price=Decimal('300.00'),
            charge_type="fixed"  # Same as service1
        )
        
        cs3 = self.cs_factory.create(
            customer=self.customer,
            service=service3,
            unit_price=Decimal('299.99')
        )
        
        # Query customer services by charge_type
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT cs.id, s.charge_type 
            FROM customer_services_customerservice cs
            JOIN services_service s ON cs.service_id = s.id
            WHERE s.charge_type = %s AND cs.customer_id = %s
            """, ("fixed", self.customer["id"]))
            fixed_services = cursor.fetchall()
            
            cursor.execute("""
            SELECT cs.id, s.charge_type 
            FROM customer_services_customerservice cs
            JOIN services_service s ON cs.service_id = s.id
            WHERE s.charge_type = %s AND cs.customer_id = %s
            """, ("per_unit", self.customer["id"]))
            per_unit_services = cursor.fetchall()
        
        # We should have 2 fixed services (service1 and service3)
        self.assertEqual(len(fixed_services), 2)
        # And 1 per_unit service (service2)
        self.assertEqual(len(per_unit_services), 1)
        
        # Verify charge types
        for cs in fixed_services:
            self.assertEqual(cs[1], "fixed")
        
        for cs in per_unit_services:
            self.assertEqual(cs[1], "per_unit")
    
    def test_customer_services_total_calculation(self):
        """Test calculating total from customer services."""
        # Calculate total price
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT SUM(cs.unit_price)
            FROM customer_services_customerservice cs
            WHERE cs.customer_id = %s
            """, (self.customer["id"],))
            total = cursor.fetchone()[0]
        
        # Verify total
        expected_total = Decimal('99.99') + Decimal('199.99')
        self.assertEqual(Decimal(total), expected_total)
    
    def tearDown(self):
        """Clean up test data."""
        with self.conn.cursor() as cursor:
            # Delete billing data if it exists
            cursor.execute("SELECT to_regclass('billing_billingreport')")
            if cursor.fetchone()[0] is not None:
                cursor.execute("DELETE FROM billing_billingreport")
            
            # Delete customer services data
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        self.conn.close()


if __name__ == '__main__':
    unittest.main()