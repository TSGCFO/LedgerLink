"""
Tests for rule model validations and edge cases.
"""

import pytest
from django.core.exceptions import ValidationError

from rules.models import BasicRule
from test_utils.factories import BasicRuleFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestBasicRuleModel:
    """Tests for the BasicRule model."""

    def test_basic_rule_creation(self, test_user):
        """Test that a basic rule can be created with valid data."""
        rule = BasicRuleFactory(
            name="Test Rule",
            description="Test rule description",
            field="product__price",
            operator="greater_than",
            value="100",
            created_by=test_user
        )
        assert rule.pk is not None
        assert rule.name == "Test Rule"
        assert rule.field == "product__price"
        assert rule.operator == "greater_than"
        assert rule.value == "100"
        assert rule.created_by == test_user

    def test_rule_str_representation(self):
        """Test the string representation of a rule."""
        rule = BasicRuleFactory(name="Test Rule")
        assert str(rule) == "Test Rule"

    def test_rule_without_name_invalid(self, test_user):
        """Test that a rule without a name is invalid."""
        rule = BasicRule(
            field="product__price",
            operator="greater_than",
            value="100",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_rule_without_field_invalid(self, test_user):
        """Test that a rule without a field is invalid."""
        rule = BasicRule(
            name="Test Rule",
            operator="greater_than",
            value="100",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_rule_without_operator_invalid(self, test_user):
        """Test that a rule without an operator is invalid."""
        rule = BasicRule(
            name="Test Rule",
            field="product__price",
            value="100",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_rule_with_invalid_operator(self, test_user):
        """Test that a rule with an invalid operator is invalid."""
        rule = BasicRule(
            name="Test Rule",
            field="product__price",
            operator="invalid_operator",  # Invalid operator
            value="100",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_rule_without_value(self, test_user):
        """Test that a rule can be created without a value for certain operators."""
        # For operators like 'is_null', value can be empty
        rule = BasicRuleFactory(
            field="product__price",
            operator="is_null",
            value="",
            created_by=test_user
        )
        rule.full_clean()  # Should not raise

    def test_rule_value_required_for_most_operators(self, test_user):
        """Test that a value is required for most operators."""
        rule = BasicRule(
            name="Test Rule",
            field="product__price",
            operator="greater_than",  # Requires a value
            value="",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_rule_numeric_operators_require_numeric_values(self, test_user):
        """Test that numeric operators require numeric values."""
        # Valid numeric value
        rule1 = BasicRuleFactory(
            field="product__price",
            operator="greater_than",
            value="100.5",
            created_by=test_user
        )
        rule1.full_clean()  # Should not raise

        # Invalid non-numeric value
        rule2 = BasicRule(
            name="Invalid Rule",
            field="product__price",
            operator="greater_than",
            value="not-a-number",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule2.full_clean()

    def test_rule_date_operators_require_date_values(self, test_user):
        """Test that date operators require date values."""
        # Valid date value
        rule1 = BasicRuleFactory(
            field="order__order_date",
            operator="before",
            value="2023-01-01",
            created_by=test_user
        )
        rule1.full_clean()  # Should not raise

        # Invalid date value
        rule2 = BasicRule(
            name="Invalid Date Rule",
            field="order__order_date",
            operator="before",
            value="not-a-date",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            rule2.full_clean()