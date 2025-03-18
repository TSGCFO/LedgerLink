#!/usr/bin/env python
"""
Comprehensive tests for operator handling in the billing calculator.
These tests focus on verifying the correct behavior of various operators
(ne/neq, contains/ncontains/not_contains, etc.) across different field types.

This is a standalone test file that doesn't require the Django environment.
"""

import unittest
from decimal import Decimal
import json
from unittest.mock import Mock, patch

# Mock versions of the functions we want to test
def normalize_sku(sku):
    """Normalize a given SKU by removing spaces/hyphens and converting to uppercase."""
    if not sku:
        return ''
    # Remove spaces and hyphens
    return ''.join(c for c in str(sku) if c not in ' -').upper()

def convert_sku_format(sku_data):
    """Convert SKU data to a normalized dictionary format."""
    try:
        if isinstance(sku_data, str):
            sku_data = json.loads(sku_data)

        if not isinstance(sku_data, list):
            return {}

        sku_dict = {}
        for item in sku_data:
            if not isinstance(item, dict):
                continue

            if 'sku' not in item or 'quantity' not in item:
                continue

            # Normalize SKU format (uses our normalize_sku function)
            sku = normalize_sku(str(item['sku']))
            if not sku:
                continue

            try:
                # Convert to numeric
                quantity = float(item['quantity'])
                if isinstance(item['quantity'], int):
                    quantity = int(quantity)  # Keep integers as integers
            except (TypeError, ValueError):
                continue

            if quantity <= 0:
                continue

            # If the same SKU appears multiple times, add the quantities
            sku_dict[sku] = sku_dict.get(sku, 0) + quantity

        return sku_dict
    except Exception:
        return {}


class RuleEvaluator:
    """Simplified version of the RuleEvaluator class for testing."""
    
    @staticmethod
    def evaluate_rule(rule, order):
        """Evaluate a rule against an order."""
        try:
            field_value = getattr(order, rule.field, None)
            if field_value is None:
                return False

            values = rule.get_values_as_list()

            # Handle numeric fields
            numeric_fields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']
            if rule.field in numeric_fields:
                try:
                    field_value = float(field_value) if field_value is not None else 0
                    value = float(values[0]) if values else 0

                    if rule.operator == 'gt':
                        return field_value > value
                    elif rule.operator == 'lt':
                        return field_value < value
                    elif rule.operator == 'eq':
                        return field_value == value
                    elif rule.operator == 'ne' or rule.operator == 'neq':  # Support both variants
                        return field_value != value
                    elif rule.operator == 'ge':
                        return field_value >= value
                    elif rule.operator == 'le':
                        return field_value <= value
                except (ValueError, TypeError):
                    return False

            # Handle string fields
            string_fields = ['reference_number', 'ship_to_name', 'ship_to_company',
                            'ship_to_city', 'ship_to_state', 'ship_to_country',
                            'carrier', 'notes']
            if rule.field in string_fields:
                field_value = str(field_value) if field_value is not None else ''

                if rule.operator == 'eq':
                    return field_value == values[0]
                elif rule.operator == 'ne' or rule.operator == 'neq':  # Support both variants
                    return field_value != values[0]
                elif rule.operator == 'in':
                    return field_value in values
                elif rule.operator == 'ni':
                    return field_value not in values
                elif rule.operator == 'contains':
                    return any(v in field_value for v in values)
                elif rule.operator == 'ncontains' or rule.operator == 'not_contains':  # Support both variants
                    return not any(v in field_value for v in values)
                elif rule.operator == 'startswith':
                    return any(field_value.startswith(v) for v in values)
                elif rule.operator == 'endswith':
                    return any(field_value.endswith(v) for v in values)

            # Handle SKU quantity
            if rule.field == 'sku_quantity':
                if field_value is None:
                    return False

                try:
                    # For SKU quantity, check if the value is in the SKU list
                    if isinstance(field_value, str):
                        # Try both raw comparison and normalized comparison
                        original_skus = json.loads(field_value) if field_value else []
                        normalized_skus = [normalize_sku(item.get('sku', '')) 
                                          for item in original_skus if isinstance(item, dict)]
                        
                        if rule.operator == 'contains':
                            # Check if the SKU exists either in original format or normalized format
                            for v in values:
                                # Check original format
                                if any(v.lower() in item.get('sku', '').lower() 
                                      for item in original_skus if isinstance(item, dict)):
                                    return True
                                # Check normalized format
                                if normalize_sku(v) in normalized_skus:
                                    return True
                            return False
                        elif rule.operator == 'ncontains' or rule.operator == 'not_contains':
                            # Check if the SKU does NOT exist in either original or normalized format
                            for v in values:
                                # Check original format
                                if any(v.lower() in item.get('sku', '').lower() 
                                      for item in original_skus if isinstance(item, dict)):
                                    return False
                                # Check normalized format
                                if normalize_sku(v) in normalized_skus:
                                    return False
                            return True
                        elif rule.operator == 'in':
                            return any(v.lower() in field_value.lower() for v in values)
                        elif rule.operator == 'ni':
                            return not any(v.lower() in field_value.lower() for v in values)
                    else:
                        # Try to convert to dictionary for proper comparison
                        sku_dict = field_value
                        # Extract normalized SKUs for comparison
                        skus = list(sku_dict.keys()) if isinstance(sku_dict, dict) else []
                        
                        if rule.operator == 'contains':
                            return any(normalize_sku(v) in skus for v in values)
                        elif rule.operator == 'ncontains' or rule.operator == 'not_contains':
                            return not any(normalize_sku(v) in skus for v in values)
                        elif rule.operator == 'in':
                            return any(normalize_sku(v) in str(sku_dict) for v in values)
                        elif rule.operator == 'ni':
                            return not any(normalize_sku(v) in str(sku_dict) for v in values)
                except (json.JSONDecodeError, AttributeError):
                    return False

            return False
        except Exception:
            return False


class MockRule:
    """Mock rule for operator testing."""
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value
        self._values_list = [value] if value is not None else []
    
    def get_values_as_list(self):
        """Return a list of values."""
        return self._values_list


class MockOrder:
    """Mock order for operator testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class NumericOperatorTests(unittest.TestCase):
    """Tests for numeric operators in the rule evaluator."""
    
    def test_equal_operator(self):
        """Test the 'eq' operator on numeric fields."""
        rule = MockRule(field='weight_lb', operator='eq', value='10')
        
        # Test equal value
        order = MockOrder(weight_lb='10')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test different value
        order = MockOrder(weight_lb='15')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with integer vs string
        order = MockOrder(weight_lb=10)
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_not_equal_operator(self):
        """Test the 'ne'/'neq' operators on numeric fields."""
        # Test with 'ne' operator
        rule = MockRule(field='weight_lb', operator='ne', value='10')
        
        order = MockOrder(weight_lb='15')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(weight_lb='10')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with 'neq' operator (alias)
        rule = MockRule(field='weight_lb', operator='neq', value='10')
        
        order = MockOrder(weight_lb='15')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(weight_lb='10')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_greater_than_operator(self):
        """Test the 'gt' operator on numeric fields."""
        rule = MockRule(field='total_item_qty', operator='gt', value='10')
        
        order = MockOrder(total_item_qty='15')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(total_item_qty='10')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(total_item_qty='5')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_less_than_operator(self):
        """Test the 'lt' operator on numeric fields."""
        rule = MockRule(field='line_items', operator='lt', value='10')
        
        order = MockOrder(line_items='5')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(line_items='10')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(line_items='15')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_greater_equal_operator(self):
        """Test the 'ge' operator on numeric fields."""
        rule = MockRule(field='packages', operator='ge', value='10')
        
        order = MockOrder(packages='15')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(packages='10')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(packages='5')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_less_equal_operator(self):
        """Test the 'le' operator on numeric fields."""
        rule = MockRule(field='volume_cuft', operator='le', value='10')
        
        order = MockOrder(volume_cuft='5')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(volume_cuft='10')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(volume_cuft='15')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_numeric_invalid_values(self):
        """Test numeric operators with invalid values."""
        rule = MockRule(field='weight_lb', operator='eq', value='10')
        
        # Test with non-numeric value
        order = MockOrder(weight_lb='not-a-number')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with None value
        order = MockOrder(weight_lb=None)
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))


class StringOperatorTests(unittest.TestCase):
    """Tests for string operators in the rule evaluator."""
    
    def test_equal_operator(self):
        """Test the 'eq' operator on string fields."""
        rule = MockRule(field='ship_to_country', operator='eq', value='US')
        
        # Test equal value
        order = MockOrder(ship_to_country='US')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test different value
        order = MockOrder(ship_to_country='CA')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with case difference
        order = MockOrder(ship_to_country='us')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_not_equal_operator(self):
        """Test the 'ne'/'neq' operators on string fields."""
        # Test with 'ne' operator
        rule = MockRule(field='ship_to_country', operator='ne', value='US')
        
        order = MockOrder(ship_to_country='CA')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_country='US')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with 'neq' operator (alias)
        rule = MockRule(field='ship_to_country', operator='neq', value='US')
        
        order = MockOrder(ship_to_country='CA')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_country='US')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_in_operator(self):
        """Test the 'in' operator on string fields."""
        rule = MockRule(field='ship_to_state', operator='in', value='CA')
        rule._values_list = ['CA', 'NY', 'TX']
        
        order = MockOrder(ship_to_state='CA')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_state='FL')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_not_in_operator(self):
        """Test the 'ni' operator on string fields."""
        rule = MockRule(field='ship_to_state', operator='ni', value='CA')
        rule._values_list = ['CA', 'NY', 'TX']
        
        order = MockOrder(ship_to_state='FL')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_state='CA')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_contains_operator(self):
        """Test the 'contains' operator on string fields."""
        rule = MockRule(field='ship_to_name', operator='contains', value='John')
        
        order = MockOrder(ship_to_name='John Doe')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_name='Jane Smith')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test multiple values
        rule._values_list = ['John', 'Jane']
        
        order = MockOrder(ship_to_name='Jane Smith')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_not_contains_operators(self):
        """Test the 'ncontains'/'not_contains' operators on string fields."""
        # Test with 'ncontains' operator
        rule = MockRule(field='ship_to_name', operator='ncontains', value='John')
        
        order = MockOrder(ship_to_name='Jane Smith')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_name='John Doe')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with 'not_contains' operator (alias)
        rule = MockRule(field='ship_to_name', operator='not_contains', value='John')
        
        order = MockOrder(ship_to_name='Jane Smith')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_name='John Doe')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test multiple values
        rule._values_list = ['John', 'Jane']
        
        order = MockOrder(ship_to_name='Bob Smith')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(ship_to_name='Jane Smith')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_startswith_operator(self):
        """Test the 'startswith' operator on string fields."""
        rule = MockRule(field='reference_number', operator='startswith', value='ORD')
        
        order = MockOrder(reference_number='ORD-12345')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(reference_number='REF-12345')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_endswith_operator(self):
        """Test the 'endswith' operator on string fields."""
        rule = MockRule(field='carrier', operator='endswith', value='Express')
        
        order = MockOrder(carrier='FedEx Express')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        order = MockOrder(carrier='UPS Ground')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_string_null_values(self):
        """Test string operators with null values."""
        rule = MockRule(field='notes', operator='eq', value='Important')
        
        # Test with None value
        order = MockOrder(notes=None)
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with empty string
        rule = MockRule(field='notes', operator='eq', value='')
        order = MockOrder(notes='')
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))


class SKUQuantityOperatorTests(unittest.TestCase):
    """Tests for SKU quantity operators in the rule evaluator."""
    
    def setUp(self):
        """Set up test data."""
        self.sku_json = json.dumps([
            {"sku": "SKU-001", "quantity": 10},
            {"sku": "SKU-002", "quantity": 5}
        ])
        self.sku_dict = {
            "SKU001": 10,
            "SKU002": 5
        }
    
    def test_contains_operator(self):
        """Test the 'contains' operator on SKU quantity."""
        rule = MockRule(field='sku_quantity', operator='contains', value='SKU-001')
        
        order = MockOrder(sku_quantity=self.sku_json)
        # Debug print
        print(f"SKU JSON: {self.sku_json}")
        print(f"Testing contains operator with value: {rule.value}")
        result = RuleEvaluator.evaluate_rule(rule, order)
        print(f"Result: {result}")
        self.assertTrue(result)
        
        # Test with normalized SKU
        rule = MockRule(field='sku_quantity', operator='contains', value='SKU001')
        print(f"Testing contains operator with normalized value: {rule.value}")
        result = RuleEvaluator.evaluate_rule(rule, order)
        print(f"Result: {result}")
        self.assertTrue(result)
        
        # Test with non-existent SKU
        rule = MockRule(field='sku_quantity', operator='contains', value='SKU-999')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_not_contains_operators(self):
        """Test the 'ncontains'/'not_contains' operators on SKU quantity."""
        # Test with 'ncontains' operator
        rule = MockRule(field='sku_quantity', operator='ncontains', value='SKU-999')
        
        order = MockOrder(sku_quantity=self.sku_json)
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        rule = MockRule(field='sku_quantity', operator='ncontains', value='SKU-001')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with 'not_contains' operator (alias)
        rule = MockRule(field='sku_quantity', operator='not_contains', value='SKU-999')
        
        order = MockOrder(sku_quantity=self.sku_json)
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        rule = MockRule(field='sku_quantity', operator='not_contains', value='SKU-001')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_in_operator(self):
        """Test the 'in' operator on SKU quantity."""
        rule = MockRule(field='sku_quantity', operator='in', value='SKU-001')
        
        order = MockOrder(sku_quantity=self.sku_json)
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        rule = MockRule(field='sku_quantity', operator='in', value='SKU-999')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_not_in_operator(self):
        """Test the 'ni' operator on SKU quantity."""
        rule = MockRule(field='sku_quantity', operator='ni', value='SKU-999')
        
        order = MockOrder(sku_quantity=self.sku_json)
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))
        
        rule = MockRule(field='sku_quantity', operator='ni', value='SKU-001')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
    
    def test_with_invalid_sku_format(self):
        """Test SKU operators with invalid SKU format."""
        rule = MockRule(field='sku_quantity', operator='contains', value='SKU-001')
        
        # Test with invalid JSON
        order = MockOrder(sku_quantity='not valid json')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with empty SKU list
        order = MockOrder(sku_quantity='[]')
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))
        
        # Test with None value
        order = MockOrder(sku_quantity=None)
        self.assertFalse(RuleEvaluator.evaluate_rule(rule, order))


class SKUUtilityTests(unittest.TestCase):
    """Tests for SKU utility functions."""
    
    def test_normalize_sku(self):
        """Test normalize_sku function."""
        # Test removing spaces
        self.assertEqual('SKU123', normalize_sku('SKU 123'))
        
        # Test removing hyphens
        self.assertEqual('SKU123', normalize_sku('SKU-123'))
        
        # Test uppercase conversion
        self.assertEqual('SKU123', normalize_sku('sku-123'))
        
        # Test with mixed formats
        self.assertEqual('SKU123XYZ', normalize_sku('Sku-123 XYZ'))
        
        # Test with empty and None values
        self.assertEqual('', normalize_sku(''))
        self.assertEqual('', normalize_sku(None))
        
        # Test with non-string values
        self.assertEqual('123', normalize_sku(123))
    
    def test_convert_sku_format(self):
        """Test convert_sku_format function."""
        # Test with list of dictionaries
        sku_data = [
            {"sku": "SKU-123", "quantity": 5},
            {"sku": "SKU-456", "quantity": 10}
        ]
        expected = {
            "SKU123": 5,
            "SKU456": 10
        }
        self.assertEqual(expected, convert_sku_format(sku_data))
        
        # Test with JSON string
        sku_json = json.dumps(sku_data)
        self.assertEqual(expected, convert_sku_format(sku_json))
        
        # Test with duplicate SKUs (normalization aggregates quantities)
        sku_data = [
            {"sku": "SKU-123", "quantity": 5},
            {"sku": "SKU 123", "quantity": 10}
        ]
        expected = {
            "SKU123": 15
        }
        self.assertEqual(expected, convert_sku_format(sku_data))
        
        # Test with invalid inputs
        self.assertEqual({}, convert_sku_format(None))
        self.assertEqual({}, convert_sku_format("not valid json"))
        self.assertEqual({}, convert_sku_format(123))
    
    def test_convert_sku_format_validation(self):
        """Test convert_sku_format function error handling."""
        # Test with missing keys
        sku_data = [
            {"sku": "SKU-123"},  # Missing quantity
            {"quantity": 10}      # Missing sku
        ]
        self.assertEqual({}, convert_sku_format(sku_data))
        
        # Test with invalid quantity values
        sku_data = [
            {"sku": "SKU-123", "quantity": "not a number"},
            {"sku": "SKU-456", "quantity": -5}
        ]
        self.assertEqual({}, convert_sku_format(sku_data))
        
        # Test with non-list input
        sku_data = {"sku": "SKU-123", "quantity": 5}
        self.assertEqual({}, convert_sku_format(sku_data))


if __name__ == '__main__':
    unittest.main()