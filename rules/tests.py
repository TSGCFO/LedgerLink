from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

from .models import Rule, RuleGroup, AdvancedRule
from .forms import RuleForm
from .utils.validators import validate_calculation
from customer_services.models import CustomerService
from customers.models import Customer
from orders.models import Order, OrderSKUView

class RuleTests(TestCase):
    def setUp(self):
        # Create test customer and customer service
        self.customer = Customer.objects.create(
            company_name="Test Company"
        )
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service_name="Test Service"
        )
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )

    def test_sku_name_rule(self):
        # Test SKU name rule creation and validation
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_name',
            operator='eq',
            value='TEST-SKU'
        )
        self.assertEqual(rule.field, 'sku_name')
        self.assertEqual(rule.value, 'TEST-SKU')

        # Test invalid operator for SKU name
        with self.assertRaises(ValidationError):
            rule.operator = 'gt'
            rule.clean()

    def test_sku_count_rule(self):
        # Test SKU count rule creation and validation
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_count',
            operator='gt',
            value='5'
        )
        self.assertEqual(rule.field, 'sku_count')
        self.assertEqual(rule.value, '5')

        # Test string value for SKU count
        with self.assertRaises(ValidationError):
            rule.value = 'invalid'
            rule.clean()

    def test_rule_form_sku_name(self):
        # Test form validation for SKU name
        form_data = {
            'rule_group': self.rule_group.id,
            'field': 'sku_name',
            'operator': 'contains',
            'value': 'TEST'
        }
        form = RuleForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid operator for SKU name
        form_data['operator'] = 'gt'
        form = RuleForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_rule_form_sku_count(self):
        # Test form validation for SKU count
        form_data = {
            'rule_group': self.rule_group.id,
            'field': 'sku_count',
            'operator': 'gt',
            'value': '5'
        }
        form = RuleForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid value for SKU count
        form_data['value'] = 'invalid'
        form = RuleForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_rule_evaluation(self):
        # Create test order with SKU view data
        order = Order.objects.create(
            transaction_id=1,
            customer=self.customer,
            reference_number='TEST-ORDER'
        )
        order_sku = OrderSKUView.objects.create(
            transaction_id=1,
            customer=self.customer,
            reference_number='TEST-ORDER',
            sku_name='TEST-SKU',
            sku_count=10
        )

        # Test SKU name rule evaluation
        name_rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_name',
            operator='eq',
            value='TEST-SKU'
        )
        self.assertTrue(name_rule.evaluate(order_sku))

        # Test SKU count rule evaluation
        count_rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_count',
            operator='gt',
            value='5'
        )
        self.assertTrue(count_rule.evaluate(order_sku))


class CaseBasedTierTestCase(TestCase):
    def setUp(self):
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com",
            is_active=True
        )
        
        # Create test customer service
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service_name="Test Service",
            description="Test service description"
        )
        
        # Create rule group
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator="AND"
        )
        
        # Create test order for evaluating rules
        self.order = Order.objects.create(
            transaction_id="TEST123",
            reference_number="REF123",
            ship_to_name="Test Ship",
            ship_to_company="Test Ship Co",
            ship_to_address1="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_country="Test Country",
            ship_to_zip="12345",
            weight_lb=10.5,
            volume_cuft=2.5,
            total_item_qty=20,
            sku_count=3,
            line_items=3,
            sku_quantity=json.dumps({
                "SKU1": {"quantity": 5, "cases": 2},
                "SKU2": {"quantity": 10, "cases": 3},
                "SKU3": {"quantity": 5, "cases": 1}
            })
        )
        
    def test_case_based_tier_validation(self):
        """Test validation for case-based tier configuration"""
        # Valid tier configuration
        valid_tier_config = {
            "ranges": [
                {"min": 1, "max": 3, "multiplier": 1.0},
                {"min": 4, "max": 6, "multiplier": 2.0},
                {"min": 7, "max": 10, "multiplier": 3.0}
            ],
            "excluded_skus": ["SKU3"]
        }
        
        # Test valid configuration
        is_valid, _ = validate_calculation(
            'case_based_tier', 
            {'value': 1.0}, 
            valid_tier_config
        )
        self.assertTrue(is_valid)
        
        # Test missing ranges
        invalid_config_1 = {
            "excluded_skus": ["SKU3"]
        }
        is_valid, error = validate_calculation(
            'case_based_tier', 
            {'value': 1.0}, 
            invalid_config_1
        )
        self.assertFalse(is_valid)
        self.assertEqual(error, "ranges are required in tier_config")
        
        # Test invalid min/max relationship
        invalid_config_2 = {
            "ranges": [
                {"min": 5, "max": 3, "multiplier": 1.0},  # min > max
            ],
            "excluded_skus": []
        }
        is_valid, error = validate_calculation(
            'case_based_tier', 
            {'value': 1.0}, 
            invalid_config_2
        )
        self.assertFalse(is_valid)
        self.assertTrue("Min value (5) cannot be greater than max value (3)" in error)
        
        # Test missing required fields
        invalid_config_3 = {
            "ranges": [
                {"min": 1, "multiplier": 1.0},  # missing max
            ],
        }
        is_valid, error = validate_calculation(
            'case_based_tier', 
            {'value': 1.0}, 
            invalid_config_3
        )
        self.assertFalse(is_valid)
        self.assertEqual(error, "Each tier must have min, max, and multiplier")
    
    def test_advanced_rule_model_validation(self):
        """Test the AdvancedRule model validation"""
        # Create a valid advanced rule with case-based tier
        rule = AdvancedRule(
            rule_group=self.rule_group,
            field="sku_quantity",
            operator="contains",
            value="SKU1",
            calculations=[
                {"type": "case_based_tier", "value": 1.0}
            ],
            tier_config={
                "ranges": [
                    {"min": 1, "max": 3, "multiplier": 1.0},
                    {"min": 4, "max": 6, "multiplier": 2.0},
                    {"min": 7, "max": 10, "multiplier": 3.0}
                ],
                "excluded_skus": ["SKU3"]
            }
        )
        
        # Should not raise ValidationError
        try:
            rule.full_clean()
            rule.save()
        except ValidationError as e:
            self.fail(f"ValidationError was raised: {e}")
            
        # Invalid tier config (min > max)
        invalid_rule = AdvancedRule(
            rule_group=self.rule_group,
            field="sku_quantity",
            operator="contains",
            value="SKU1",
            calculations=[
                {"type": "case_based_tier", "value": 1.0}
            ],
            tier_config={
                "ranges": [
                    {"min": 5, "max": 3, "multiplier": 1.0},
                ],
                "excluded_skus": []
            }
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            invalid_rule.full_clean()
    
    def test_case_based_tier_evaluation(self):
        """Test the evaluation of case-based tiers"""
        # Create a rule with excluded SKU3
        rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            field="sku_quantity",
            operator="contains",
            value="SKU1",
            calculations=[
                {"type": "case_based_tier", "value": 1.0}
            ],
            tier_config={
                "ranges": [
                    {"min": 1, "max": 3, "multiplier": 1.0},
                    {"min": 4, "max": 6, "multiplier": 2.0},
                    {"min": 7, "max": 10, "multiplier": 3.0}
                ],
                "excluded_skus": ["SKU3"]
            }
        )
        
        # Total cases: SKU1 (2) + SKU2 (3) = 5 cases (excluding SKU3)
        # This should match the second tier (4-6 cases)
        
        # Base amount
        base_amount = Decimal('100.00')
        
        # Apply adjustment - should use the multiplier from the matching tier
        adjusted_amount = rule.apply_adjustment(self.order, base_amount)
        
        # Expected: base amount * multiplier from second tier (2.0)
        expected_amount = base_amount * Decimal('2.0')
        
        self.assertEqual(adjusted_amount, expected_amount)
        
    def test_validation_consistency(self):
        """Test that validation works consistently across frontend and backend"""
        # These test cases should match the ones in 
        # frontend/src/components/rules/core/__tests__/AdvancedRuleValidation.test.js
        
        # 1. Valid configuration
        valid_calculation = {
            'type': 'case_based_tier',
            'value': 1.0
        }
        valid_tier_config = {
            'ranges': [
                {'min': 1, 'max': 3, 'multiplier': 1.0},
                {'min': 4, 'max': 6, 'multiplier': 2.0},
                {'min': 7, 'max': 10, 'multiplier': 3.0}
            ],
            'excluded_skus': ['SKU3']
        }
        is_valid, _ = validate_calculation('case_based_tier', valid_calculation, valid_tier_config)
        self.assertTrue(is_valid)
        
        # 2. Missing ranges array
        invalid_config_1 = {
            'excluded_skus': ['SKU3']
        }
        is_valid, error = validate_calculation('case_based_tier', valid_calculation, invalid_config_1)
        self.assertFalse(is_valid)
        self.assertIn('ranges', error.lower())
        
        # 3. Invalid min/max relationship
        invalid_config_2 = {
            'ranges': [
                {'min': 5, 'max': 3, 'multiplier': 1.0}, # min > max
            ],
            'excluded_skus': []
        }
        is_valid, error = validate_calculation('case_based_tier', valid_calculation, invalid_config_2)
        self.assertFalse(is_valid)
        self.assertIn('min value (5) cannot be greater than max value (3)', error.lower())
        
        # 4. Missing required fields
        invalid_config_3 = {
            'ranges': [
                {'min': 1, 'multiplier': 1.0},  # missing max
            ],
        }
        is_valid, error = validate_calculation('case_based_tier', valid_calculation, invalid_config_3)
        self.assertFalse(is_valid)
        self.assertIn('must have min, max, and multiplier', error.lower())
        
        # 5. Negative values
        invalid_config_4 = {
            'ranges': [
                {'min': -1, 'max': 3, 'multiplier': 1.0},  # negative min
            ],
            'excluded_skus': []
        }
        is_valid, error = validate_calculation('case_based_tier', valid_calculation, invalid_config_4)
        self.assertFalse(is_valid)
        self.assertIn('must be non-negative', error.lower())
        
        # 6. Invalid excluded_skus format
        invalid_config_5 = {
            'ranges': [
                {'min': 1, 'max': 3, 'multiplier': 1.0},
            ],
            'excluded_skus': 'SKU1,SKU2'  # should be list
        }
        is_valid, error = validate_calculation('case_based_tier', valid_calculation, invalid_config_5)
        self.assertFalse(is_valid)
        self.assertIn('excluded_skus must be a list', error.lower())
