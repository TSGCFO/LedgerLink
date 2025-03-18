"""
Performance tests for CustomerService.
Tests system performance under various conditions.
"""
import unittest
import psycopg2
import os
import time
import statistics
from decimal import Decimal
from datetime import datetime
import concurrent.futures

# Import our factory test pattern
from test_scripts.factory_test import (
    ModelFactory, 
    CustomerFactory, 
    ServiceFactory, 
    CustomerServiceFactory
)


class TestCustomerServicePerformance(unittest.TestCase):
    """Test CustomerService performance characteristics."""
    
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
        
        # Create base test data - a single customer with multiple services
        self.customer = self.customer_factory.create(
            company_name="Performance Test Company",
            legal_business_name="Performance Legal Company",
            email="performance@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create multiple services
        self.services = []
        for i in range(5):
            service = self.service_factory.create(
                name=f"Performance Service {i}",
                description=f"Service {i} for performance testing",
                price=Decimal(f"{100 + i}.99"),
                charge_type="fixed" if i % 2 == 0 else "per_unit"
            )
            self.services.append(service)
    
    def _measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, (end_time - start_time) * 1000  # Return time in milliseconds
    
    def test_bulk_customer_service_creation(self):
        """Test performance of bulk creation of customer services."""
        # Number of customer services to create
        num_services = 50
        
        # Create a new customer for bulk testing
        bulk_customer = self.customer_factory.create(
            company_name="Bulk Test Company",
            legal_business_name="Bulk Legal Company",
            email="bulk@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create multiple services for bulk testing
        bulk_services = []
        for i in range(num_services):
            service = self.service_factory.create(
                name=f"Bulk Service {i}",
                description=f"Service {i} for bulk testing",
                price=Decimal(f"{100 + i}.99"),
                charge_type="fixed" if i % 2 == 0 else "per_unit"
            )
            bulk_services.append(service)
        
        # Measure time to create customer services one by one
        start_time = time.time()
        for service in bulk_services:
            self.cs_factory.create(
                customer=bulk_customer,
                service=service,
                unit_price=Decimal(f"{99 + (service['id'] % 10)}.99")
            )
        end_time = time.time()
        
        sequential_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Report results
        print(f"\nSequential creation of {num_services} customer services: {sequential_time:.2f}ms")
        print(f"Average time per customer service: {sequential_time / num_services:.2f}ms")
        
        # Verify reasonable performance - adjust threshold based on environment
        self.assertLess(sequential_time / num_services, 100, 
                        "Average creation time per customer service is too high")
    
    def test_customer_service_query_performance(self):
        """Test performance of querying customer services."""
        # Create a number of customer services for querying
        num_services = 100
        
        # Create customers for query testing
        customers = []
        for i in range(10):
            customer = self.customer_factory.create(
                company_name=f"Query Customer {i}",
                legal_business_name=f"Query Legal Company {i}",
                email=f"query{i}@example.com",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            customers.append(customer)
        
        # Create services for query testing
        services = []
        for i in range(num_services // 10):
            service = self.service_factory.create(
                name=f"Query Service {i}",
                description=f"Service {i} for query testing",
                price=Decimal(f"{100 + i}.99"),
                charge_type="fixed" if i % 2 == 0 else "per_unit"
            )
            services.append(service)
        
        # Create customer services for query testing
        # Distribute services across customers
        for i in range(num_services):
            customer = customers[i % 10]
            service = services[i % len(services)]
            self.cs_factory.create(
                customer=customer,
                service=service,
                unit_price=Decimal(f"{99 + (i % 10)}.99")
            )
        
        # Test query times for different query types
        query_times = {}
        
        # Test 1: Simple query by ID
        def query_by_id(service_id):
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT * FROM customer_services_customerservice
                WHERE id = %s
                """, (service_id,))
                return cursor.fetchone()
        
        _, query_times['by_id'] = self._measure_execution_time(
            query_by_id, num_services // 2
        )
        
        # Test 2: Query with customer join
        def query_with_customer_join(customer_id):
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT cs.*, c.company_name 
                FROM customer_services_customerservice cs
                JOIN customers_customer c ON cs.customer_id = c.id
                WHERE cs.customer_id = %s
                """, (customer_id,))
                return cursor.fetchall()
        
        _, query_times['customer_join'] = self._measure_execution_time(
            query_with_customer_join, customers[0]['id']
        )
        
        # Test 3: Query with multiple joins
        def query_with_multiple_joins():
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT cs.*, c.company_name, s.name as service_name
                FROM customer_services_customerservice cs
                JOIN customers_customer c ON cs.customer_id = c.id
                JOIN services_service s ON cs.service_id = s.id
                WHERE s.charge_type = 'fixed'
                """)
                return cursor.fetchall()
        
        _, query_times['multiple_joins'] = self._measure_execution_time(
            query_with_multiple_joins
        )
        
        # Test 4: Query with aggregation
        def query_with_aggregation():
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT c.company_name, COUNT(cs.id) as service_count, 
                       SUM(cs.unit_price) as total_price
                FROM customer_services_customerservice cs
                JOIN customers_customer c ON cs.customer_id = c.id
                GROUP BY c.company_name
                ORDER BY total_price DESC
                """)
                return cursor.fetchall()
        
        _, query_times['aggregation'] = self._measure_execution_time(
            query_with_aggregation
        )
        
        # Report results
        print("\nQuery Performance Results:")
        for query_type, time_ms in query_times.items():
            print(f"  {query_type}: {time_ms:.2f}ms")
        
        # Verify reasonable performance - adjust thresholds based on environment
        self.assertLess(query_times['by_id'], 50, 
                        "Simple ID query is too slow")
        self.assertLess(query_times['customer_join'], 100, 
                        "Customer join query is too slow")
        self.assertLess(query_times['multiple_joins'], 200, 
                        "Multiple join query is too slow")
        self.assertLess(query_times['aggregation'], 300, 
                        "Aggregation query is too slow")
    
    def test_concurrent_customer_service_operations(self):
        """Test performance of concurrent customer service operations."""
        # Number of concurrent operations
        num_concurrent = 10
        
        # Create a new customer for concurrent testing
        concurrent_customer = self.customer_factory.create(
            company_name="Concurrent Test Company",
            legal_business_name="Concurrent Legal Company",
            email="concurrent@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create services for concurrent testing
        concurrent_services = []
        for i in range(num_concurrent):
            service = self.service_factory.create(
                name=f"Concurrent Service {i}",
                description=f"Service {i} for concurrent testing",
                price=Decimal(f"{100 + i}.99"),
                charge_type="fixed" if i % 2 == 0 else "per_unit"
            )
            concurrent_services.append(service)
        
        # Define function for concurrent creation
        def create_customer_service(service):
            # Create a new connection for this thread
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'db'),
                database=os.environ.get('DB_NAME', 'ledgerlink_test'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'postgres')
            )
            conn.autocommit = True
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                    INSERT INTO customer_services_customerservice
                    (customer_id, service_id, unit_price, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    RETURNING id
                    """, (
                        concurrent_customer['id'],
                        service['id'],
                        Decimal(f"{99 + (service['id'] % 10)}.99")
                    ))
                    cs_id = cursor.fetchone()[0]
                    return cs_id
            finally:
                conn.close()
        
        # Measure time for concurrent operations
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = {executor.submit(create_customer_service, service): service 
                       for service in concurrent_services}
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"Thread error: {e}")
        end_time = time.time()
        
        concurrent_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Report results
        print(f"\nConcurrent creation of {num_concurrent} customer services: {concurrent_time:.2f}ms")
        print(f"Average time per operation: {concurrent_time / num_concurrent:.2f}ms")
        
        # Verify all operations completed successfully
        self.assertEqual(len(results), num_concurrent, 
                        "Not all concurrent operations completed successfully")
        
        # Verify reasonable performance - this will depend on environment
        # Here we're mainly checking that concurrent operations are faster than sequential
        # per operation, but this is a relative metric
        self.assertLess(concurrent_time / num_concurrent, 200, 
                        "Average concurrent operation time is too high")
    
    def tearDown(self):
        """Clean up test data."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        self.conn.close()


if __name__ == '__main__':
    unittest.main()