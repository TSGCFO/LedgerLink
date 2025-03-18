# orders/tests/test_views/test_order_viewset.py
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from orders.models import Order
from orders.views import OrderViewSet
from orders.serializers import OrderSerializer
from orders.tests.factories import (
    OrderFactory, SubmittedOrderFactory, ShippedOrderFactory,
    DeliveredOrderFactory, CancelledOrderFactory,
    OrderWithoutShippingFactory, HighPriorityOrderFactory,
    LowPriorityOrderFactory
)
from customers.tests.factories import CustomerFactory
from unittest.mock import patch, MagicMock
import json
from decimal import Decimal


class TestOrderViewSet(TestCase):
    """
    Test suite for the OrderViewSet.
    """
    
    def setUp(self):
        """Set up test data."""
        # Clear any existing orders to ensure consistent test environment
        from orders.models import Order
        Order.objects.all().delete()
        
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.customer = CustomerFactory()
        self.order = OrderFactory(customer=self.customer)
        self.order_list_url = reverse('order-list')
        self.order_detail_url = reverse('order-detail', kwargs={'pk': self.order.transaction_id})
    
    def test_get_order_list(self):
        """Test getting a list of orders."""
        # Create additional orders
        OrderFactory.create_batch(5, customer=self.customer)
        
        # Get the list
        response = self.client.get(self.order_list_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 6)  # 5 + 1 original
    
    def test_get_order_detail(self):
        """Test getting a specific order."""
        response = self.client.get(self.order_detail_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_id'], self.order.transaction_id)
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertEqual(response.data['reference_number'], self.order.reference_number)
    
    def test_create_order(self):
        """Test creating a new order."""
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'TEST-REF-001',
            'status': 'draft',
            'priority': 'medium',
            'ship_to_name': 'Test Recipient',
            'ship_to_address': '123 Test St',
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
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Order created successfully')
        
        # Check the created order
        created_order = Order.objects.get(reference_number='TEST-REF-001')
        self.assertEqual(created_order.customer.id, self.customer.id)
        self.assertEqual(created_order.status, 'draft')
        self.assertEqual(created_order.sku_quantity, {"SKU001": 5, "SKU002": 10})
    
    def test_update_order(self):
        """Test updating an existing order."""
        update_data = {
            'status': 'submitted',
            'priority': 'high',
            'reference_number': 'UPDATED-REF'
        }
        
        response = self.client.patch(
            self.order_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Order updated successfully')
        
        # Check the updated order
        updated_order = Order.objects.get(transaction_id=self.order.transaction_id)
        self.assertEqual(updated_order.status, 'submitted')
        self.assertEqual(updated_order.priority, 'high')
        self.assertEqual(updated_order.reference_number, 'UPDATED-REF')
    
    def test_delete_order(self):
        """Test deleting an order."""
        # Can only delete draft orders
        response = self.client.delete(self.order_detail_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Order deleted successfully')
        
        # Check the order was deleted
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(transaction_id=self.order.transaction_id)
    
    def test_cannot_delete_submitted_order(self):
        """Test that submitted orders cannot be deleted."""
        submitted_order = SubmittedOrderFactory(customer=self.customer)
        url = reverse('order-detail', kwargs={'pk': submitted_order.transaction_id})
        
        response = self.client.delete(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Can only delete draft or cancelled orders')
        
        # Check the order was not deleted
        self.assertTrue(Order.objects.filter(transaction_id=submitted_order.transaction_id).exists())
    
    def test_cancel_order(self):
        """Test cancelling an order."""
        cancel_url = reverse('order-cancel', kwargs={'pk': self.order.transaction_id})
        
        response = self.client.post(cancel_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Order cancelled successfully')
        
        # Check the order was cancelled
        cancelled_order = Order.objects.get(transaction_id=self.order.transaction_id)
        self.assertEqual(cancelled_order.status, 'cancelled')
    
    def test_cannot_cancel_delivered_order(self):
        """Test that delivered orders cannot be cancelled."""
        delivered_order = DeliveredOrderFactory(customer=self.customer)
        cancel_url = reverse('order-cancel', kwargs={'pk': delivered_order.transaction_id})
        
        response = self.client.post(cancel_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Cannot cancel a delivered order')
        
        # Check the order was not cancelled
        delivered_order = Order.objects.get(transaction_id=delivered_order.transaction_id)
        self.assertEqual(delivered_order.status, 'delivered')
    
    def test_get_status_counts(self):
        """Test getting count of orders by status."""
        # Create orders with different statuses
        OrderFactory.create_batch(3, status='draft')
        SubmittedOrderFactory.create_batch(2)
        ShippedOrderFactory.create_batch(1)
        DeliveredOrderFactory.create_batch(4)
        CancelledOrderFactory.create_batch(2)
        
        status_counts_url = reverse('order-status-counts')
        
        response = self.client.get(status_counts_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Check counts (including the one created in setUp)
        counts = response.data['data']
        self.assertEqual(counts['draft'], 4)  # 3 + 1 from setUp
        self.assertEqual(counts['submitted'], 2)
        self.assertEqual(counts['shipped'], 1)
        self.assertEqual(counts['delivered'], 4)
        self.assertEqual(counts['cancelled'], 2)
    
    def test_get_choices(self):
        """Test getting available choices for status and priority fields."""
        choices_url = reverse('order-choices')
        
        response = self.client.get(choices_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Check choices
        choices = response.data['data']
        self.assertEqual(len(choices['status_choices']), 5)  # 5 status choices
        self.assertEqual(len(choices['priority_choices']), 3)  # 3 priority choices
        
        # Check that choices include expected values
        status_values = [choice['value'] for choice in choices['status_choices']]
        self.assertIn('draft', status_values)
        self.assertIn('submitted', status_values)
        self.assertIn('shipped', status_values)
        self.assertIn('delivered', status_values)
        self.assertIn('cancelled', status_values)
        
        priority_values = [choice['value'] for choice in choices['priority_choices']]
        self.assertIn('low', priority_values)
        self.assertIn('medium', priority_values)
        self.assertIn('high', priority_values)
    
    def test_filter_by_customer(self):
        """Test filtering orders by customer."""
        # Create orders for different customers
        customer2 = CustomerFactory()
        OrderFactory.create_batch(3, customer=self.customer)
        OrderFactory.create_batch(2, customer=customer2)
        
        # Filter by first customer
        url = f"{self.order_list_url}?customer={self.customer.id}"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 4)  # 3 + 1 from setUp
        
        # Check all returned orders have the correct customer
        for order_data in response.data['data']:
            self.assertEqual(order_data['customer'], self.customer.id)
        
        # Filter by second customer
        url = f"{self.order_list_url}?customer={customer2.id}"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        
        # Check all returned orders have the correct customer
        for order_data in response.data['data']:
            self.assertEqual(order_data['customer'], customer2.id)
    
    def test_filter_by_status(self):
        """Test filtering orders by status."""
        # Create orders with different statuses
        OrderFactory.create_batch(2, status='draft')
        SubmittedOrderFactory.create_batch(3)
        
        # Filter by draft status
        url = f"{self.order_list_url}?status=draft"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)  # 2 + 1 from setUp
        
        # Check all returned orders have draft status
        for order_data in response.data['data']:
            self.assertEqual(order_data['status'], 'draft')
        
        # Filter by submitted status
        url = f"{self.order_list_url}?status=submitted"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
        
        # Check all returned orders have submitted status
        for order_data in response.data['data']:
            self.assertEqual(order_data['status'], 'submitted')
    
    def test_filter_by_priority(self):
        """Test filtering orders by priority."""
        # Create orders with different priorities
        LowPriorityOrderFactory.create_batch(2)
        HighPriorityOrderFactory.create_batch(3)
        
        # Filter by medium priority (default from setUp)
        url = f"{self.order_list_url}?priority=medium"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)  # Just the one from setUp
        
        # Check all returned orders have medium priority
        for order_data in response.data['data']:
            self.assertEqual(order_data['priority'], 'medium')
        
        # Filter by high priority
        url = f"{self.order_list_url}?priority=high"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
        
        # Check all returned orders have high priority
        for order_data in response.data['data']:
            self.assertEqual(order_data['priority'], 'high')
    
    def test_search_functionality(self):
        """Test search functionality."""
        # Create orders with specific reference numbers
        OrderFactory(reference_number="SEARCH-TEST-123")
        OrderFactory(reference_number="SEARCH-TEST-456")
        OrderFactory(reference_number="OTHER-REF-789")
        
        # Search for 'SEARCH'
        url = f"{self.order_list_url}?search=SEARCH"
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        
        # Check all returned orders have matching reference numbers
        ref_numbers = [order['reference_number'] for order in response.data['data']]
        self.assertIn("SEARCH-TEST-123", ref_numbers)
        self.assertIn("SEARCH-TEST-456", ref_numbers)
        self.assertNotIn("OTHER-REF-789", ref_numbers)
        
        # Test search by ship_to_name
        OrderFactory(ship_to_name="John SearchTest")
        
        url = f"{self.order_list_url}?search=SearchTest"
        response = self.client.get(url)
        
        # There should be at least one result
        self.assertGreater(len(response.data['data']), 0)
        
        # At least one result should have matching ship_to_name
        ship_to_names = [order['ship_to_name'] for order in response.data['data'] if order['ship_to_name']]
        self.assertTrue(any("SearchTest" in name for name in ship_to_names))