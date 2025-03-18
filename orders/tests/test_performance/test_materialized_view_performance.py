import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import random
from unittest import TestCase

from django.db import connection
from django.test import TransactionTestCase
from django.db.models import Q, Sum, Count

from orders.models import Order, OrderSKUView
from orders.tests.factories import OrderFactory, LargeOrderFactory
from customers.tests.factories import CustomerFactory

try:
    from django.core.management import call_command
except ImportError:
    call_command = None

@pytest.mark.performance
class OrderSKUViewPerformanceTests(TransactionTestCase):
    """Performance tests for OrderSKUView materialized view."""
    
    def setUp(self):
        """Set up performance tests with orders and SKUs."""
        # Create customers
        self.customers = [CustomerFactory() for _ in range(5)]
        
        # Create regular orders with varying SKUs
        self.regular_orders = []
        for i in range(20):  # Create 20 regular orders
            customer = self.customers[i % len(self.customers)]
            order = OrderFactory(
                customer=customer,
                reference_number=f"REG-{i:04d}",
                status=random.choice(['draft', 'submitted', 'shipped', 'delivered']),
                sku_quantity={f"SKU-{j:04d}": random.randint(1, 10) for j in range(5)}
            )
            self.regular_orders.append(order)
        
        # Create some large orders with many SKUs
        self.large_orders = []
        for i in range(5):  # Create 5 large orders
            customer = self.customers[i % len(self.customers)]
            order = LargeOrderFactory(
                customer=customer,
                reference_number=f"LRG-{i:04d}",
                status=random.choice(['draft', 'submitted', 'shipped', 'delivered'])
            )
            self.large_orders.append(order)
        
        # Refresh the materialized view to include the test data
        if call_command:
            call_command('refresh_sku_view')
        
        # Reset connection to simulate real-world usage
        connection.close()
    
    def test_materialized_view_query_performance(self):
        """Test the performance of querying the materialized view."""
        # Get an order ID to query
        order_id = self.regular_orders[0].transaction_id
        
        # Measure time to query the materialized view
        start_time = time.time()
        sku_views = OrderSKUView.objects.filter(transaction_id=order_id)
        sku_count = sku_views.count()
        end_time = time.time()
        
        # Ensure we found SKUs for the order
        self.assertTrue(sku_count > 0)
        
        # The materialized view query should be very fast (under 10ms)
        self.assertLess(end_time - start_time, 0.01, 
                        "Materialized view query took too long")
    
    def test_case_calculation_performance(self):
        """Test the performance of case/pick calculations using the view."""
        # Get a large order for testing
        order = self.large_orders[0]
        
        # Measure time to get case summary
        start_time = time.time()
        case_summary = order.get_case_summary()
        end_time = time.time()
        
        # Verify we got a valid summary
        self.assertIn('total_cases', case_summary)
        self.assertIn('total_picks', case_summary)
        self.assertIn('sku_breakdown', case_summary)
        
        # Case calculation should be reasonably fast (under 50ms for large order)
        self.assertLess(end_time - start_time, 0.05, 
                        "Case calculation took too long")
    
    def test_materialized_view_aggregation_performance(self):
        """Test the performance of aggregation queries on the materialized view."""
        # Measure time for aggregation query
        start_time = time.time()
        aggregation = OrderSKUView.objects.values('status').annotate(
            total_cases=Sum('cases'),
            total_orders=Count('transaction_id', distinct=True)
        ).order_by('status')
        result = list(aggregation)
        end_time = time.time()
        
        # Verify we got valid results
        self.assertTrue(len(result) > 0)
        
        # The aggregation should be reasonably fast (under 50ms)
        self.assertLess(end_time - start_time, 0.05, 
                        "Materialized view aggregation took too long")
    
    def test_sku_search_performance(self):
        """Test the performance of searching for specific SKUs."""
        # Choose a SKU to search for
        test_sku = "SKU-0001"
        
        # Measure time to search for this SKU
        start_time = time.time()
        sku_orders = OrderSKUView.objects.filter(sku_name=test_sku)
        result_count = sku_orders.count()
        end_time = time.time()
        
        # Search should be reasonably fast (under 20ms)
        self.assertLess(end_time - start_time, 0.02, 
                        "SKU search took too long")
    
    def test_join_performance(self):
        """Test the performance of joining Order with OrderSKUView."""
        # Measure time for a query that joins Order with the materialized view
        start_time = time.time()
        joined_query = Order.objects.filter(
            status='submitted'
        ).values('transaction_id').annotate(
            total_cases=Sum('ordersku__cases')
        ).filter(total_cases__gt=0)
        result = list(joined_query)
        end_time = time.time()
        
        # The join should be reasonably fast (under 50ms)
        self.assertLess(end_time - start_time, 0.05, 
                        "Join query took too long")
    
    def test_refresh_view_performance(self):
        """Test the performance of refreshing the materialized view."""
        if not call_command:
            self.skipTest("Django management commands not available")
        
        # Add more orders first to make the refresh meaningful
        for i in range(10):
            OrderFactory(
                customer=self.customers[0],
                reference_number=f"PERF-{i:04d}",
                sku_quantity={f"PERF-SKU-{j:04d}": random.randint(1, 5) for j in range(3)}
            )
        
        # Measure time to refresh the view
        start_time = time.time()
        call_command('refresh_sku_view')
        end_time = time.time()
        
        # View refresh time will depend on data size, but should be reasonable
        # For this test dataset, should be under 500ms
        refresh_time = end_time - start_time
        self.assertLess(refresh_time, 0.5, 
                        f"Materialized view refresh took too long: {refresh_time:.2f}s")
    
    def test_concurrent_view_access(self):
        """Test concurrent access to the materialized view."""
        # Create a list of order IDs to query
        order_ids = [order.transaction_id for order in self.regular_orders[:10]]
        
        def query_sku_view(order_id):
            """Query the materialized view for a specific order."""
            sku_views = OrderSKUView.objects.filter(transaction_id=order_id)
            return sku_views.count() > 0
        
        # Measure time for concurrent access
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(query_sku_view, order_ids))
        end_time = time.time()
        
        # All queries should have succeeded
        self.assertTrue(all(results))
        
        # Concurrent access should be reasonably performant
        # For 10 concurrent queries, ideally under 100ms total
        self.assertLess(end_time - start_time, 0.1, 
                        "Concurrent materialized view access took too long")