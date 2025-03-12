#!/usr/bin/env python
"""
Standalone test for Billing_V2 rule evaluator.
This uses mocks to avoid database connections.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

# Now import the rule evaluator
from Billing_V2.utils.rule_evaluator import RuleEvaluator

class TestRuleEvaluator(unittest.TestCase):
    """Test RuleEvaluator class"""
    
    def setUp(self):
        """Set up test data"""
        # Create mock rule and order for testing
        self.order = MagicMock()
        self.rule = MagicMock()
        self.rule_group = MagicMock()
        
    def test_evaluate_rule_with_numeric_field(self):
        """Test evaluating a rule with a numeric field"""
        # Set up order and rule
        self.order.weight_lb = 100
        self.rule.field = 'weight_lb'
        self.rule.values = [50]
        
        # Test different operators
        self.rule.operator = 'gt'
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        self.rule.operator = 'lt'
        self.assertFalse(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        self.rule.operator = 'eq'
        self.assertFalse(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        self.rule.operator = 'ne'
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        self.rule.operator = 'ge'
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        self.rule.operator = 'le'
        self.assertFalse(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
    def test_evaluate_rule_with_string_field(self):
        """Test evaluating a rule with a string field"""
        # Set up order and rule
        self.order.reference_number = "REF12345"
        self.rule.field = 'reference_number'
        
        # Test equality
        self.rule.operator = 'eq'
        self.rule.values = ["REF12345"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test inequality
        self.rule.operator = 'ne'
        self.rule.values = ["REF54321"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test in list
        self.rule.operator = 'in'
        self.rule.values = ["REF12345", "REF54321"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test not in list
        self.rule.operator = 'ni'
        self.rule.values = ["REF54321", "REF67890"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test contains
        self.rule.operator = 'contains'
        self.rule.values = ["REF"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test not contains
        self.rule.operator = 'not_contains'
        self.rule.values = ["XYZ"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
    def test_evaluate_rule_with_sku_field(self):
        """Test evaluating a rule with a SKU field"""
        # Set up order and rule
        self.order.sku_quantity = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "quantity": 10}
        ]
        self.rule.field = 'sku_quantity'
        
        # Test contains
        self.rule.operator = 'contains'
        self.rule.values = ["ABC123"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test not contains
        self.rule.operator = 'not_contains'
        self.rule.values = ["XYZ789"]
        self.assertTrue(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
        # Test with invalid field
        self.rule.field = 'nonexistent_field'
        self.assertFalse(RuleEvaluator.evaluate_rule(self.rule, self.order))
        
    def test_evaluate_rule_group(self):
        """Test evaluating a rule group"""
        # Create mock rules
        rule1 = MagicMock()
        rule2 = MagicMock()
        
        # Set up rule group with AND logic
        self.rule_group.logic_operator = 'AND'
        self.rule_group.rules.all.return_value = [rule1, rule2]
        
        # Test both rules true
        with patch.object(RuleEvaluator, 'evaluate_rule', side_effect=[True, True]):
            self.assertTrue(RuleEvaluator.evaluate_rule_group(self.rule_group, self.order))
            
        # Test one rule false
        with patch.object(RuleEvaluator, 'evaluate_rule', side_effect=[True, False]):
            self.assertFalse(RuleEvaluator.evaluate_rule_group(self.rule_group, self.order))
            
        # Set up rule group with OR logic
        self.rule_group.logic_operator = 'OR'
        
        # Test one rule true
        with patch.object(RuleEvaluator, 'evaluate_rule', side_effect=[True, False]):
            self.assertTrue(RuleEvaluator.evaluate_rule_group(self.rule_group, self.order))
            
        # Test both rules false
        with patch.object(RuleEvaluator, 'evaluate_rule', side_effect=[False, False]):
            self.assertFalse(RuleEvaluator.evaluate_rule_group(self.rule_group, self.order))
            
        # Test with empty rules
        self.rule_group.rules.all.return_value = []
        self.assertFalse(RuleEvaluator.evaluate_rule_group(self.rule_group, self.order))
        
    def test_evaluate_case_based_rule(self):
        """Test evaluating a case-based tier rule"""
        # Create mock rule and order
        rule = MagicMock()
        order = MagicMock()
        
        # Set up tier configuration
        rule.tier_config = {
            'excluded_skus': ['XYZ789'],
            'ranges': [
                {'min': 0, 'max': 10, 'multiplier': 1.0},
                {'min': 11, 'max': 20, 'multiplier': 0.9},
                {'min': 21, 'max': float('inf'), 'multiplier': 0.8}
            ]
        }
        
        # Set up case summary
        case_summary = {
            'total_cases': 15,
            'sku_breakdown': [
                {'sku_name': 'ABC123', 'cases': 10, 'picks': 5},
                {'sku_name': 'DEF456', 'cases': 5, 'picks': 2}
            ]
        }
        
        # Mock the order methods
        order.get_case_summary.return_value = case_summary
        order.has_only_excluded_skus.return_value = False
        
        # Evaluate the rule
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(rule, order)
        
        # Check results
        self.assertTrue(applies)
        self.assertEqual(multiplier, 0.9)
        self.assertEqual(summary, case_summary)

if __name__ == "__main__":
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRuleEvaluator)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    sys.exit(not result.wasSuccessful())