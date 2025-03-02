from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

from rules.models import Rule, RuleGroup, AdvancedRule, RuleEvaluator
from customer_services.models import CustomerService, Service
from customers.models import Customer
from orders.models import Order

class MockOrderData:
    """Mock order data for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class RuleEvaluationTests(TestCase):
    """Test the evaluation of rules with different operators."""
    
    def setUp(self):
        # Create test models
        self.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Legal Name",
            email="test@example.com",
        )
        
        self.service = Service.objects.create(
            service_name="Test Service",
            description="Test service description",
            charge_type="per_order"
        )
        
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('10.00')
        )
        
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        # Create a mock order for testing
        self.order = MockOrderData(
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
        
        # Create the rule evaluator
        self.evaluator = RuleEvaluator()
        
    def test_basic_rule_eq_operator(self):
        """Test a basic rule with the 'eq' operator."""
        # Create a rule that should match
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field="ship_to_country",
            operator="eq",
            value="US",
            adjustment_amount=Decimal('5.00')
        )
        
        # Test the evaluation
        self.assertTrue(
            self.evaluator.evaluate_rule(rule, self.order),
            "Rule with eq operator should match when values are equal"
        )
        
        # Change the rule to one that should not match
        rule.value = "CA"
        rule.save()
        
        # Test the evaluation
        self.assertFalse(
            self.evaluator.evaluate_rule(rule, self.order),
            "Rule with eq operator should not match when values are different"
        )
        
    def test_basic_rule_ne_operator(self):
        """Test a basic rule with the 'ne' operator."""
        # Create a rule that should match (ship_to_country is not 'CA')
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field="ship_to_country",
            operator="ne",
            value="CA",
            adjustment_amount=Decimal('5.00')
        )
        
        # Test the evaluation
        self.assertTrue(
            self.evaluator.evaluate_rule(rule, self.order),
            "Rule with ne operator should match when values are different"
        )
        
        # Change the rule to one that should not match (ship_to_country is not 'US')
        rule.value = "US"
        rule.save()
        
        # Test the evaluation
        self.assertFalse(
            self.evaluator.evaluate_rule(rule, self.order),
            "Rule with ne operator should not match when values are the same"
        )
        
    def test_advanced_rule_with_ne_operator(self):
        """Test an advanced rule with a 'ne' operator and additional conditions."""
        # Create an advanced rule
        rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            field="ship_to_country",
            operator="ne",
            value="CA",
            adjustment_amount=Decimal('5.00'),
            conditions={
                "weight_lb": {"gt": "5"}
            },
            calculations=[
                {"type": "flat_fee", "value": "10.00"}
            ]
        )
        
        # Test the evaluation
        self.assertTrue(
            self.evaluator.evaluate_rule(rule, self.order),
            "Advanced rule with ne operator should match when base condition and additional conditions are met"
        )
        
        # Change the additional condition to one that should not match
        rule.conditions = {"weight_lb": {"gt": "20"}}
        rule.save()
        
        # Test the evaluation
        self.assertFalse(
            self.evaluator.evaluate_rule(rule, self.order),
            "Advanced rule should not match when additional conditions are not met"
        )
        
        # Change the base condition to one that should not match
        rule.value = "US"
        rule.conditions = {"weight_lb": {"gt": "5"}}
        rule.save()
        
        # Test the evaluation
        self.assertFalse(
            self.evaluator.evaluate_rule(rule, self.order),
            "Advanced rule should not match when the base condition is not met"
        )
        
    def test_rule_group_evaluation(self):
        """Test the evaluation of a rule group with multiple rules."""
        # Create three rules in the group
        rule1 = Rule.objects.create(
            rule_group=self.rule_group,
            field="ship_to_country",
            operator="eq",
            value="US",
            adjustment_amount=Decimal('5.00')
        )
        
        rule2 = Rule.objects.create(
            rule_group=self.rule_group,
            field="weight_lb",
            operator="gt",
            value="5",
            adjustment_amount=Decimal('3.00')
        )
        
        rule3 = Rule.objects.create(
            rule_group=self.rule_group,
            field="ship_to_state",
            operator="ne",
            value="CA",
            adjustment_amount=Decimal('2.00')
        )
        
        # Test with AND logic (all rules must match)
        self.rule_group.logic_operator = 'AND'
        self.rule_group.save()
        
        # All rules match
        self.assertTrue(
            self.rule_group.evaluate(self.order),
            "Rule group with AND logic should match when all rules match"
        )
        
        # Change one rule to not match
        rule1.value = "CA"
        rule1.save()
        
        # Not all rules match
        self.assertFalse(
            self.rule_group.evaluate(self.order),
            "Rule group with AND logic should not match when not all rules match"
        )
        
        # Test with OR logic (any rule must match)
        self.rule_group.logic_operator = 'OR'
        self.rule_group.save()
        
        # Some rules match
        self.assertTrue(
            self.rule_group.evaluate(self.order),
            "Rule group with OR logic should match when at least one rule matches"
        )
        
        # Change all rules to not match
        rule2.value = "20"
        rule2.save()
        rule3.value = "NY"
        rule3.save()
        
        # No rules match
        self.assertFalse(
            self.rule_group.evaluate(self.order),
            "Rule group with OR logic should not match when no rules match"
        )