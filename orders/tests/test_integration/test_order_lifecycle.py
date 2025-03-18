# orders/tests/test_integration/test_order_lifecycle.py
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.tests.factories import OrderFactory
from customers.tests.factories import CustomerFactory
import json
from decimal import Decimal


class TestOrderLifecycle(TestCase):
    """
    Integration test for the full lifecycle of an order.
    Tests the creation, updating, and deleting of an order.
    """
    
    def setUp(self):
        """Set up test data."""
        # Clear any existing orders to ensure consistent test environment
        from orders.models import Order
        Order.objects.all().delete()
        
        self.client = APIClient()
        self.customer = CustomerFactory()
        self.order_list_url = reverse('order-list')
    
    def test_order_lifecycle(self):
        """Test the complete lifecycle of an order."""
        # 1. Create a new order
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'LIFECYCLE-TEST-001',
            'status': 'draft',
            'priority': 'medium',
            'ship_to_name': 'Lifecycle Test',
            'ship_to_address': '123 Lifecycle St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_to_country': 'US',
            'sku_quantity': {"SKU001": 5, "SKU002": 10}
        }
        
        response = self.client.post(
            self.order_list_url,
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        # Check creation response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        
        # Get transaction_id from response
        transaction_id = response.data['data']['transaction_id']
        order_detail_url = reverse('order-detail', kwargs={'pk': transaction_id})
        
        # 2. Verify the order details
        response = self.client.get(order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference_number'], 'LIFECYCLE-TEST-001')
        self.assertEqual(response.data['status'], 'draft')
        self.assertEqual(response.data['priority'], 'medium')
        self.assertEqual(response.data['sku_quantity'], {"SKU001": 5, "SKU002": 10})
        
        # 3. Update order status to submitted
        update_data = {
            'status': 'submitted',
            'carrier': 'UPS'
        }
        
        response = self.client.patch(
            order_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Check update response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['status'], 'submitted')
        self.assertEqual(response.data['data']['carrier'], 'UPS')
        
        # Verify the updated order in the database
        order = Order.objects.get(transaction_id=transaction_id)
        self.assertEqual(order.status, 'submitted')
        self.assertEqual(order.carrier, 'UPS')
        
        # 4. Update order status to shipped
        update_data = {
            'status': 'shipped',
            'packages': 3,
            'weight_lb': Decimal('45.50'),
            'volume_cuft': Decimal('12.75')
        }
        
        response = self.client.patch(
            order_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Check update response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['status'], 'shipped')
        self.assertEqual(response.data['data']['packages'], 3)
        self.assertEqual(response.data['data']['weight_lb'], '45.50')
        
        # Verify the updated order in the database
        order = Order.objects.get(transaction_id=transaction_id)
        self.assertEqual(order.status, 'shipped')
        self.assertEqual(order.packages, 3)
        self.assertEqual(order.weight_lb, Decimal('45.50'))
        
        # 5. Update order status to delivered
        update_data = {
            'status': 'delivered'
        }
        
        response = self.client.patch(
            order_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Check update response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['status'], 'delivered')
        
        # Verify the updated order in the database
        order = Order.objects.get(transaction_id=transaction_id)
        self.assertEqual(order.status, 'delivered')
        
        # 6. Try to delete a delivered order (should fail)
        response = self.client.delete(order_detail_url)
        
        # Check delete response (should be an error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Can only delete draft or cancelled orders')
        
        # Verify the order still exists
        self.assertTrue(Order.objects.filter(transaction_id=transaction_id).exists())
    
    def test_order_cancellation_flow(self):
        """Test the cancellation flow of an order."""
        # 1. Create a new order
        order = OrderFactory(customer=self.customer, status='draft')
        order_detail_url = reverse('order-detail', kwargs={'pk': order.transaction_id})
        
        # 2. Cancel the order
        cancel_url = reverse('order-cancel', kwargs={'pk': order.transaction_id})
        response = self.client.post(cancel_url)
        
        # Check cancel response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Order cancelled successfully')
        
        # Verify the order is now cancelled
        order = Order.objects.get(transaction_id=order.transaction_id)
        self.assertEqual(order.status, 'cancelled')
        
        # 3. Try to update a cancelled order (should still work)
        update_data = {
            'notes': 'Cancelled due to customer request'
        }
        
        response = self.client.patch(
            order_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Check update response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Verify the note was updated but status remains cancelled
        order = Order.objects.get(transaction_id=order.transaction_id)
        self.assertEqual(order.notes, 'Cancelled due to customer request')
        self.assertEqual(order.status, 'cancelled')
        
        # 4. Try to change status of cancelled order (should fail)
        update_data = {
            'status': 'submitted'
        }
        
        response = self.client.patch(
            order_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Check update response (should be an error)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        
        # 5. Delete the cancelled order (should work)
        response = self.client.delete(order_detail_url)
        
        # Check delete response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Order deleted successfully')
        
        # Verify the order no longer exists
        self.assertFalse(Order.objects.filter(transaction_id=order.transaction_id).exists())


class TestOrderBulkOperations(TestCase):
    """
    Integration test for bulk operations on orders.
    Tests creating, updating, and querying multiple orders.
    """
    
    def setUp(self):
        """Set up test data."""
        # Clear any existing orders to ensure consistent test environment
        from orders.models import Order
        Order.objects.all().delete()
        
        self.client = APIClient()
        self.customer = CustomerFactory()
        self.order_list_url = reverse('order-list')
        
        # Create a batch of orders with various statuses
        self.orders = []
        for status in ['draft', 'submitted', 'shipped', 'delivered', 'cancelled']:
            for i in range(2):  # 2 orders of each status
                order = OrderFactory(
                    customer=self.customer,
                    status=status,
                    reference_number=f"{status.upper()}-{i+1}"
                )
                self.orders.append(order)
    
    def test_status_count_api(self):
        """Test the status_counts API endpoint."""
        status_counts_url = reverse('order-status-counts')
        
        response = self.client.get(status_counts_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Check counts
        counts = response.data['data']
        self.assertEqual(counts['draft'], 2)
        self.assertEqual(counts['submitted'], 2)
        self.assertEqual(counts['shipped'], 2)
        self.assertEqual(counts['delivered'], 2)
        self.assertEqual(counts['cancelled'], 2)
    
    def test_bulk_status_filtering(self):
        """Test filtering orders by status."""
        # Test each status
        for status in ['draft', 'submitted', 'shipped', 'delivered', 'cancelled']:
            url = f"{self.order_list_url}?status={status}"
            response = self.client.get(url)
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['success'], True)
            self.assertEqual(len(response.data['data']), 2)  # Should have 2 of each status
            
            # Check all returned orders have the expected status
            for order_data in response.data['data']:
                self.assertEqual(order_data['status'], status)
    
    def test_search_integration(self):
        """Test searching orders."""
        # Create orders with specific reference numbers for searching
        OrderFactory(customer=self.customer, reference_number="SEARCH-INTEGRATION-001")
        OrderFactory(customer=self.customer, reference_number="SEARCH-INTEGRATION-002")
        OrderFactory(customer=self.customer, reference_number="OTHER-REFERENCE-XYZ")
        
        # Search for 'SEARCH-INTEGRATION'
        url = f"{self.order_list_url}?search=SEARCH-INTEGRATION"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # We should find at least 2 orders
        found_references = []
        for order in response.data['data']:
            if 'SEARCH-INTEGRATION' in order['reference_number']:
                found_references.append(order['reference_number'])
        
        self.assertGreaterEqual(len(found_references), 2)
        self.assertIn("SEARCH-INTEGRATION-001", found_references)
        self.assertIn("SEARCH-INTEGRATION-002", found_references)