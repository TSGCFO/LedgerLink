from django.test import TestCase
from rules.views import evaluate_condition

class MockOrder:
    """A mock order class for testing condition evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ConditionEvaluatorTests(TestCase):
    """Test suite for the evaluate_condition function."""

    def test_equals_operator(self):
        """Test the 'eq' operator."""
        # Test with string values
        order = MockOrder(ship_to_country="US")
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'eq', 'US'))
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'eq', 'CA'))

        # Test with numeric values
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'eq', '10'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'eq', '10.0'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'eq', 10))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'eq', '11'))

        # Test with empty values
        order = MockOrder(notes="")
        self.assertTrue(evaluate_condition(order, 'notes', 'eq', ''))
        self.assertFalse(evaluate_condition(order, 'notes', 'eq', 'any'))

    def test_not_equals_operator(self):
        """Test the 'ne' operator."""
        # Test with string values
        order = MockOrder(ship_to_country="US")
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'ne', 'CA'))
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'ne', 'US'))

        # Ensure the 'neq' alias works too (for backward compatibility)
        self.assertTrue(evaluate_condition(order, 'ship_to_country', 'neq', 'CA'))
        self.assertFalse(evaluate_condition(order, 'ship_to_country', 'neq', 'US'))

        # Test with numeric values
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'ne', '11'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'ne', '10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'ne', 10))

        # Test with empty values
        order = MockOrder(notes="")
        self.assertTrue(evaluate_condition(order, 'notes', 'ne', 'any'))
        self.assertFalse(evaluate_condition(order, 'notes', 'ne', ''))

    def test_greater_than_operator(self):
        """Test the 'gt' operator."""
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'gt', '9'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'gt', 9))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'gt', '10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'gt', '11'))

        # Edge case: string that looks like a number
        order = MockOrder(reference_number="100")
        self.assertTrue(evaluate_condition(order, 'reference_number', 'gt', '50'))
        self.assertFalse(evaluate_condition(order, 'reference_number', 'gt', '200'))

    def test_greater_than_or_equals_operator(self):
        """Test the 'gte' operator."""
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'gte', '9'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'gte', '10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'gte', '11'))

    def test_less_than_operator(self):
        """Test the 'lt' operator."""
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'lt', '11'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'lt', '10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'lt', '9'))

    def test_less_than_or_equals_operator(self):
        """Test the 'lte' operator."""
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'lte', '11'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'lte', '10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'lte', '9'))

    def test_contains_operator(self):
        """Test the 'contains' operator."""
        order = MockOrder(notes="This is a test note")
        self.assertTrue(evaluate_condition(order, 'notes', 'contains', 'test'))
        self.assertFalse(evaluate_condition(order, 'notes', 'contains', 'missing'))

        # Case insensitivity
        self.assertTrue(evaluate_condition(order, 'notes', 'contains', 'TEST'))
        self.assertTrue(evaluate_condition(order, 'notes', 'contains', 'Test'))

    def test_not_contains_operator(self):
        """Test the 'not_contains' operator."""
        order = MockOrder(notes="This is a test note")
        self.assertTrue(evaluate_condition(order, 'notes', 'not_contains', 'missing'))
        self.assertFalse(evaluate_condition(order, 'notes', 'not_contains', 'test'))

        # Case insensitivity
        self.assertFalse(evaluate_condition(order, 'notes', 'not_contains', 'TEST'))

    def test_edge_cases(self):
        """Test various edge cases."""
        # Missing field
        order = MockOrder(weight_lb="10")
        self.assertFalse(evaluate_condition(order, 'missing_field', 'eq', 'any'))

        # None value
        order = MockOrder(notes=None)
        self.assertFalse(evaluate_condition(order, 'notes', 'eq', 'any'))
        self.assertFalse(evaluate_condition(order, 'notes', 'ne', 'any'))

        # Invalid operator
        order = MockOrder(weight_lb="10")
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'invalid_op', '10'))

        # Type conversion issues
        order = MockOrder(weight_lb="not_a_number")
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'gt', '5'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'eq', 'not_a_number'))

        # Empty string vs None
        order = MockOrder(notes="")
        self.assertFalse(evaluate_condition(order, 'notes', 'eq', None))
        self.assertTrue(evaluate_condition(order, 'notes', 'ne', None))

    def test_empty_values(self):
        """Test handling of empty and zero values."""
        # Zero values
        order = MockOrder(weight_lb="0")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'eq', '0'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'eq', 0))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'gt', '0'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'lte', '0'))

        # Empty string
        order = MockOrder(notes="")
        self.assertTrue(evaluate_condition(order, 'notes', 'eq', ''))
        self.assertFalse(evaluate_condition(order, 'notes', 'contains', 'anything'))

    def test_between_operator(self):
        """Test the 'between' operator."""
        order = MockOrder(weight_lb="10")
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'between', '5,15'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'between', '10,15'))
        self.assertTrue(evaluate_condition(order, 'weight_lb', 'between', '5,10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'between', '11,15'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'between', '5,9'))

        # Invalid range format
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'between', '10'))
        self.assertFalse(evaluate_condition(order, 'weight_lb', 'between', '5,10,15'))

    def test_json_field_conditions(self):
        """Test conditions on JSON fields."""
        # Test SKU quantity as JSON
        order = MockOrder(sku_quantity='{"SKU-123": 2, "SKU-456": 3}')
        
        # Contains SKU
        self.assertTrue(evaluate_condition(order, 'sku_quantity', 'contains', 'SKU-123'))
        self.assertFalse(evaluate_condition(order, 'sku_quantity', 'contains', 'SKU-789'))
        
        # Not contains SKU
        self.assertTrue(evaluate_condition(order, 'sku_quantity', 'not_contains', 'SKU-789'))
        self.assertFalse(evaluate_condition(order, 'sku_quantity', 'not_contains', 'SKU-123'))

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