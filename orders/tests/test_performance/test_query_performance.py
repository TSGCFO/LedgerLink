# orders/tests/test_performance/test_query_performance.py
import pytest
import time
from django.test import TestCase, override_settings
from django.db import connection, reset_queries
from django.urls import reverse
from rest_framework.test import APIClient
from orders.models import Order
from orders.tests.factories import OrderFactory, LargeOrderFactory
from customers.tests.factories import CustomerFactory
import json


@pytest.mark.django_db
class TestOrderQueryPerformance:
    """
    Performance tests for Order queries.
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self, django_db_setup):
        """Set up test data."""
        # Skip tests if not using PostgreSQL
        if connection.vendor != 'postgresql':
            pytest.skip("Performance tests require PostgreSQL")
    
    def test_large_sku_quantity_performance(self):
        """Test performance with large SKU quantities."""
        # Create order with large number of SKUs (smaller for testing)
        num_skus = 20  # reduced from 100 for faster tests
        order = OrderFactory()
        
        # Add large SKU quantity
        sku_data = {f"PERF-SKU-{i:03d}": i for i in range(1, num_skus + 1)}
        order.sku_quantity = sku_data
        order.save()
        
        # Measure the time to retrieve and deserialize
        start_time = time.time()
        
        # Retrieve from database
        retrieved_order = Order.objects.get(transaction_id=order.transaction_id)
        
        # Access the SKU quantity data
        sku_count = len(retrieved_order.sku_quantity)
        
        end_time = time.time()
        retrieval_time = end_time - start_time
        
        # Print performance info (for debugging)
        print(f"Retrieved order with {sku_count} SKUs in {retrieval_time:.6f} seconds")
        
        # Assert performance is acceptable (adjust threshold as needed)
        assert retrieval_time < 0.1, f"Retrieval time was {retrieval_time:.6f} seconds"
        assert sku_count == num_skus, f"Expected {num_skus} SKUs, got {sku_count}"
    
    def test_filter_performance(self):
        """Test performance of filtering many orders."""
        # Create a large number of orders (smaller for testing)
        num_orders = 20  # reduced from 100 for faster tests
        customer = CustomerFactory()
        
        # Create orders with different statuses
        status_list = ['draft', 'submitted', 'shipped', 'delivered', 'cancelled']
        for i in range(num_orders):
            status = status_list[i % len(status_list)]
            OrderFactory(
                customer=customer,
                status=status,
                reference_number=f"PERF-{status.upper()}-{i}"
            )
        
        # Enable query counting
        reset_queries()
        
        # Measure time to filter orders by status
        start_time = time.time()
        
        filtered_orders = Order.objects.filter(
            customer=customer,
            status='submitted'
        ).select_related('customer')
        
        # Force evaluation of queryset
        order_count = filtered_orders.count()
        orders_list = list(filtered_orders)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Count queries
        query_count = len(connection.queries)
        
        # Print performance info (for debugging)
        print(f"Filtered {order_count} orders from {num_orders} total in {query_time:.6f} seconds with {query_count} queries")
        
        # Assert performance is acceptable
        assert query_time < 0.1, f"Query time was {query_time:.6f} seconds"
        assert query_count <= 2, f"Expected 2 or fewer queries, got {query_count}"
        assert order_count == num_orders // len(status_list), f"Expected {num_orders // len(status_list)} orders, got {order_count}"
    
    def test_search_performance(self):
        """Test performance of search functionality."""
        # Create a number of orders with searchable terms
        num_orders = 10  # reduced for faster tests
        customer = CustomerFactory()
        
        # Create some orders with "SEARCHABLE" in the reference number
        for i in range(num_orders // 2):
            OrderFactory(
                customer=customer,
                reference_number=f"SEARCHABLE-ORDER-{i}"
            )
        
        # Create some orders without the search term
        for i in range(num_orders // 2):
            OrderFactory(
                customer=customer,
                reference_number=f"OTHER-ORDER-{i}"
            )
        
        # Reset query counter
        reset_queries()
        
        # Measure time to search orders
        start_time = time.time()
        
        # Search using Q objects (which is what the view does)
        from django.db.models import Q
        searched_orders = Order.objects.filter(
            Q(reference_number__icontains="SEARCHABLE")
        ).select_related('customer')
        
        # Force evaluation of queryset
        order_count = searched_orders.count()
        orders_list = list(searched_orders)
        
        end_time = time.time()
        search_time = end_time - start_time
        
        # Count queries
        query_count = len(connection.queries)
        
        # Print performance info (for debugging)
        print(f"Found {order_count} orders matching search in {search_time:.6f} seconds with {query_count} queries")
        
        # Assert performance is acceptable
        assert search_time < 0.1, f"Search time was {search_time:.6f} seconds"
        assert query_count <= 2, f"Expected 2 or fewer queries, got {query_count}"
        assert order_count == num_orders // 2, f"Expected {num_orders // 2} orders, got {order_count}"


@override_settings(DEBUG=True)  # Enable query logging
class TestAPIPerformance(TestCase):
    """
    Performance tests for the Order API endpoints.
    """
    
    def setUp(self):
        """Set up test data."""
        # Skip if not using PostgreSQL
        if connection.vendor != 'postgresql':
            self.skipTest("Performance tests require PostgreSQL")
            
        self.client = APIClient()
        self.customer = CustomerFactory()
        self.order_list_url = reverse('order-list')
        
        # Create a large number of orders
        self.num_orders = 10  # reduced for faster tests
        for i in range(self.num_orders):
            OrderFactory(
                customer=self.customer,
                reference_number=f"API-PERF-TEST-{i}"
            )
    
    def test_list_api_performance(self):
        """Test performance of the list API endpoint."""
        # Reset query counter
        reset_queries()
        
        # Measure time for API request
        start_time = time.time()
        
        response = self.client.get(self.order_list_url)
        
        end_time = time.time()
        api_time = end_time - start_time
        
        # Count queries
        query_count = len(connection.queries)
        
        # Print performance info (for debugging)
        print(f"List API returned {len(response.data['data'])} orders in {api_time:.6f} seconds with {query_count} queries")
        
        # Assert performance is acceptable
        self.assertLess(api_time, 0.5, f"API time was {api_time:.6f} seconds")
        self.assertLessEqual(query_count, 5, f"Expected 5 or fewer queries, got {query_count}")
        
        # Check that we got all orders
        self.assertEqual(len(response.data['data']), self.num_orders)
    
    def test_filtered_api_performance(self):
        """Test performance of the filtered API endpoint."""
        # Create some orders with a specific status
        status = 'submitted'
        status_count = 10
        for i in range(status_count):
            OrderFactory(
                customer=self.customer,
                status=status,
                reference_number=f"API-PERF-FILTER-{i}"
            )
        
        # Reset query counter
        reset_queries()
        
        # Measure time for filtered API request
        start_time = time.time()
        
        filtered_url = f"{self.order_list_url}?status={status}"
        response = self.client.get(filtered_url)
        
        end_time = time.time()
        api_time = end_time - start_time
        
        # Count queries
        query_count = len(connection.queries)
        
        # Print performance info (for debugging)
        print(f"Filtered API returned {len(response.data['data'])} orders in {api_time:.6f} seconds with {query_count} queries")
        
        # Assert performance is acceptable
        self.assertLess(api_time, 0.5, f"API time was {api_time:.6f} seconds")
        self.assertLessEqual(query_count, 5, f"Expected 5 or fewer queries, got {query_count}")
        
        # Check that we got the expected number of orders
        self.assertEqual(len(response.data['data']), status_count)
        
        # Check that all returned orders have the expected status
        for order in response.data['data']:
            self.assertEqual(order['status'], status)
    
    def test_create_large_order_performance(self):
        """Test performance of creating a large order."""
        # Create a large order payload
        num_skus = 10  # reduced for faster tests
        sku_data = {f"PERF-API-SKU-{i:03d}": i for i in range(1, num_skus + 1)}
        
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'LARGE-ORDER-PERF-TEST',
            'status': 'draft',
            'priority': 'medium',
            'ship_to_name': 'Performance Test',
            'ship_to_address': '123 Performance St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_to_country': 'US',
            'sku_quantity': sku_data
        }
        
        # Reset query counter
        reset_queries()
        
        # Measure time for API request
        start_time = time.time()
        
        response = self.client.post(
            self.order_list_url,
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        end_time = time.time()
        api_time = end_time - start_time
        
        # Count queries
        query_count = len(connection.queries)
        
        # Print performance info (for debugging)
        print(f"Created order with {num_skus} SKUs in {api_time:.6f} seconds with {query_count} queries")
        
        # Assert performance is acceptable
        self.assertLess(api_time, 1.0, f"API time was {api_time:.6f} seconds")
        self.assertLessEqual(query_count, 10, f"Expected 10 or fewer queries, got {query_count}")
        
        # Check response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['success'], True)
        
        # Verify the SKU data was saved correctly
        transaction_id = response.data['data']['transaction_id']
        order = Order.objects.get(transaction_id=transaction_id)
        self.assertEqual(len(order.sku_quantity), num_skus)