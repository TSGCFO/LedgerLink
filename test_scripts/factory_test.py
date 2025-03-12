#!/usr/bin/env python
"""
Factory-style test for customer_services that works without Django's ORM.
Uses a factory pattern manually implemented for creating test data.
"""
import os
import sys
import unittest
import psycopg2
from decimal import Decimal
from datetime import datetime


class ModelFactory:
    """Base factory for creating database records."""
    
    def __init__(self, connection, table_name):
        self.conn = connection
        self.table_name = table_name
        self.sequence = 0
    
    def get_next_sequence(self):
        """Get the next sequence number."""
        self.sequence += 1
        return self.sequence
    
    def create(self, **kwargs):
        """Create a record with the given attributes."""
        raise NotImplementedError("Subclasses must implement this method")


class CustomerFactory(ModelFactory):
    """Factory for Customer records."""
    
    def __init__(self, connection):
        super().__init__(connection, "customers_customer")
    
    def create(self, **kwargs):
        """Create a customer record."""
        # Default values
        data = {
            "company_name": f"Test Company {self.get_next_sequence()}",
            "legal_business_name": f"Legal Test Company {self.get_next_sequence()}",
            "email": f"test{self.get_next_sequence()}@example.com",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Override with provided values
        data.update(kwargs)
        
        # Insert into database
        with self.conn.cursor() as cursor:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            
            query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders}) RETURNING id
            """
            
            cursor.execute(query, list(data.values()))
            record_id = cursor.fetchone()[0]
            
            # Return a dictionary representing the created record
            return {"id": record_id, **data}


class ServiceFactory(ModelFactory):
    """Factory for Service records."""
    
    def __init__(self, connection):
        super().__init__(connection, "services_service")
    
    def create(self, **kwargs):
        """Create a service record."""
        # Default values
        seq = self.get_next_sequence()
        data = {
            "name": f"Test Service {seq}",
            "description": f"Description for service {seq}",
            "price": Decimal(f"{100 + seq}.99"),
            "charge_type": "fixed"
        }
        
        # Override with provided values
        data.update(kwargs)
        
        # Insert into database
        with self.conn.cursor() as cursor:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            
            query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders}) RETURNING id
            """
            
            cursor.execute(query, list(data.values()))
            record_id = cursor.fetchone()[0]
            
            # Return a dictionary representing the created record
            return {"id": record_id, **data}


class CustomerServiceFactory(ModelFactory):
    """Factory for CustomerService records."""
    
    def __init__(self, connection):
        super().__init__(connection, "customer_services_customerservice")
    
    def create(self, **kwargs):
        """Create a customer service record."""
        # Default values
        seq = self.get_next_sequence()
        data = {
            "unit_price": Decimal(f"{99 + seq}.99"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Handle relationships
        if "customer" in kwargs:
            customer = kwargs.pop("customer")
            data["customer_id"] = customer["id"]
        
        if "service" in kwargs:
            service = kwargs.pop("service")
            data["service_id"] = service["id"]
        
        # Override with any remaining values
        data.update(kwargs)
        
        # Insert into database
        with self.conn.cursor() as cursor:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            
            query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders}) RETURNING id
            """
            
            cursor.execute(query, list(data.values()))
            record_id = cursor.fetchone()[0]
            
            # Return a dictionary representing the created record
            return {"id": record_id, **data}


class CustomerServiceTest(unittest.TestCase):
    """Test CustomerService using factory pattern."""
    
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
        
        # Ensure tables exist
        self._ensure_tables_exist()
        
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
        self.customer = self.customer_factory.create()
        self.service = self.service_factory.create()
    
    def _ensure_tables_exist(self):
        """Ensure tables exist by checking and creating if needed."""
        with self.conn.cursor() as cursor:
            # Check if tables exist
            cursor.execute("SELECT to_regclass('customers_customer')")
            customers_exists = cursor.fetchone()[0] is not None
            
            cursor.execute("SELECT to_regclass('services_service')")
            services_exists = cursor.fetchone()[0] is not None
            
            cursor.execute("SELECT to_regclass('customer_services_customerservice')")
            cs_exists = cursor.fetchone()[0] is not None
            
            # Get actual schema information
            if customers_exists:
                cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'customers_customer'
                """)
                columns = [row[0] for row in cursor.fetchall()]
                print(f"Customer columns: {columns}")
            
            # Create tables if needed
            if not customers_exists:
                print("Creating customers_customer table...")
                cursor.execute("""
                CREATE TABLE customers_customer (
                    id SERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    legal_business_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(255),
                    address VARCHAR(255),
                    city VARCHAR(255),
                    state VARCHAR(255),
                    zip VARCHAR(255),
                    country VARCHAR(255),
                    business_type VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
                )
                """)
            
            if not services_exists:
                print("Creating services_service table...")
                cursor.execute("""
                CREATE TABLE services_service (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    charge_type VARCHAR(50) DEFAULT 'fixed'
                )
                """)
            
            if not cs_exists:
                print("Creating customer_services_customerservice table...")
                cursor.execute("""
                CREATE TABLE customer_services_customerservice (
                    id SERIAL PRIMARY KEY,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    customer_id INTEGER REFERENCES customers_customer(id),
                    service_id INTEGER REFERENCES services_service(id),
                    CONSTRAINT unique_customer_service UNIQUE (customer_id, service_id)
                )
                """)
    
    def test_customer_service_creation(self):
        """Test creating a CustomerService."""
        # Create using factory
        cs = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Verify creation
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT customer_id, service_id, unit_price FROM customer_services_customerservice
            WHERE id = %s
            """, (cs["id"],))
            result = cursor.fetchone()
            
            self.assertEqual(result[0], self.customer["id"])
            self.assertEqual(result[1], self.service["id"])
            self.assertEqual(float(result[2]), 99.99)
    
    def test_unique_constraint(self):
        """Test the unique constraint on customer and service."""
        # Create first CS
        self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):
            self.cs_factory.create(
                customer=self.customer,
                service=self.service,
                unit_price=Decimal('149.99')
            )
    
    def tearDown(self):
        """Clean up test data."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        self.conn.close()


if __name__ == '__main__':
    print("Running CustomerService tests with factory pattern...")
    unittest.main()