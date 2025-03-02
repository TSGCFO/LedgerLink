#!/usr/bin/env python
"""
Standalone test for the billing calculator's rule evaluator.
This script tests the operator handling in billing/billing_calculator.py without requiring Django.
"""

import unittest
from unittest.mock import Mock

class MockOrder:
    """Mock order for testing rule evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Mock normalize_sku function for testing
def normalize_sku(sku):
    if not sku:
        return ''
    return ''.join(str(sku).split()).upper()

class RuleEvaluator:
    """Simplified version of the RuleEvaluator class from billing_calculator.py"""
    
    @staticmethod
    def evaluate_rule(rule, order):
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
                    elif rule.operator == 'ne' or rule.operator == 'neq':  # Support both 'ne' and 'neq'
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
                elif rule.operator == 'ne' or rule.operator == 'neq':  # Support both 'ne' and 'neq'
                    return field_value != values[0]
                elif rule.operator == 'in':
                    return field_value in values
                elif rule.operator == 'ni':
                    return field_value not in values
                elif rule.operator == 'contains':
                    return any(v.lower() in field_value.lower() for v in values)
                elif rule.operator == 'ncontains' or rule.operator == 'not_contains':  # Support both variants
                    return all(v.lower() not in field_value.lower() for v in values)
                elif rule.operator == 'startswith':
                    return any(field_value.startswith(v) for v in values)
                elif rule.operator == 'endswith':
                    return any(field_value.endswith(v) for v in values)

            # Handle SKU quantity - simplified for testing
            if rule.field == 'sku_quantity':
                if rule.operator == 'contains':
                    return values[0].lower() in field_value.lower()
                elif rule.operator == 'ncontains' or rule.operator == 'not_contains':  # Support both variants
                    return values[0].lower() not in field_value.lower()

            return False
        except Exception as e:
            print(f"Error evaluating rule: {str(e)}")
            return False


class RuleEvaluatorTests(unittest.TestCase):
    """Tests for the RuleEvaluator class."""
    
    def setUp(self):
        # Create a mock rule
        self.mock_rule = Mock()
        self.mock_rule.field = None
        self.mock_rule.operator = None
        self.mock_rule.value = None
        self.mock_rule.get_values_as_list = lambda: [self.mock_rule.value]
    
    def test_numeric_ne_operator(self):
        """Test the 'ne' operator on numeric fields."""
        # Setup
        self.mock_rule.field = 'weight_lb'
        self.mock_rule.value = '15'
        
        # Test 'ne' operator
        self.mock_rule.operator = 'ne'
        order = MockOrder(weight_lb='10')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(weight_lb='15')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        # Test 'neq' operator (alias for 'ne')
        self.mock_rule.operator = 'neq'
        order = MockOrder(weight_lb='10')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(weight_lb='15')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
    
    def test_string_ne_operator(self):
        """Test the 'ne' operator on string fields."""
        # Setup
        self.mock_rule.field = 'ship_to_country'
        self.mock_rule.value = 'US'
        
        # Test 'ne' operator
        self.mock_rule.operator = 'ne'
        order = MockOrder(ship_to_country='CA')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(ship_to_country='US')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        # Test 'neq' operator (alias for 'ne')
        self.mock_rule.operator = 'neq'
        order = MockOrder(ship_to_country='CA')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(ship_to_country='US')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
    
    def test_string_ncontains_operator(self):
        """Test the 'ncontains' operator on string fields."""
        # Setup
        self.mock_rule.field = 'ship_to_country'
        self.mock_rule.value = 'US'
        
        # Test 'ncontains' operator
        self.mock_rule.operator = 'ncontains'
        order = MockOrder(ship_to_country='Canada')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order), 
                      "Canada should not contain 'US'")
        
        # Test with a country that actually contains "US" as a substring
        order = MockOrder(ship_to_country='USA')
        result = RuleEvaluator.evaluate_rule(self.mock_rule, order)
        self.assertFalse(result, 
                       "USA should contain 'US' as a substring")
        
        # Test 'not_contains' operator (alias for 'ncontains')
        self.mock_rule.operator = 'not_contains'
        order = MockOrder(ship_to_country='Canada')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order), 
                      "Canada should not contain 'US'")
        
        order = MockOrder(ship_to_country='USA')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order), 
                       "USA should contain 'US' as a substring")
    
    def test_sku_quantity_ncontains_operator(self):
        """Test the 'ncontains' operator on SKU quantity."""
        # Setup
        self.mock_rule.field = 'sku_quantity'
        self.mock_rule.value = 'SKU-123'
        
        # Test 'ncontains' operator
        self.mock_rule.operator = 'ncontains'
        order = MockOrder(sku_quantity='{"SKU-456": 2, "SKU-789": 3}')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(sku_quantity='{"SKU-123": 2, "SKU-456": 3}')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        # Test 'not_contains' operator (alias for 'ncontains')
        self.mock_rule.operator = 'not_contains'
        order = MockOrder(sku_quantity='{"SKU-456": 2, "SKU-789": 3}')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(sku_quantity='{"SKU-123": 2, "SKU-456": 3}')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))


if __name__ == "__main__":
    unittest.main()