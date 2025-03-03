"""
Unit tests for Bulk Operations serializers.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from rest_framework.exceptions import ValidationError
import pandas as pd
from decimal import Decimal

from bulk_operations.serializers import (
    BulkOperationBaseSerializer,
    CustomerBulkSerializer,
    OrderBulkSerializer,
    ProductBulkSerializer,
    BulkSerializerFactory
)


class TestBulkOperationBaseSerializer:
    """Tests for the base bulk operation serializer."""

    def test_validate_foreign_key_success(self):
        """Test foreign key validation with existing object."""
        serializer = BulkOperationBaseSerializer()
        
        # Mock model and query
        mock_model = MagicMock()
        mock_instance = MagicMock()
        mock_model.objects.get.return_value = mock_instance
        mock_model.__name__ = "TestModel"
        
        # Call validation method
        result = serializer.validate_foreign_key(1, mock_model)
        
        # Check result
        assert result == mock_instance
        mock_model.objects.get.assert_called_once_with(id=1)

    def test_validate_foreign_key_does_not_exist(self):
        """Test foreign key validation with non-existent object."""
        serializer = BulkOperationBaseSerializer()
        
        # Mock model and query
        mock_model = MagicMock()
        mock_model.DoesNotExist = Exception
        mock_model.objects.get.side_effect = mock_model.DoesNotExist("Does not exist")
        mock_model.__name__ = "TestModel"
        
        # Call validation method and check exception
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_foreign_key(999, mock_model)
        
        assert "TestModel with id 999 does not exist" in str(excinfo.value)

    def test_validate_foreign_key_invalid_format(self):
        """Test foreign key validation with invalid format."""
        serializer = BulkOperationBaseSerializer()
        
        # Mock model
        mock_model = MagicMock()
        mock_model.objects.get.side_effect = ValueError("Invalid format")
        mock_model.__name__ = "TestModel"
        
        # Call validation method and check exception
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_foreign_key("not-an-id", mock_model)
        
        assert "Invalid TestModel ID format" in str(excinfo.value)


class TestCustomerBulkSerializer:
    """Tests for the CustomerBulkSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name',
            'email': 'test@example.com',
            'phone': '123-456-7890',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip': '12345',
            'country': 'US',
            'business_type': 'Corporation'
        }
        
        serializer = CustomerBulkSerializer(data=data)
        assert serializer.is_valid()
        
        # Check validated data
        validated_data = serializer.validated_data
        assert validated_data['company_name'] == 'Test Company'
        assert validated_data['legal_business_name'] == 'Test Legal Name'
        assert validated_data['email'] == 'test@example.com'

    def test_invalid_email(self):
        """Test serializer with invalid email."""
        data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name',
            'email': 'not-an-email'
        }
        
        serializer = CustomerBulkSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_required_fields(self):
        """Test serializer with missing required fields."""
        data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name'
            # Missing email field
        }
        
        serializer = CustomerBulkSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    @patch('bulk_operations.serializers.apps.get_model')
    def test_create_method(self, mock_get_model):
        """Test create method."""
        # Setup mock
        mock_customer_model = MagicMock()
        mock_get_model.return_value = mock_customer_model
        
        # Setup validated data
        validated_data = {
            'company_name': 'Test Company',
            'legal_business_name': 'Test Legal Name',
            'email': 'test@example.com'
        }
        
        # Call create method
        serializer = CustomerBulkSerializer()
        serializer.create(validated_data)
        
        # Check if model was created with correct data
        mock_get_model.assert_called_once_with('customers', 'Customer')
        mock_customer_model.objects.create.assert_called_once_with(**validated_data)


class TestOrderBulkSerializer:
    """Tests for the OrderBulkSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'transaction_id': 12345,
            'customer': 1,
            'reference_number': 'REF123',
            'ship_to_name': 'John Doe',
            'ship_to_address': '123 Main St',
            'ship_to_city': 'Anytown',
            'ship_to_state': 'ST',
            'ship_to_zip': '12345',
            'status': 'draft',
            'priority': 'medium'
        }
        
        # Mock the validate_customer method
        with patch.object(OrderBulkSerializer, 'validate_customer', return_value=MagicMock()):
            serializer = OrderBulkSerializer(data=data)
            assert serializer.is_valid()
            
            # Check validated data
            validated_data = serializer.validated_data
            assert validated_data['transaction_id'] == 12345
            assert validated_data['reference_number'] == 'REF123'
            assert validated_data['status'] == 'draft'
            assert validated_data['priority'] == 'medium'

    def test_status_default(self):
        """Test status field default value."""
        serializer = OrderBulkSerializer()
        
        # Test None value
        assert serializer.validate_status(None) == 'draft'
        
        # Test empty string
        assert serializer.validate_status('') == 'draft'
        
        # Test NaN
        assert serializer.validate_status(float('nan')) == 'draft'
        
        # Test valid value
        assert serializer.validate_status('shipped') == 'shipped'

    def test_priority_default(self):
        """Test priority field default value."""
        serializer = OrderBulkSerializer()
        
        # Test None value
        assert serializer.validate_priority(None) == 'medium'
        
        # Test empty string
        assert serializer.validate_priority('') == 'medium'
        
        # Test NaN
        assert serializer.validate_priority(float('nan')) == 'medium'
        
        # Test valid value
        assert serializer.validate_priority('high') == 'high'

    def test_validate_sku_quantity_valid_json(self):
        """Test SKU quantity validation with valid JSON string."""
        serializer = OrderBulkSerializer()
        json_value = '{"SKU1": 5, "SKU2": 3}'
        
        result = serializer.validate_sku_quantity(json_value)
        
        assert isinstance(result, dict)
        assert result["SKU1"] == 5
        assert result["SKU2"] == 3

    def test_validate_sku_quantity_invalid_json(self):
        """Test SKU quantity validation with invalid JSON string."""
        serializer = OrderBulkSerializer()
        invalid_json = '{invalid json}'
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_sku_quantity(invalid_json)
        
        assert "Invalid JSON format" in str(excinfo.value)

    def test_validate_sku_quantity_not_dict(self):
        """Test SKU quantity validation with non-dictionary value."""
        serializer = OrderBulkSerializer()
        non_dict_value = [1, 2, 3]  # A list, not a dict
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_sku_quantity(non_dict_value)
        
        assert "must be a dictionary" in str(excinfo.value)

    def test_validate_sku_quantity_invalid_quantity(self):
        """Test SKU quantity validation with invalid quantity values."""
        serializer = OrderBulkSerializer()
        invalid_quantity = {"SKU1": -5}  # Negative quantity
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate_sku_quantity(invalid_quantity)
        
        assert "Invalid quantity" in str(excinfo.value)

    def test_validate_sku_quantity_null(self):
        """Test SKU quantity validation with null value."""
        serializer = OrderBulkSerializer()
        
        # Test None value
        assert serializer.validate_sku_quantity(None) is None
        
        # Test NaN
        assert serializer.validate_sku_quantity(float('nan')) is None
        
        # Test empty string
        assert serializer.validate_sku_quantity('') is None


class TestProductBulkSerializer:
    """Tests for the ProductBulkSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'sku': 'TEST-SKU-123',
            'customer': 1,
            'labeling_unit_1': 'box',
            'labeling_quantity_1': 10
        }
        
        # Mock the validate_customer method
        with patch.object(ProductBulkSerializer, 'validate_customer', return_value=MagicMock()):
            serializer = ProductBulkSerializer(data=data)
            assert serializer.is_valid()
            
            # Check validated data
            validated_data = serializer.validated_data
            assert validated_data['sku'] == 'TEST-SKU-123'
            assert validated_data['labeling_unit_1'] == 'box'
            assert validated_data['labeling_quantity_1'] == 10

    @patch('bulk_operations.serializers.apps.get_model')
    def test_validate_customer(self, mock_get_model):
        """Test customer validation."""
        # Setup mock
        mock_customer_model = MagicMock()
        mock_customer = MagicMock()
        mock_customer_model.objects.get.return_value = mock_customer
        mock_get_model.return_value = mock_customer_model
        
        # Call validate method
        serializer = ProductBulkSerializer()
        result = serializer.validate_customer(1)
        
        # Check result
        assert result == mock_customer
        mock_get_model.assert_called_once_with('customers', 'Customer')
        mock_customer_model.objects.get.assert_called_once_with(id=1)


class TestBulkSerializerFactory:
    """Tests for the BulkSerializerFactory."""

    def test_get_serializer_valid_types(self):
        """Test getting serializers for all valid types."""
        # Test all valid template types
        factory = BulkSerializerFactory()
        
        # Customer serializer
        serializer_class = factory.get_serializer('customers')
        assert serializer_class == CustomerBulkSerializer
        
        # Order serializer
        serializer_class = factory.get_serializer('orders')
        assert serializer_class == OrderBulkSerializer
        
        # Product serializer
        serializer_class = factory.get_serializer('products')
        assert serializer_class == ProductBulkSerializer

    def test_get_serializer_invalid_type(self):
        """Test getting serializer for invalid type."""
        factory = BulkSerializerFactory()
        
        with pytest.raises(KeyError) as excinfo:
            factory.get_serializer('nonexistent')
        
        assert "No serializer found for template type" in str(excinfo.value)