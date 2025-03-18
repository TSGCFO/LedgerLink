import json
from decimal import Decimal
from unittest import mock
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.exceptions import ValidationError
from customers.models import Customer
from orders.models import Order
from products.models import Product
from services.models import Service
from customer_services.models import CustomerService
from rules.models import Rule, RuleGroup
from ..utils.sku_utils import normalize_sku, convert_sku_format, validate_sku_quantity
from ..utils.rule_evaluator import RuleEvaluator
from ..utils.calculator import BillingCalculator, generate_billing_report
from ..models import BillingReport, OrderCost, ServiceCost


class SkuUtilsTest(TestCase):
    """Tests for SKU utility functions"""
    
    def test_normalize_sku_with_valid_input(self):
        """Test normalize_sku with valid input"""
        # Test with different formats
        self.assertEqual(normalize_sku("ABC-123"), "ABC123")
        self.assertEqual(normalize_sku("abc 123"), "ABC123")
        self.assertEqual(normalize_sku("abc-1 2 3"), "ABC123")
        self.assertEqual(normalize_sku("  ABC  - 123  "), "ABC123")
        
    def test_normalize_sku_with_edge_cases(self):
        """Test normalize_sku with edge cases"""
        # Test with empty and None values
        self.assertEqual(normalize_sku(None), "")
        self.assertEqual(normalize_sku(""), "")
        
        # Test with non-string input
        self.assertEqual(normalize_sku(123), "123")
        
    def test_convert_sku_format_with_valid_input(self):
        """Test convert_sku_format with valid input"""
        # Test with list of dictionaries
        data = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "quantity": 10}
        ]
        expected = {
            "ABC123": 5,
            "DEF456": 10
        }
        self.assertEqual(convert_sku_format(data), expected)
        
        # Test with JSON string
        json_data = json.dumps(data)
        self.assertEqual(convert_sku_format(json_data), expected)
        
        # Test with duplicates (should aggregate)
        data_with_duplicates = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "ABC123", "quantity": 10}
        ]
        expected_aggregated = {
            "ABC123": 15
        }
        self.assertEqual(convert_sku_format(data_with_duplicates), expected_aggregated)
        
    def test_convert_sku_format_with_invalid_input(self):
        """Test convert_sku_format with invalid input"""
        # Test with None
        self.assertEqual(convert_sku_format(None), {})
        
        # Test with invalid JSON
        self.assertEqual(convert_sku_format("{invalid json}"), {})
        
        # Test with non-list data
        self.assertEqual(convert_sku_format({"not": "a list"}), {})
        
        # Test with invalid items
        data = [
            {"missing_sku_key": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "missing_quantity_key": 10},
            "not a dictionary",
            {"sku": "", "quantity": 5},
            {"sku": "GHI-789", "quantity": 0},
            {"sku": "JKL-012", "quantity": "not a number"}
        ]
        # Should only keep valid entries
        self.assertEqual(convert_sku_format(data), {})
        
    def test_validate_sku_quantity_with_valid_input(self):
        """Test validate_sku_quantity with valid input"""
        # Test with valid data
        data = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "quantity": 10}
        ]
        self.assertTrue(validate_sku_quantity(data))
        
        # Test with valid JSON string
        json_data = json.dumps(data)
        self.assertTrue(validate_sku_quantity(json_data))
        
    def test_validate_sku_quantity_with_invalid_input(self):
        """Test validate_sku_quantity with invalid input"""
        # Test with None
        self.assertFalse(validate_sku_quantity(None))
        
        # Test with invalid JSON
        self.assertFalse(validate_sku_quantity("{invalid json}"))
        
        # Test with non-list data
        self.assertFalse(validate_sku_quantity({"not": "a list"}))
        
        # Test with invalid items
        data = [
            {"missing_sku_key": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "missing_quantity_key": 10},
            "not a dictionary",
            {"sku": "", "quantity": 5},
            {"sku": "GHI-789", "quantity": 0},
            {"sku": "JKL-012", "quantity": "not a number"}
        ]
        self.assertFalse(validate_sku_quantity(data))


class RuleEvaluatorTest(TestCase):
    """Tests for RuleEvaluator"""
    
    def setUp(self):
        """Set up test data"""
        # Create mock rule and order for testing
        self.order = mock.MagicMock()
        self.rule = mock.MagicMock()
        self.rule_group = mock.MagicMock()
        
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
        rule1 = mock.MagicMock()
        rule2 = mock.MagicMock()
        
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
        rule = mock.MagicMock()
        order = mock.MagicMock()
        
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
        
        # Test with zero cases
        case_summary_zero = {'total_cases': 0}
        order.get_case_summary.return_value = case_summary_zero
        
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(rule, order)
        
        # Check results
        self.assertFalse(applies)
        self.assertEqual(multiplier, 0)
        
        # Test with only excluded SKUs
        order.has_only_excluded_skus.return_value = True
        
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(rule, order)
        
        # Check results
        self.assertFalse(applies)
        self.assertEqual(multiplier, 0)
        
        # Test with no tier configuration
        rule.tier_config = {}
        
        applies, multiplier, summary = RuleEvaluator.evaluate_case_based_rule(rule, order)
        
        # Check results
        self.assertFalse(applies)
        self.assertEqual(multiplier, 0)


class BillingCalculatorTest(TestCase):
    """Tests for BillingCalculator"""
    
    @patch('Billing_V2.utils.calculator.BillingCalculator.validate_input')
    @patch('Billing_V2.utils.calculator.BillingCalculator.calculate_service_cost')
    @patch('Billing_V2.utils.calculator.RuleEvaluator.evaluate_rule_group')
    def test_generate_report(self, mock_evaluate_rule_group, mock_calculate_service_cost, mock_validate_input):
        """Test generating a billing report"""
        # Create test data
        customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create test orders
        order = Order.objects.create(
            transaction_id=12345,
            customer=customer,
            reference_number="REF12345",
            status="shipped",
            priority="medium"
        )
        
        # Create test services and customer services
        service = Service.objects.create(
            name="Test Service",
            charge_type="single"
        )
        
        customer_service = CustomerService.objects.create(
            customer=customer,
            service=service,
            unit_price=Decimal('100.00')
        )
        
        # Set up mocks
        mock_validate_input.return_value = None
        mock_evaluate_rule_group.return_value = True
        mock_calculate_service_cost.return_value = Decimal('100.00')
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=customer.id,
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        
        # Mock the queryset results
        with patch('orders.models.Order.objects.filter') as mock_order_filter:
            mock_order_filter.return_value.order_by.return_value = [order]
            
            with patch('customer_services.models.CustomerService.objects.filter') as mock_cs_filter:
                mock_cs_filter.return_value.select_related.return_value.prefetch_related.return_value = [customer_service]
                
                # Generate the report
                report = calculator.generate_report()
                
                # Verify the results
                self.assertEqual(report.customer_id, customer.id)
                self.assertEqual(report.total_amount, Decimal('100.00'))
                self.assertEqual(len(report.service_totals), 1)
                
                # Verify the mocks were called
                mock_validate_input.assert_called_once()
                mock_calculate_service_cost.assert_called_once()
                
    def test_calculate_service_cost_single(self):
        """Test calculating cost for a single service"""
        # Create test data
        service = mock.MagicMock()
        service.charge_type = 'single'
        service.name = 'Test Service'
        
        customer_service = mock.MagicMock()
        customer_service.service = service
        customer_service.unit_price = Decimal('100.00')
        
        order = mock.MagicMock()
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        
        # Calculate cost
        cost = calculator.calculate_service_cost(customer_service, order)
        
        # Verify result
        self.assertEqual(cost, Decimal('100.00'))
        
    def test_calculate_service_cost_quantity(self):
        """Test calculating cost for a quantity-based service"""
        # Create test data
        service = mock.MagicMock()
        service.charge_type = 'quantity'
        service.name = 'Test Service'
        
        customer_service = mock.MagicMock()
        customer_service.service = service
        customer_service.unit_price = Decimal('10.00')
        customer_service.assigned_skus = None
        
        order = mock.MagicMock()
        order.total_item_qty = 5
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        
        # Calculate cost
        cost = calculator.calculate_service_cost(customer_service, order)
        
        # Verify result (10.00 * 5 = 50.00)
        self.assertEqual(cost, Decimal('50.00'))
        
    @patch('Billing_V2.utils.calculator.BillingCalculator')
    def test_generate_billing_report(self, mock_calculator):
        """Test the generate_billing_report function"""
        # Set up mock calculator
        mock_instance = mock.MagicMock()
        mock_calculator.return_value = mock_instance
        mock_instance.generate_report.return_value = mock.MagicMock()
        mock_instance.to_json.return_value = '{"test": "data"}'
        mock_instance.to_csv.return_value = 'test,data'
        mock_instance.to_dict.return_value = {'test': 'data'}
        
        # Test with JSON format
        result_json = generate_billing_report(1, '2023-01-01', '2023-01-31', 'json')
        self.assertEqual(result_json, '{"test": "data"}')
        
        # Test with CSV format
        result_csv = generate_billing_report(1, '2023-01-01', '2023-01-31', 'csv')
        self.assertEqual(result_csv, 'test,data')
        
        # Test with dict format
        result_dict = generate_billing_report(1, '2023-01-01', '2023-01-31', 'dict')
        self.assertEqual(result_dict, {'test': 'data'})