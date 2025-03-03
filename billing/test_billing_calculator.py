import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch
import json

from billing.billing_calculator import RuleEvaluator, BillingCalculator, normalize_sku, convert_sku_format

class MockOrder:
    """Mock order object for testing rule evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class RuleEvaluatorTests(unittest.TestCase):
    """Tests for the RuleEvaluator class in billing_calculator.py."""
    
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
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(ship_to_country='United States')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        # Test 'not_contains' operator (alias for 'ncontains')
        self.mock_rule.operator = 'not_contains'
        order = MockOrder(ship_to_country='Canada')
        self.assertTrue(RuleEvaluator.evaluate_rule(self.mock_rule, order))
        
        order = MockOrder(ship_to_country='United States')
        self.assertFalse(RuleEvaluator.evaluate_rule(self.mock_rule, order))
    
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


class SkuUtilsTests(unittest.TestCase):
    """Tests for SKU utility functions."""
    
    def test_normalize_sku(self):
        """Test the normalize_sku function."""
        self.assertEqual(normalize_sku("SKU-123"), "SKU123")
        self.assertEqual(normalize_sku("sku 123"), "SKU123")
        self.assertEqual(normalize_sku("sku-123"), "SKU123")
        self.assertEqual(normalize_sku(None), "")
        self.assertEqual(normalize_sku(""), "")
    
    def test_convert_sku_format(self):
        """Test the convert_sku_format function."""
        # Test with string input
        sku_data = '[{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}]'
        expected = {"SKU123": 2, "SKU456": 3}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with list input
        sku_data = [{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}]
        expected = {"SKU123": 2, "SKU456": 3}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with invalid input
        self.assertEqual(convert_sku_format("invalid"), {})
        self.assertEqual(convert_sku_format(None), {})


if __name__ == "__main__":
    unittest.main()