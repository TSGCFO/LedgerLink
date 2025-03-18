import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

from django.db import connection
from django.test import TransactionTestCase
from django.db.models import Q

from customers.models import Customer
from customers.tests.factories import CustomerFactory


@pytest.mark.performance
class CustomerPerformanceTests(TransactionTestCase):
    """Performance tests for Customer model queries."""
    
    def setUp(self):
        """Set up performance tests with a large number of customers."""
        # Create a controlled number of customers for consistent testing
        self.customer_count = 100  # Adjust based on your needs
        self.customers = [CustomerFactory() for _ in range(self.customer_count)]
        
        # Create customers with specific parameters for search testing
        for i in range(10):
            CustomerFactory(company_name=f"Test Company {i}")
            CustomerFactory(legal_business_name=f"Test Legal Name {i}")
            CustomerFactory(email=f"test{i}@example.com")
        
        # Reset connection to simulate real-world usage
        connection.close()
    
    def test_customer_retrieve_performance(self):
        """Test the performance of retrieving a customer by ID."""
        # Get a specific customer ID
        customer_id = self.customers[0].id
        
        # Measure time to retrieve the customer
        start_time = time.time()
        Customer.objects.get(id=customer_id)
        end_time = time.time()
        
        # The retrieval should be very fast (under 10ms)
        self.assertLess(end_time - start_time, 0.01, "Customer retrieval by ID took too long")
    
    def test_customer_search_performance(self):
        """Test the performance of searching customers by criteria."""
        # Measure time to search by company name
        start_time = time.time()
        customers = Customer.objects.filter(company_name__icontains="Test Company")
        end_time = time.time()
        search_time = end_time - start_time
        
        # Ensure we found the expected customers
        self.assertEqual(customers.count(), 10)
        
        # The search should be reasonably fast (under 50ms for 100 customers)
        self.assertLess(search_time, 0.05, "Customer search by company name took too long")
    
    def test_complex_query_performance(self):
        """Test the performance of complex customer queries."""
        # Measure time for a more complex query with multiple conditions
        start_time = time.time()
        customers = Customer.objects.filter(
            Q(company_name__icontains="Test") | 
            Q(legal_business_name__icontains="Legal") |
            Q(email__icontains="test")
        )
        end_time = time.time()
        query_time = end_time - start_time
        
        # The query should be reasonably fast (under 100ms)
        self.assertLess(query_time, 0.1, "Complex customer query took too long")
    
    def test_filtered_listing_performance(self):
        """Test the performance of filtered customer listings."""
        # Measure time to get active customers (filtering)
        start_time = time.time()
        customers = Customer.objects.filter(is_active=True)
        end_time = time.time()
        filter_time = end_time - start_time
        
        # The filtered listing should be reasonably fast (under 50ms)
        self.assertLess(filter_time, 0.05, "Filtered customer listing took too long")
    
    def test_bulk_operation_performance(self):
        """Test the performance of bulk operations."""
        # Prepare data for bulk creation
        bulk_data = [
            Customer(
                company_name=f"Bulk Company {i}",
                legal_business_name=f"Bulk Legal Name {i}",
                email=f"bulk{i}@example.com"
            ) for i in range(50)
        ]
        
        # Measure time for bulk creation
        start_time = time.time()
        Customer.objects.bulk_create(bulk_data)
        end_time = time.time()
        bulk_time = end_time - start_time
        
        # Bulk creation should be faster than individual creations
        # For 50 records, it should be under 100ms
        self.assertLess(bulk_time, 0.1, "Bulk customer creation took too long")
    
    def test_concurrent_access_performance(self):
        """Test the performance of concurrent customer access."""
        customer_ids = [c.id for c in self.customers[:10]]  # Take 10 customers to query
        
        def query_customer(customer_id):
            """Query a customer by ID."""
            customer = Customer.objects.get(id=customer_id)
            return customer is not None
        
        # Measure time for concurrent access
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(query_customer, customer_ids))
        end_time = time.time()
        
        # All queries should have succeeded
        self.assertTrue(all(results))
        
        # Concurrent access should be reasonably performant
        # For 10 concurrent queries, it should be under 100ms
        self.assertLess(end_time - start_time, 0.1, "Concurrent customer access took too long")
    
    def test_index_effectiveness(self):
        """Test the effectiveness of database indexes."""
        # Django's ORM doesn't expose query execution plans,
        # but we can measure the time difference between indexed and non-indexed fields
        
        # Get a customer email (indexed field)
        email = self.customers[0].email
        
        # Measure time to query by email (indexed)
        start_time = time.time()
        Customer.objects.filter(email=email).exists()
        indexed_time = time.time() - start_time
        
        # Measure time to query by phone (non-indexed)
        phone = self.customers[0].phone if self.customers[0].phone else "555-1234"
        start_time = time.time()
        Customer.objects.filter(phone=phone).exists()
        non_indexed_time = time.time() - start_time
        
        # The indexed query should generally be faster
        # This is a heuristic test and may not always be true depending on the database state
        self.assertLessEqual(indexed_time, non_indexed_time * 2, 
                          "Indexed field query should be faster than non-indexed field")
    
    def test_query_with_select_related_performance(self):
        """
        Test the performance of queries that use select_related for foreign keys.
        
        Note: This test is included for completeness but may be skipped since
        Customer doesn't have foreign keys in its basic model.
        """
        # This could be relevant if Customer gets relations in the future
        self.skipTest("Customer model doesn't have foreign keys to test select_related")