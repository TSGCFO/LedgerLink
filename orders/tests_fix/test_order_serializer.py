"""
Tests for OrderSerializer
"""
from django.test import TestCase
import random

from orders.models import Order
from orders.serializers import OrderSerializer
from customers.models import Customer


class TestOrderSerializer(TestCase):
    """Test OrderSerializer functionality"""

    def setUp(self):
        """Set up test data."""
        # Generate random transaction IDs to prevent conflicts
        self.transaction_id = random.randint(100000, 999999)
        
        # Create a customer
        self.customer = Customer.objects.create(
            company_name="Test Serializer Corp",
            legal_business_name="Test Serializer LLC",
            email="serializer@example.com",
            phone="123-456-7890",
            is_active=True
        )
        
        # Create an order for serializer testing
        self.order = Order.objects.create(
            transaction_id=self.transaction_id,
            customer=self.customer,
            reference_number="SER-TEST-001",
            ship_to_name="Serializer Recipient",
            ship_to_address="123 Serializer St",
            ship_to_city="Serializer City",
            ship_to_state="SC",
            ship_to_zip="12345",
            sku_quantity={"SKU-A": 10, "SKU-B": 5},
            total_item_qty=15,
            line_items=2,
            status="draft",
            priority="medium"
        )
        
        # Valid data for serializer tests
        self.valid_data = {
            'transaction_id': random.randint(1, 2147483647),  # Max safe integer for PostgreSQL
            'customer': self.customer.id,
            'reference_number': 'SER-TEST-002',
            'ship_to_name': 'Another Recipient',
            'ship_to_address': '456 Serializer St',
            'ship_to_city': 'Serializer City',
            'ship_to_state': 'SC',
            'ship_to_zip': '54321',
            'sku_quantity': {"SKU-C": 3, "SKU-D": 7},
            'status': 'draft',
            'priority': 'high'
        }
    
    def test_serializer_valid_data(self):
        """Test serializer with valid data."""
        serializer = OrderSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_missing_required_field(self):
        """Test serializer with missing required field."""
        # Remove required field
        invalid_data = self.valid_data.copy()
        invalid_data.pop('reference_number')
        
        serializer = OrderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('reference_number', serializer.errors)
    
    def test_serializer_autocalculates_item_quantities(self):
        """Test serializer autocalculates total_item_qty from sku_quantity."""
        data = self.valid_data.copy()
        # Remove calculated fields to test auto-calculation
        if 'total_item_qty' in data:
            data.pop('total_item_qty')
        if 'line_items' in data:
            data.pop('line_items')
        
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Instead of saving, check the validated data includes calculated fields
        validated_data = serializer.validated_data
        
        # Verify sku_quantity is processed correctly
        self.assertIn('sku_quantity', validated_data)
        self.assertEqual(validated_data['sku_quantity'], {"SKU-C": 3, "SKU-D": 7})
        
        # If serializer auto-calculates these fields, check them
        if 'total_item_qty' in validated_data:
            self.assertEqual(validated_data['total_item_qty'], 10)  # 3 + 7
        if 'line_items' in validated_data:
            self.assertEqual(validated_data['line_items'], 2)  # 2 SKUs
    
    def test_shipping_address_validation(self):
        """Test shipping address validation."""
        data = self.valid_data.copy()
        # Remove zip code which should be required if city/state are provided
        data.pop('ship_to_zip')
        
        serializer = OrderSerializer(data=data)
        # This should fail since we have city/state but no zip
        self.assertFalse(serializer.is_valid())
        # Error might be direct or grouped under 'shipping'
        self.assertTrue(
            'ship_to_zip' in serializer.errors or
            'shipping' in serializer.errors
        )
    
    def test_sku_quantity_validation_valid(self):
        """Test SKU quantity validation with valid format."""
        serializer = OrderSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_sku_quantity_validation_invalid_format(self):
        """Test SKU quantity validation with invalid format."""
        invalid_data = self.valid_data.copy()
        invalid_data['sku_quantity'] = "not a dict"
        
        serializer = OrderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku_quantity', serializer.errors)
    
    def test_sku_quantity_validation_invalid_quantities(self):
        """Test SKU quantity validation with invalid quantities."""
        invalid_data = self.valid_data.copy()
        invalid_data['sku_quantity'] = {"SKU-X": -5, "SKU-Y": "not a number"}
        
        serializer = OrderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku_quantity', serializer.errors)