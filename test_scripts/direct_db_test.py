#!/usr/bin/env python
"""
A direct database test that uses pure psycopg2 to test the database schema
without depending on Django's ORM or migrations.
"""
import os
import sys
import unittest
import psycopg2
from decimal import Decimal
from datetime import datetime

class DirectDBTest(unittest.TestCase):
    """Test database operations directly with psycopg2."""
    
    def setUp(self):
        """Set up test connection and create tables if needed."""
        print("Setting up test database...")
        
        # Connect to database
        self.conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'db'),
            database=os.environ.get('DB_NAME', 'ledgerlink_test'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        self.conn.autocommit = True  # Needed for CREATE TABLE
        
        # Create tables if they don't exist
        with self.conn.cursor() as cursor:
            # Create customers table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers_customer (
                id SERIAL PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                contact_name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(255)
            )
            """)
            
            # Create services table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS services_service (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                charge_type VARCHAR(50) DEFAULT 'fixed'
            )
            """)
            
            # Create customer_services table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_services_customerservice (
                id SERIAL PRIMARY KEY,
                unit_price DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                customer_id INTEGER REFERENCES customers_customer(id),
                service_id INTEGER REFERENCES services_service(id),
                CONSTRAINT unique_customer_service UNIQUE (customer_id, service_id)
            )
            """)
        
        # Get actual schema information
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'customers_customer'
            """)
            customer_columns = [row[0] for row in cursor.fetchall()]
            print(f"Customer columns: {customer_columns}")
            
            cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'services_service'
            """)
            service_columns = [row[0] for row in cursor.fetchall()]
            print(f"Service columns: {service_columns}")
        
        # Insert test data
        with self.conn.cursor() as cursor:
            # Clear existing data
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
            
            # Insert a customer with all required fields
            cursor.execute("""
            INSERT INTO customers_customer (company_name, legal_business_name, email, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW()) RETURNING id
            """, ('Test Company', 'Legal Test Company', 'test@example.com'))
            self.customer_id = cursor.fetchone()[0]
            
            # Insert a service
            cursor.execute("""
            INSERT INTO services_service (name, description, price, charge_type)
            VALUES (%s, %s, %s, %s) RETURNING id
            """, ('Test Service', 'Test service description', 100.00, 'fixed'))
            self.service_id = cursor.fetchone()[0]
    
    def test_customer_service_creation(self):
        """Test creating a customer service."""
        # Insert a customer service
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO customer_services_customerservice 
            (customer_id, service_id, unit_price)
            VALUES (%s, %s, %s) RETURNING id
            """, (self.customer_id, self.service_id, 99.99))
            cs_id = cursor.fetchone()[0]
            
            # Verify the record was created
            cursor.execute("""
            SELECT customer_id, service_id, unit_price FROM customer_services_customerservice
            WHERE id = %s
            """, (cs_id,))
            result = cursor.fetchone()
            
            self.assertEqual(result[0], self.customer_id)
            self.assertEqual(result[1], self.service_id)
            self.assertEqual(float(result[2]), 99.99)
    
    def test_unique_constraint(self):
        """Test the unique constraint on customer and service."""
        # Insert a customer service
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO customer_services_customerservice 
            (customer_id, service_id, unit_price)
            VALUES (%s, %s, %s)
            """, (self.customer_id, self.service_id, 99.99))
            
            # Try to insert a duplicate
            try:
                cursor.execute("""
                INSERT INTO customer_services_customerservice 
                (customer_id, service_id, unit_price)
                VALUES (%s, %s, %s)
                """, (self.customer_id, self.service_id, 149.99))
                self.fail("Expected a unique constraint violation")
            except psycopg2.IntegrityError:
                # This is expected
                pass
    
    def tearDown(self):
        """Clean up after tests."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        self.conn.close()


if __name__ == '__main__':
    print("Running direct database tests...")
    unittest.main()