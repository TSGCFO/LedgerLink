# orders/tests/test_serializers/test_order_serializer.py
import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from orders.serializers import OrderSerializer
from orders.models import Order
from orders.tests.factories import (
    OrderFactory, SubmittedOrderFactory, ShippedOrderFactory,
    DeliveredOrderFactory, CancelledOrderFactory
)
from customers.tests.factories import CustomerFactory
from unittest.mock import patch, MagicMock
import json
from decimal import Decimal
from django.utils import timezone


class TestOrderSerializer(TestCase):
    """
    Test suite for the OrderSerializer.
    """
    
    def setUp(self):
        """Set up test data."""
        self.customer = CustomerFactory()
        self.order = OrderFactory(customer=self.customer)
        self.serializer = OrderSerializer(instance=self.order)
    
    def test_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        expected_fields = [
            'transaction_id', 'customer', 'customer_details', 'close_date',
            'reference_number', 'status', 'priority',
            'ship_to_name', 'ship_to_company', 'ship_to_address',
            'ship_to_address2', 'ship_to_city', 'ship_to_state',
            'ship_to_zip', 'ship_to_country', 'weight_lb',
            'line_items', 'sku_quantity', 'total_item_qty',
            'volume_cuft', 'packages', 'notes', 'carrier'
        ]
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_customer_serialization(self):
        """Test that the customer field is properly serialized."""
        data = self.serializer.data
        
        # Check the nested customer details field
        self.assertEqual(data['customer'], self.customer.id)
        self.assertIn('company_name', data['customer_details'])
        self.assertEqual(data['customer_details']['id'], self.customer.id)
    
    def test_decimal_serialization(self):
        """Test that decimal fields are properly serialized."""
        # Set decimal values
        self.order.weight_lb = Decimal("42.50")
        self.order.volume_cuft = Decimal("123.45")
        self.order.save()
        
        serializer = OrderSerializer(instance=self.order)
        data = serializer.data
        
        # Check decimal fields
        self.assertEqual(data['weight_lb'], '42.50')
        self.assertEqual(data['volume_cuft'], '123.45')
    
    def test_json_serialization(self):
        """Test that JSON fields are properly serialized."""
        # Set JSON data
        sku_data = {"SKU001": 5, "SKU002": 10}
        self.order.sku_quantity = sku_data
        self.order.save()
        
        serializer = OrderSerializer(instance=self.order)
        data = serializer.data
        
        # JSON should be returned as a Python object
        self.assertEqual(data['sku_quantity'], sku_data)
    
    def test_create_order(self):
        """Test creating a new order with the serializer."""
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'TEST-REF-001',
            'status': 'draft',
            'priority': 'medium',
            'ship_to_name': 'Test Recipient',
            'ship_to_company': 'Test Company',
            'ship_to_address': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_to_country': 'US',
            'sku_quantity': {"SKU001": 5, "SKU002": 10}
        }
        
        serializer = OrderSerializer(data=order_data)
        self.assertTrue(serializer.is_valid())
        
        # Create the order
        order = serializer.save()
        
        # Verify the order was created correctly
        self.assertIsInstance(order, Order)
        self.assertEqual(order.customer.id, self.customer.id)
        self.assertEqual(order.reference_number, 'TEST-REF-001')
        self.assertEqual(order.status, 'draft')
        self.assertEqual(order.sku_quantity, {"SKU001": 5, "SKU002": 10})
        self.assertEqual(order.line_items, 2)  # 2 SKUs
        self.assertEqual(order.total_item_qty, 15)  # 5 + 10
    
    def test_update_order(self):
        """Test updating an existing order with the serializer."""
        # Initial data
        self.assertEqual(self.order.status, 'draft')
        
        # Update data
        update_data = {
            'status': 'submitted',
            'priority': 'high',
            'reference_number': 'UPDATED-REF'
        }
        
        serializer = OrderSerializer(instance=self.order, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Save the updates
        updated_order = serializer.save()
        
        # Verify the order was updated correctly
        self.assertEqual(updated_order.status, 'submitted')
        self.assertEqual(updated_order.priority, 'high')
        self.assertEqual(updated_order.reference_number, 'UPDATED-REF')
        
        # Other fields should remain unchanged
        self.assertEqual(updated_order.customer.id, self.customer.id)
    
    def test_validate_sku_quantity_valid(self):
        """Test validation of valid SKU quantity data."""
        # Valid SKU quantity formats
        valid_formats = [
            {"SKU001": 5},  # Single SKU
            {"SKU001": 5, "SKU002": 10},  # Multiple SKUs
            {"SKU001": 5.5},  # Decimal quantity
            {}  # Empty dict
        ]
        
        for sku_data in valid_formats:
            serializer = OrderSerializer()
            result = serializer.validate_sku_quantity(sku_data)
            self.assertEqual(result, sku_data)
    
    def test_validate_sku_quantity_invalid(self):
        """Test validation of invalid SKU quantity data."""
        # Invalid SKU quantity formats
        invalid_formats = [
            {"SKU001": -5},  # Negative quantity
            {"SKU001": 0},  # Zero quantity
            {"SKU001": "string"},  # Non-numeric quantity
            [1, 2, 3],  # Not a dict
            123  # Not a dict
        ]
        
        serializer = OrderSerializer()
        for sku_data in invalid_formats:
            with self.assertRaises(ValidationError):
                serializer.validate_sku_quantity(sku_data)
    
    def test_transaction_id_generation(self):
        """Test that transaction_id is generated when creating a new order."""
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'TEST-REF-001'
        }
        
        serializer = OrderSerializer(data=order_data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
            
        # Verify a transaction_id was generated (specific value not important)
        self.assertIsNotNone(order.transaction_id)
        self.assertGreater(order.transaction_id, 0)
    
    def test_calculate_total_item_qty(self):
        """Test that total_item_qty is calculated from sku_quantity."""
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'TEST-REF-001',
            'sku_quantity': {"SKU001": 5, "SKU002": 10, "SKU003": 15}
        }
        
        serializer = OrderSerializer(data=order_data)
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        
        # Check that total_item_qty was calculated
        self.assertEqual(validated_data['total_item_qty'], 30)  # 5 + 10 + 15
        self.assertEqual(validated_data['line_items'], 3)  # 3 SKUs
    
    def test_shipping_address_validation(self):
        """Test validation of shipping address."""
        # Test with incomplete shipping information
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'TEST-REF-001',
            'ship_to_name': 'Test Recipient',  # Only providing name, missing other required fields
        }
        
        serializer = OrderSerializer(data=order_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('shipping', serializer.errors)
        
        # Test with complete shipping information
        order_data = {
            'customer': self.customer.id,
            'reference_number': 'TEST-REF-001',
            'ship_to_name': 'Test Recipient',
            'ship_to_address': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345'
        }
        
        serializer = OrderSerializer(data=order_data)
        self.assertTrue(serializer.is_valid())
    
    def test_status_transition_validation(self):
        """Test validation of status transitions."""
        # Test valid transition: draft -> submitted
        draft_order = OrderFactory(status='draft')
        serializer = OrderSerializer(instance=draft_order, data={'status': 'submitted'}, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Test valid transition: submitted -> shipped
        submitted_order = SubmittedOrderFactory()
        serializer = OrderSerializer(instance=submitted_order, data={'status': 'shipped'}, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid transition: draft -> delivered (skipping statuses)
        draft_order = OrderFactory(status='draft')
        serializer = OrderSerializer(instance=draft_order, data={'status': 'delivered'}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        
        # Test invalid transition: cancelled -> any other status
        cancelled_order = CancelledOrderFactory()
        serializer = OrderSerializer(instance=cancelled_order, data={'status': 'submitted'}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)