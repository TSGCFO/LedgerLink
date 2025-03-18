"""
Unit tests for Order models using direct database access.
This approach is more reliable for PostgreSQL-specific features.
"""
import unittest
import psycopg2
import os
from decimal import Decimal
from datetime import datetime


class TestOrderModelDirectDB(unittest.TestCase):
    """Test Order model behavior with direct database access."""
    
    def setUp(self):
        """Set up test data using direct database connection."""
        # Connect to database
        self.conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'db'),
            database=os.environ.get('DB_NAME', 'ledgerlink_test'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        self.conn.autocommit = True
        
        # Clear existing data
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM orders_order")
            cursor.execute("DELETE FROM customers_customer")
        
        # Create test customer
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO customers_customer 
            (company_name, legal_business_name, email, phone, address, city, state, zip, country, is_active, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (
                "Test Company Direct DB",
                "Test Company Direct DB LLC",
                "directdb@example.com",
                "555-1234",
                "123 Test St",
                "Test City",
                "TS",
                "12345",
                "US",
                True,
                datetime.now(),
                datetime.now()
            ))
            self.customer_id = cursor.fetchone()[0]

    def test_create_order(self):
        """Test creating an Order with direct SQL."""
        # Create an order
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO orders_order
            (transaction_id, customer_id, reference_number, status, priority, sku_quantity, total_item_qty, line_items)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                99999,
                self.customer_id,
                "REF-DIRECT-DB",
                "draft",
                "medium",
                '{"SKU1": 10, "SKU2": 5}',
                15,
                2
            ))
            
            # Verify with database query
            cursor.execute("""
            SELECT transaction_id, customer_id, reference_number, status, priority
            FROM orders_order
            WHERE transaction_id = %s
            """, (99999,))
            result = cursor.fetchone()
        
        self.assertEqual(result[0], 99999)  # transaction_id
        self.assertEqual(result[1], self.customer_id)  # customer_id
        self.assertEqual(result[2], "REF-DIRECT-DB")  # reference_number
        self.assertEqual(result[3], "draft")  # status
        self.assertEqual(result[4], "medium")  # priority
    
    def test_update_order(self):
        """Test updating an Order with direct SQL."""
        # Create an order first
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO orders_order
            (transaction_id, customer_id, reference_number, status, priority)
            VALUES (%s, %s, %s, %s, %s)
            """, (
                88888,
                self.customer_id,
                "REF-UPDATE",
                "draft",
                "low"
            ))
            
            # Update the order
            cursor.execute("""
            UPDATE orders_order
            SET status = %s, priority = %s
            WHERE transaction_id = %s
            """, ("submitted", "high", 88888))
            
            # Verify the update
            cursor.execute("""
            SELECT status, priority FROM orders_order
            WHERE transaction_id = %s
            """, (88888,))
            result = cursor.fetchone()
        
        self.assertEqual(result[0], "submitted")
        self.assertEqual(result[1], "high")
    
    def test_delete_order(self):
        """Test deleting an Order with direct SQL."""
        # Create an order first
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO orders_order
            (transaction_id, customer_id, reference_number)
            VALUES (%s, %s, %s)
            """, (
                77777,
                self.customer_id,
                "REF-DELETE"
            ))
            
            # Delete the order
            cursor.execute("""
            DELETE FROM orders_order
            WHERE transaction_id = %s
            """, (77777,))
            
            # Verify deletion
            cursor.execute("""
            SELECT COUNT(*) FROM orders_order
            WHERE transaction_id = %s
            """, (77777,))
            count = cursor.fetchone()[0]
        
        self.assertEqual(count, 0)
    
    def test_json_field(self):
        """Test the JSON field (sku_quantity) with direct SQL."""
        # Create an order with JSON data
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO orders_order
            (transaction_id, customer_id, reference_number, sku_quantity)
            VALUES (%s, %s, %s, %s::jsonb)
            """, (
                66666,
                self.customer_id,
                "REF-JSON",
                '{"SKU1": 5, "SKU2": 10, "SKU3": 15}'
            ))
            
            # Query the JSON data
            cursor.execute("""
            SELECT sku_quantity FROM orders_order
            WHERE transaction_id = %s
            """, (66666,))
            json_data = cursor.fetchone()[0]
        
        self.assertEqual(json_data["SKU1"], 5)
        self.assertEqual(json_data["SKU2"], 10)
        self.assertEqual(json_data["SKU3"], 15)
    
    def tearDown(self):
        """Clean up test data."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM orders_order")
            cursor.execute("DELETE FROM customers_customer WHERE id = %s", (self.customer_id,))
        self.conn.close()


if __name__ == '__main__':
    unittest.main()