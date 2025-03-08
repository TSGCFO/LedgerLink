import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from decimal import Decimal
import json

from django.test import TestCase
from django.core.exceptions import ValidationError

from billing.billing_calculator import (
    RuleEvaluator, BillingCalculator, normalize_sku,
    convert_sku_format, validate_sku_quantity,
    ServiceCost, OrderCost, BillingReport, generate_billing_report
)
from .factories import (
    CustomerFactory, OrderFactory, ServiceFactory,
    CustomerServiceFactory, RuleFactory, RuleGroupFactory
)


class MockOrder:
    """Mock order object for testing rule evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get_case_summary(self, exclude_skus=None):
        """Mock implementation of get_case_summary"""
        return {
            'total_cases': getattr(self, 'total_cases', 10),
            'case_details': getattr(self, 'case_details', {}),
        }
    
    def has_only_excluded_skus(self, excluded_skus):
        """Mock implementation of has_only_excluded_skus"""
        return getattr(self, 'only_excluded_skus', False)


class SkuUtilsTests(TestCase):
    """Tests for SKU utility functions."""
    
    def test_normalize_sku(self):
        """Test the normalize_sku function."""
        self.assertEqual(normalize_sku("SKU-123"), "SKU123")
        self.assertEqual(normalize_sku("sku 123"), "SKU123")
        self.assertEqual(normalize_sku("sku-123"), "SKU123")
        self.assertEqual(normalize_sku("sku.123"), "SKU123")
        self.assertEqual(normalize_sku("SKU_123"), "SKU123")
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
        
        # Test with duplicate SKUs that should be combined
        sku_data = [
            {"sku": "SKU-123", "quantity": 2}, 
            {"sku": "SKU-456", "quantity": 3},
            {"sku": "sku 123", "quantity": 5}  # Same as SKU-123 after normalization
        ]
        expected = {"SKU123": 7, "SKU456": 3}  # 2 + 5 = 7 for SKU123
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with negative quantity (should be excluded)
        sku_data = [
            {"sku": "SKU-123", "quantity": 2}, 
            {"sku": "SKU-456", "quantity": -3}
        ]
        expected = {"SKU123": 2}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with zero quantity (should be excluded)
        sku_data = [
            {"sku": "SKU-123", "quantity": 2}, 
            {"sku": "SKU-456", "quantity": 0}
        ]
        expected = {"SKU123": 2}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with missing required fields
        sku_data = [
            {"sku": "SKU-123", "quantity": 2}, 
            {"name": "Invalid item"}
        ]
        expected = {"SKU123": 2}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with invalid input
        self.assertEqual(convert_sku_format("invalid"), {})
        self.assertEqual(convert_sku_format(None), {})
        self.assertEqual(convert_sku_format({}), {})
        self.assertEqual(convert_sku_format(123), {})

    def test_validate_sku_quantity(self):
        """Test the validate_sku_quantity function."""
        # Valid formats
        valid_data = [
            # JSON string format
            '[{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}]',
            # List format
            [{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}]
        ]
        for data in valid_data:
            self.assertTrue(validate_sku_quantity(data))
        
        # Invalid formats
        invalid_data = [
            # Empty SKU
            '[{"sku": "", "quantity": 2}]',
            # Negative quantity
            '[{"sku": "SKU-123", "quantity": -2}]',
            # Zero quantity
            '[{"sku": "SKU-123", "quantity": 0}]',
            # Missing required field
            '[{"sku": "SKU-123"}]',
            '[{"quantity": 2}]',
            # Invalid format
            'invalid',
            None,
            {},
            123
        ]
        for data in invalid_data:
            self.assertFalse(validate_sku_quantity(data))


class RuleEvaluatorTests(TestCase):
    """Tests for the RuleEvaluator class."""
    
    def setUp(self):
        # Create a mock rule
        self.mock_rule = Mock()
        self.mock_rule.field = None
        self.mock_rule.operator = None
        self.mock_rule.value = None
        self.mock_rule.get_values_as_list = lambda: [self.mock_rule.value]
    
    def test_numeric_operators(self):
        """Test numeric field operators."""
        # Setup
        numeric_fields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']
        operators = {
            'gt': (15, [10], True),     # 15 > 10 = True
            'gt': (5, [10], False),     # 5 > 10 = False
            'lt': (5, [10], True),      # 5 < 10 = True
            'lt': (15, [10], False),    # 15 < 10 = False
            'eq': (10, [10], True),     # 10 == 10 = True
            'eq': (5, [10], False),     # 5 == 10 = False
            'ne': (5, [10], True),      # 5 != 10 = True
            'ne': (10, [10], False),    # 10 != 10 = False
            'neq': (5, [10], True),     # 5 != 10 = True (alias for 'ne')
            'ge': (10, [10], True),     # 10 >= 10 = True
            'ge': (15, [10], True),     # 15 >= 10 = True
            'ge': (5, [10], False),     # 5 >= 10 = False
            'le': (10, [10], True),     # 10 <= 10 = True
            'le': (5, [10], True),      # 5 <= 10 = True
            'le': (15, [10], False),    # 15 <= 10 = False
        }
        
        for field in numeric_fields:
            self.mock_rule.field = field
            for operator, (field_value, rule_values, expected) in operators.items():
                self.mock_rule.operator = operator
                self.mock_rule.value = str(rule_values[0])
                order = MockOrder(**{field: str(field_value)})
                result = RuleEvaluator.evaluate_rule(self.mock_rule, order)
                self.assertEqual(result, expected, 
                    f"Failed: {field} {operator} {rule_values} with value {field_value}")
    
    def test_string_operators(self):
        """Test string field operators."""
        # Setup
        string_fields = ['reference_number', 'ship_to_name', 'ship_to_company',
                         'ship_to_city', 'ship_to_state', 'ship_to_country',
                         'carrier', 'notes']
        
        scenarios = [
            # field_value, operator, rule_values, expected
            ('US', 'eq', ['US'], True),
            ('US', 'eq', ['CA'], False),
            ('US', 'ne', ['CA'], True),
            ('US', 'ne', ['US'], False),
            ('US', 'neq', ['CA'], True),
            ('US', 'in', ['CA', 'US', 'MX'], True),
            ('JP', 'in', ['CA', 'US', 'MX'], False),
            ('US', 'ni', ['CA', 'JP', 'MX'], True),
            ('US', 'ni', ['CA', 'US', 'MX'], False),
            ('United States', 'contains', ['State'], True),
            ('United States', 'contains', ['Canada'], False),
            ('United States', 'ncontains', ['Canada'], True),
            ('United States', 'ncontains', ['State'], False),
            ('United States', 'not_contains', ['Canada'], True),
            ('United States', 'startswith', ['United'], True),
            ('United States', 'startswith', ['State'], False),
            ('United States', 'endswith', ['States'], True),
            ('United States', 'endswith', ['United'], False),
        ]
        
        for field in string_fields:
            self.mock_rule.field = field
            for field_value, operator, rule_values, expected in scenarios:
                self.mock_rule.operator = operator
                self.mock_rule.value = rule_values[0]
                self.mock_rule.get_values_as_list = lambda: rule_values
                order = MockOrder(**{field: field_value})
                result = RuleEvaluator.evaluate_rule(self.mock_rule, order)
                self.assertEqual(result, expected,
                    f"Failed: {field_value} {operator} {rule_values}")
    
    def test_sku_quantity_operators(self):
        """Test SKU quantity field operators."""
        self.mock_rule.field = 'sku_quantity'
        
        scenarios = [
            # sku_data, operator, rule_values, expected
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'contains', ['SKU-123'], True),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'contains', ['SKU-789'], False),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'ncontains', ['SKU-789'], True),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'ncontains', ['SKU-123'], False),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'not_contains', ['SKU-789'], True),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'in', ['SKU-123'], True),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'in', ['SKU-789'], False),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'ni', ['SKU-789'], True),
            ([{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}], 
             'ni', ['SKU-123'], False),
        ]
        
        for sku_data, operator, rule_values, expected in scenarios:
            self.mock_rule.operator = operator
            self.mock_rule.value = rule_values[0]
            self.mock_rule.get_values_as_list = lambda: rule_values
            
            # Convert list to JSON string
            sku_json = json.dumps(sku_data)
            order = MockOrder(sku_quantity=sku_json)
            
            result = RuleEvaluator.evaluate_rule(self.mock_rule, order)
            self.assertEqual(result, expected,
                f"Failed: {sku_data} {operator} {rule_values}")
    
    def test_rule_with_missing_field(self):
        """Test rule evaluation with a field that doesn't exist in the order."""
        self.mock_rule.field = 'nonexistent_field'
        self.mock_rule.operator = 'eq'
        self.mock_rule.value = 'value'
        
        order = MockOrder(weight_lb=10)
        result = RuleEvaluator.evaluate_rule(self.mock_rule, order)
        self.assertFalse(result)
    
    def test_invalid_operator(self):
        """Test rule evaluation with an invalid operator."""
        self.mock_rule.field = 'weight_lb'
        self.mock_rule.operator = 'invalid'
        self.mock_rule.value = '10'
        
        order = MockOrder(weight_lb=10)
        result = RuleEvaluator.evaluate_rule(self.mock_rule, order)
        self.assertFalse(result)
    
    def test_rule_group_evaluation(self):
        """Test rule group evaluation with different logic operators."""
        # Create mock rule group
        mock_rule_group = Mock()
        
        # Create two rules - one that always passes, one that always fails
        true_rule = Mock()
        true_rule.field = 'weight_lb'
        true_rule.operator = 'eq'
        true_rule.value = '10'
        true_rule.get_values_as_list = lambda: [true_rule.value]
        
        false_rule = Mock()
        false_rule.field = 'weight_lb'
        false_rule.operator = 'eq'
        false_rule.value = '20'  # Order has weight_lb=10, so this will fail
        false_rule.get_values_as_list = lambda: [false_rule.value]
        
        # Set up mock rule group
        mock_rule_group.rules.all.return_value.select_related.return_value = [true_rule, false_rule]
        order = MockOrder(weight_lb=10)
        
        # Test different logic operators
        logic_operators = {
            'AND': False,  # true AND false = false
            'OR': True,    # true OR false = true
            'NOT': False,  # NOT (true OR false) = false
            'XOR': True,   # true XOR false = true
            'NAND': True,  # NOT (true AND false) = true
            'NOR': False,  # NOT (true OR false) = false
        }
        
        for operator, expected in logic_operators.items():
            mock_rule_group.logic_operator = operator
            result = RuleEvaluator.evaluate_rule_group(mock_rule_group, order)
            self.assertEqual(result, expected, f"Failed for logic operator: {operator}")

    def test_case_based_rule_evaluation(self):
        """Test case-based rule evaluation."""
        # Create mock rule with tier configuration
        mock_rule = Mock()
        mock_rule.tier_config = {
            'excluded_skus': ['SKU-EX1', 'SKU-EX2'],
            'ranges': [
                {'min': 1, 'max': 10, 'multiplier': 1.0},
                {'min': 11, 'max': 20, 'multiplier': 1.5},
                {'min': 21, 'max': 100, 'multiplier': 2.0}
            ]
        }
        
        # Test case within first range
        order = MockOrder(total_cases=5)
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(mock_rule, order)
        self.assertTrue(applies)
        self.assertEqual(multiplier, Decimal('1.0'))
        self.assertEqual(summary['total_cases'], 5)
        
        # Test case within second range
        order = MockOrder(total_cases=15)
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(mock_rule, order)
        self.assertTrue(applies)
        self.assertEqual(multiplier, Decimal('1.5'))
        self.assertEqual(summary['total_cases'], 15)
        
        # Test case within third range
        order = MockOrder(total_cases=30)
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(mock_rule, order)
        self.assertTrue(applies)
        self.assertEqual(multiplier, Decimal('2.0'))
        self.assertEqual(summary['total_cases'], 30)
        
        # Test case below any range
        order = MockOrder(total_cases=0)
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(mock_rule, order)
        self.assertFalse(applies)
        self.assertEqual(multiplier, 0)
        self.assertEqual(summary['total_cases'], 0)
        
        # Test case above all ranges
        order = MockOrder(total_cases=101)
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(mock_rule, order)
        self.assertFalse(applies)
        self.assertEqual(multiplier, 0)
        self.assertEqual(summary['total_cases'], 101)
        
        # Test case with only excluded SKUs
        order = MockOrder(total_cases=5, only_excluded_skus=True)
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(mock_rule, order)
        self.assertFalse(applies)
        self.assertEqual(multiplier, 0)
        self.assertEqual(summary, None)  # No summary when only_excluded_skus is True


class BillingCalculatorTests(TestCase):
    """Tests for the BillingCalculator class."""
    
    @patch('billing.billing_calculator.Customer')
    @patch('billing.billing_calculator.Order')
    @patch('billing.billing_calculator.CustomerService')
    def setUp(self, mock_cs, mock_order, mock_customer):
        # Create a calculator for testing
        self.customer_id = 1
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2023, 1, 31)
        self.calculator = BillingCalculator(self.customer_id, self.start_date, self.end_date)
        
        # Mock objects for validation
        mock_customer.objects.get.return_value = Mock(id=self.customer_id)
        mock_cs.objects.filter.return_value.exists.return_value = True
    
    def test_initialization(self):
        """Test initialization of BillingCalculator."""
        self.assertEqual(self.calculator.customer_id, self.customer_id)
        self.assertEqual(self.calculator.start_date, self.start_date)
        self.assertEqual(self.calculator.end_date, self.end_date)
        self.assertIsInstance(self.calculator.report, BillingReport)
        self.assertEqual(self.calculator.report.customer_id, self.customer_id)
        self.assertEqual(self.calculator.report.start_date, self.start_date)
        self.assertEqual(self.calculator.report.end_date, self.end_date)
    
    @patch('billing.billing_calculator.Customer')
    def test_validate_input_customer_not_found(self, mock_customer):
        """Test validation fails if customer not found."""
        mock_customer.objects.get.side_effect = Mock(side_effect=Mock(DoesNotExist=Exception()))
        mock_customer.DoesNotExist = Exception
        
        with self.assertRaises(Exception):
            self.calculator.validate_input()
    
    def test_validate_input_invalid_date_range(self):
        """Test validation fails if start_date is after end_date."""
        self.calculator.start_date = datetime(2023, 2, 1)
        self.calculator.end_date = datetime(2023, 1, 31)
        
        with self.assertRaises(ValidationError):
            self.calculator.validate_input()
    
    @patch('billing.billing_calculator.CustomerService')
    def test_validate_input_no_services(self, mock_cs):
        """Test validation fails if no services for customer."""
        mock_cs.objects.filter.return_value.exists.return_value = False
        
        with self.assertRaises(ValidationError):
            self.calculator.validate_input()
    
    @patch('billing.billing_calculator.Order')
    def test_generate_report_no_orders(self, mock_order):
        """Test generating report with no orders."""
        mock_order.objects.filter.return_value.select_related.return_value = []
        
        report = self.calculator.generate_report()
        
        self.assertEqual(report.customer_id, self.customer_id)
        self.assertEqual(report.start_date, self.start_date)
        self.assertEqual(report.end_date, self.end_date)
        self.assertEqual(report.order_costs, [])
        self.assertEqual(report.service_totals, {})
        self.assertEqual(report.total_amount, Decimal('0'))
    
    @patch('billing.billing_calculator.RuleEvaluator')
    @patch('billing.billing_calculator.CustomerService')
    @patch('billing.billing_calculator.Order')
    def test_generate_report_with_orders(self, mock_order, mock_cs, mock_rule_evaluator):
        """Test generating report with orders."""
        # Mock orders
        order1 = Mock(transaction_id=1, customer_id=self.customer_id)
        order2 = Mock(transaction_id=2, customer_id=self.customer_id)
        mock_order.objects.filter.return_value.select_related.return_value = [order1, order2]
        
        # Mock customer services
        service1 = Mock(id=1, service_name='Service 1', charge_type='single')
        service2 = Mock(id=2, service_name='Service 2', charge_type='quantity')
        cs1 = Mock(id=1, service=service1, unit_price=Decimal('10.00'))
        cs2 = Mock(id=2, service=service2, unit_price=Decimal('5.00'))
        mock_cs.objects.filter.return_value.select_related.return_value.prefetch_related.return_value = [cs1, cs2]
        
        # Mock rule evaluation - both services apply to both orders
        mock_rule_evaluator.evaluate_rule_group.return_value = True
        
        # Mock cost calculation
        with patch.object(BillingCalculator, 'calculate_service_cost') as mock_calc:
            mock_calc.side_effect = [
                Decimal('10.00'),  # CS1, Order1
                Decimal('20.00'),  # CS2, Order1
                Decimal('10.00'),  # CS1, Order2
                Decimal('15.00'),  # CS2, Order2
            ]
            
            # Generate the report
            report = self.calculator.generate_report()
            
            # Verify report structure
            self.assertEqual(len(report.order_costs), 2)
            
            # Check first order
            order_cost = report.order_costs[0]
            self.assertEqual(order_cost.order_id, 1)
            self.assertEqual(len(order_cost.service_costs), 2)
            self.assertEqual(order_cost.service_costs[0].service_id, 1)
            self.assertEqual(order_cost.service_costs[0].service_name, 'Service 1')
            self.assertEqual(order_cost.service_costs[0].amount, Decimal('10.00'))
            self.assertEqual(order_cost.service_costs[1].service_id, 2)
            self.assertEqual(order_cost.service_costs[1].service_name, 'Service 2')
            self.assertEqual(order_cost.service_costs[1].amount, Decimal('20.00'))
            self.assertEqual(order_cost.total_amount, Decimal('30.00'))
            
            # Check second order
            order_cost = report.order_costs[1]
            self.assertEqual(order_cost.order_id, 2)
            self.assertEqual(len(order_cost.service_costs), 2)
            self.assertEqual(order_cost.service_costs[0].service_id, 1)
            self.assertEqual(order_cost.service_costs[0].service_name, 'Service 1')
            self.assertEqual(order_cost.service_costs[0].amount, Decimal('10.00'))
            self.assertEqual(order_cost.service_costs[1].service_id, 2)
            self.assertEqual(order_cost.service_costs[1].service_name, 'Service 2')
            self.assertEqual(order_cost.service_costs[1].amount, Decimal('15.00'))
            self.assertEqual(order_cost.total_amount, Decimal('25.00'))
            
            # Check service totals
            self.assertEqual(report.service_totals[1], Decimal('20.00'))  # Service 1: 10 + 10
            self.assertEqual(report.service_totals[2], Decimal('35.00'))  # Service 2: 20 + 15
            
            # Check total amount
            self.assertEqual(report.total_amount, Decimal('55.00'))  # 30 + 25
    
    def test_calculate_service_cost_single_charge_type(self):
        """Test calculating cost for 'single' charge type."""
        # Create mock customer service and order
        service = Mock(charge_type='single', service_name='Single Service', id=1)
        customer_service = Mock(service=service, unit_price=Decimal('10.00'))
        order = Mock()
        
        cost = self.calculator.calculate_service_cost(customer_service, order)
        self.assertEqual(cost, Decimal('10.00'))
    
    def test_calculate_service_cost_case_based_tier(self):
        """Test calculating cost for 'case_based_tier' charge type."""
        # Create mock customer service and order
        service = Mock(charge_type='case_based_tier', service_name='Case Based Service', id=1)
        customer_service = Mock(service=service, unit_price=Decimal('10.00'))
        customer_service.advanced_rules.first.return_value = Mock()
        order = Mock()
        
        # Mock the rule evaluation
        with patch.object(RuleEvaluator, 'evaluate_case_based_rule') as mock_eval:
            # Test case 1: Rule applies with multiplier 1.5
            mock_eval.return_value = (True, Decimal('1.5'), {'total_cases': 15})
            cost = self.calculator.calculate_service_cost(customer_service, order)
            self.assertEqual(cost, Decimal('15.00'))  # 10.00 * 1.5
            
            # Test case 2: Rule doesn't apply
            mock_eval.return_value = (False, Decimal('0'), None)
            cost = self.calculator.calculate_service_cost(customer_service, order)
            self.assertEqual(cost, Decimal('0'))
    
    def test_calculate_service_cost_quantity_with_skus(self):
        """Test calculating cost for 'quantity' charge type with specific SKUs."""
        # Create mock customer service and order
        service = Mock(charge_type='quantity', service_name='SKU Quantity Service', id=1)
        customer_service = Mock(service=service, unit_price=Decimal('5.00'))
        customer_service.get_sku_list.return_value = ['SKU-123', 'SKU-456']
        
        # Create mock order with SKU quantity data
        sku_quantity = [
            {"sku": "SKU-123", "quantity": 2},
            {"sku": "SKU-456", "quantity": 3},
            {"sku": "SKU-789", "quantity": 4}  # This SKU isn't assigned to the service
        ]
        order = Mock(sku_quantity=json.dumps(sku_quantity))
        
        cost = self.calculator.calculate_service_cost(customer_service, order)
        self.assertEqual(cost, Decimal('25.00'))  # 5.00 * (2 + 3)
    
    def test_to_dict(self):
        """Test the to_dict method."""
        # Create a simple report with one order and one service
        order_cost = OrderCost(order_id='ORD-001')
        service_cost = ServiceCost(
            service_id=1,
            service_name='Service 1',
            amount=Decimal('10.00')
        )
        order_cost.service_costs.append(service_cost)
        order_cost.total_amount = Decimal('10.00')
        
        self.calculator.report.order_costs.append(order_cost)
        self.calculator.report.service_totals[1] = Decimal('10.00')
        self.calculator.report.total_amount = Decimal('10.00')
        
        # Convert to dict
        result = self.calculator.to_dict()
        
        # Verify structure
        self.assertEqual(result['customer_id'], self.customer_id)
        self.assertEqual(result['start_date'], self.start_date.isoformat())
        self.assertEqual(result['end_date'], self.end_date.isoformat())
        
        # Check orders
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['order_id'], 'ORD-001')
        self.assertEqual(len(result['orders'][0]['services']), 1)
        self.assertEqual(result['orders'][0]['services'][0]['service_id'], 1)
        self.assertEqual(result['orders'][0]['services'][0]['service_name'], 'Service 1')
        self.assertEqual(result['orders'][0]['services'][0]['amount'], '10.00')
        self.assertEqual(result['orders'][0]['total_amount'], '10.00')
        
        # Check service totals
        self.assertEqual(result['service_totals']['1']['name'], 'Service 1')
        self.assertEqual(result['service_totals']['1']['amount'], '10.00')
        
        # Check total amount
        self.assertEqual(result['total_amount'], '10.00')
    
    def test_to_json(self):
        """Test the to_json method."""
        # Mock the to_dict method
        mock_dict = {
            'customer_id': self.customer_id,
            'total_amount': '10.00'
        }
        with patch.object(BillingCalculator, 'to_dict', return_value=mock_dict):
            result = self.calculator.to_json()
            
            # Verify it's a valid JSON string
            parsed = json.loads(result)
            self.assertEqual(parsed['customer_id'], self.customer_id)
            self.assertEqual(parsed['total_amount'], '10.00')
    
    def test_to_csv(self):
        """Test the to_csv method."""
        # Create a simple report with one order and one service
        order_cost = OrderCost(order_id='ORD-001')
        service_cost = ServiceCost(
            service_id=1,
            service_name='Service 1',
            amount=Decimal('10.00')
        )
        order_cost.service_costs.append(service_cost)
        
        self.calculator.report.order_costs.append(order_cost)
        
        # Convert to CSV
        result = self.calculator.to_csv()
        
        # Verify structure
        lines = result.strip().split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "Order ID,Service ID,Service Name,Amount")
        self.assertEqual(lines[1], "ORD-001,1,Service 1,10.00")


class GenerateBillingReportTests(TestCase):
    """Tests for the generate_billing_report function."""
    
    @patch('billing.billing_calculator.BillingCalculator')
    def test_generate_billing_report(self, mock_calculator_class):
        """Test the main entry point function."""
        # Setup mock calculator
        mock_calculator = Mock()
        mock_calculator_class.return_value = mock_calculator
        mock_calculator.generate_report.return_value = Mock()
        mock_calculator.to_dict.return_value = {'total_amount': '10.00'}
        
        # Call the function
        result = generate_billing_report(
            customer_id=1,
            start_date='2023-01-01',
            end_date='2023-01-31',
            output_format='json'
        )
        
        # Verify the calculator was called correctly
        mock_calculator_class.assert_called_once()
        mock_calculator.generate_report.assert_called_once()
        
        # Verify result
        self.assertEqual(result, {'total_amount': '10.00'})