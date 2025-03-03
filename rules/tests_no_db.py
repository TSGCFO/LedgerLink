from django.test import SimpleTestCase
from rules.views import evaluate_condition

class MockOrder:
    """A mock order class for testing condition evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ConditionEvaluatorSimpleTests(SimpleTestCase):
    """Test suite for the evaluate_condition function that doesn't require a database."""

    def test_equals_operator(self):
        """Test the 'eq' operator."""
        # Test with string values
        order = MockOrder(ship_to_country="US")
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'eq', 'US'))
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'eq', 'CA'))

    def test_not_equals_operator(self):
        """Test the 'ne' operator."""
        # Test with string values
        order = MockOrder(ship_to_country="US")
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'ne', 'CA'))
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'ne', 'US'))
        
        # Ensure the 'neq' alias works too (for backward compatibility)
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'neq', 'CA'))
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'neq', 'US'))
        
    def test_rule_tester_example(self):
        """Test the specific example from the rule tester that was failing."""
        # The test case from the prompt
        order = MockOrder(
            weight_lb="10",
            total_item_qty="5",
            packages="1",
            line_items="2",
            volume_cuft="2.5",
            reference_number="ORD-12345",
            ship_to_name="John Doe",
            ship_to_company="ACME Corp",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_country="US",
            carrier="UPS",
            sku_quantity='{"SKU-123": 2, "SKU-456": 3}',
            notes="Test order notes"
        )
        
        # This should be TRUE because US is not equal to tom
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'ne', 'tom'))
        
        # And the inverse should be FALSE because US is not equal to tom
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'eq', 'tom'))