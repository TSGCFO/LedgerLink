"""
Comprehensive tests for case-based tier calculations in the billing system.
These tests focus on the billing calculator's ability to handle case-based tier pricing
with various configurations and edge cases.
"""

import unittest
from decimal import Decimal
import json
from datetime import datetime, timezone
from django.test import TestCase
from unittest.mock import Mock, patch

from billing.billing_calculator import RuleEvaluator, BillingCalculator
from customers.models import Customer
from services.models import Service
from customer_services.models import CustomerService
from rules.models import RuleGroup, AdvancedRule
from orders.models import Order


class MockOrder:
    """Mock order for testing rule evaluation without database."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def get_case_summary(self, exclude_skus=None):
        """Return a mocked case summary."""
        if hasattr(self, 'case_summary'):
            return self.case_summary
        
        # Default implementation if not explicitly set
        skus = json.loads(self.sku_quantity) if isinstance(self.sku_quantity, str) else self.sku_quantity
        excluded = set(exclude_skus or [])
        
        total_cases = 0
        sku_cases = {}
        
        for sku, data in skus.items():
            if sku not in excluded:
                cases = data.get('cases', 0)
                total_cases += cases
                sku_cases[sku] = cases
        
        return {
            'total_cases': total_cases,
            'skus': sku_cases
        }
    
    def has_only_excluded_skus(self, exclude_skus):
        """Check if the order has only excluded SKUs."""
        if not exclude_skus:
            return False
            
        skus = json.loads(self.sku_quantity) if isinstance(self.sku_quantity, str) else self.sku_quantity
        for sku in skus.keys():
            if sku not in exclude_skus:
                return False
        return True


class CaseBasedTierEvaluationTests(unittest.TestCase):
    """Test the case-based tier evaluation logic in isolation."""
    
    def setUp(self):
        """Set up test data for rule evaluation tests."""
        # Create a mock rule with case-based tier configuration
        self.mock_rule = Mock()
        self.mock_rule.tier_config = {
            "ranges": [
                {"min": 1, "max": 3, "multiplier": 1.0},
                {"min": 4, "max": 6, "multiplier": 2.0},
                {"min": 7, "max": 10, "multiplier": 3.0},
                {"min": 11, "max": 15, "multiplier": 4.0},
                {"min": 16, "max": 999999, "multiplier": 5.0}
            ],
            "excluded_skus": ["EXCLUDE-SKU-1", "EXCLUDE-SKU-2"]
        }
    
    def test_basic_tier_evaluation(self):
        """Test basic tier evaluation with different case quantities."""
        # Test tier 1: 1-3 cases
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 10, "cases": 2}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('1.0'), multiplier)
        self.assertEqual(2, case_summary['total_cases'])
        
        # Test tier 2: 4-6 cases
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 20, "cases": 5}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('2.0'), multiplier)
        self.assertEqual(5, case_summary['total_cases'])
        
        # Test tier 3: 7-10 cases
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 30, "cases": 8}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('3.0'), multiplier)
        self.assertEqual(8, case_summary['total_cases'])
    
    def test_multiple_skus(self):
        """Test tier evaluation with multiple SKUs."""
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 10, "cases": 2},
                "SKU2": {"quantity": 15, "cases": 3},
                "SKU3": {"quantity": 20, "cases": 4}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('3.0'), multiplier)  # 9 cases total = tier 3
        self.assertEqual(9, case_summary['total_cases'])
    
    def test_excluded_skus(self):
        """Test tier evaluation with excluded SKUs."""
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 10, "cases": 2},
                "EXCLUDE-SKU-1": {"quantity": 15, "cases": 3},
                "SKU3": {"quantity": 20, "cases": 4}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('2.0'), multiplier)  # 6 cases (excluding 3) = tier 2
        self.assertEqual(6, case_summary['total_cases'])
        
        # Test with only excluded SKUs
        order = MockOrder(
            sku_quantity={
                "EXCLUDE-SKU-1": {"quantity": 15, "cases": 3},
                "EXCLUDE-SKU-2": {"quantity": 20, "cases": 4}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertFalse(applies)  # Should not apply if only excluded SKUs
        self.assertEqual(0, multiplier)
        self.assertEqual(0, case_summary['total_cases'])
    
    def test_zero_cases(self):
        """Test tier evaluation with zero cases."""
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 10, "cases": 0}
            }
        )
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertFalse(applies)  # Should not apply if zero cases
        self.assertEqual(0, multiplier)
        self.assertEqual(0, case_summary['total_cases'])
    
    def test_tier_boundary_values(self):
        """Test tier evaluation at boundary values."""
        # Lowest boundary - 1 case
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 5, "cases": 1}
            }
        )
        applies, multiplier, _ = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('1.0'), multiplier)
        
        # Tier boundary - 3/4 cases
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 15, "cases": 3}
            }
        )
        applies, multiplier, _ = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('1.0'), multiplier)
        
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 20, "cases": 4}
            }
        )
        applies, multiplier, _ = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('2.0'), multiplier)
        
        # Upper boundary - large number of cases
        order = MockOrder(
            sku_quantity={
                "SKU1": {"quantity": 1000, "cases": 100}
            }
        )
        applies, multiplier, _ = RuleEvaluator.evaluate_case_based_rule(
            self.mock_rule, order
        )
        self.assertTrue(applies)
        self.assertEqual(Decimal('5.0'), multiplier)  # Max tier


class CaseBasedTierIntegrationTest(TestCase):
    """Integration tests for case-based tier calculations with the database."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for database integration tests."""
        # Create test customer
        cls.customer = Customer.objects.create(
            company_name="Test Tier Company",
            contact_name="Test Contact",
            email="test@tier.example.com"
        )
        
        # Create test services with different configurations
        cls.service = Service.objects.create(
            service_name="Standard Case-Based Tier",
            description="Standard tier configuration",
            charge_type="case_based_tier"
        )
        
        cls.service_extended = Service.objects.create(
            service_name="Extended Case-Based Tier",
            description="Extended tier configuration with more tiers",
            charge_type="case_based_tier"
        )
        
        # Create customer services
        cls.customer_service = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('100.00')
        )
        
        cls.customer_service_extended = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service_extended,
            unit_price=Decimal('150.00')
        )
        
        # Create rule groups
        cls.rule_group = RuleGroup.objects.create(
            customer_service=cls.customer_service,
            logic_operator="AND"
        )
        
        cls.rule_group_extended = RuleGroup.objects.create(
            customer_service=cls.customer_service_extended,
            logic_operator="AND"
        )
        
        # Create advanced rules
        cls.rule = AdvancedRule.objects.create(
            rule_group=cls.rule_group,
            field="sku_quantity",
            operator="contains",
            value="SKU",
            calculations=[
                {"type": "case_based_tier", "value": 1.0}
            ],
            tier_config={
                "ranges": [
                    {"min": 1, "max": 3, "multiplier": 1.0},
                    {"min": 4, "max": 6, "multiplier": 2.0},
                    {"min": 7, "max": 10, "multiplier": 3.0}
                ],
                "excluded_skus": ["EXCLUDE-SKU"]
            }
        )
        
        cls.rule_extended = AdvancedRule.objects.create(
            rule_group=cls.rule_group_extended,
            field="sku_quantity",
            operator="contains",
            value="SKU",
            calculations=[
                {"type": "case_based_tier", "value": 1.0}
            ],
            tier_config={
                "ranges": [
                    {"min": 1, "max": 5, "multiplier": 1.5},
                    {"min": 6, "max": 10, "multiplier": 2.5},
                    {"min": 11, "max": 20, "multiplier": 3.5},
                    {"min": 21, "max": 999999, "multiplier": 5.0}
                ],
                "excluded_skus": ["EXCLUDE-SKU-1", "EXCLUDE-SKU-2"]
            }
        )
        
        # Add methods to Order for case-based calculations
        def get_case_summary(order, exclude_skus=None):
            skus = json.loads(order.sku_quantity)
            excluded = set(exclude_skus or [])
            
            total_cases = 0
            sku_cases = {}
            
            for sku, data in skus.items():
                if sku not in excluded:
                    cases = data.get("cases", 0)
                    total_cases += cases
                    sku_cases[sku] = cases
            
            return {
                'total_cases': total_cases,
                'skus': sku_cases
            }
            
        def has_only_excluded_skus(order, exclude_skus):
            if not exclude_skus:
                return False
                
            skus = json.loads(order.sku_quantity)
            for sku in skus.keys():
                if sku not in exclude_skus:
                    return False
            return True
        
        # Add methods to Order model
        Order.get_case_summary = get_case_summary
        Order.has_only_excluded_skus = has_only_excluded_skus
    
    def create_test_order(self, transaction_id, sku_quantity):
        """Helper method to create test orders."""
        return Order.objects.create(
            transaction_id=transaction_id,
            customer=self.customer,
            reference_number=f"REF-{transaction_id}",
            ship_to_name="Test Ship",
            ship_to_address1="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            close_date=datetime.now(timezone.utc),
            sku_quantity=json.dumps(sku_quantity)
        )
    
    def test_case_based_price_calculation(self):
        """Test price calculation for different tier levels."""
        # Create orders in different tiers
        order1 = self.create_test_order(
            "TEST101",
            {
                "SKU1": {"quantity": 10, "cases": 2}
            }
        )
        
        order2 = self.create_test_order(
            "TEST102",
            {
                "SKU1": {"quantity": 10, "cases": 2},
                "SKU2": {"quantity": 15, "cases": 3}
            }
        )
        
        order3 = self.create_test_order(
            "TEST103",
            {
                "SKU1": {"quantity": 10, "cases": 2},
                "SKU2": {"quantity": 15, "cases": 3},
                "SKU3": {"quantity": 20, "cases": 4}
            }
        )
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        
        # Test standard service tiers
        cost1 = calculator.calculate_service_cost(self.customer_service, order1)
        self.assertEqual(Decimal('100.00'), cost1)  # Tier 1 (2 cases * $100 * 1.0)
        
        cost2 = calculator.calculate_service_cost(self.customer_service, order2)
        self.assertEqual(Decimal('200.00'), cost2)  # Tier 2 (5 cases * $100 * 2.0)
        
        cost3 = calculator.calculate_service_cost(self.customer_service, order3)
        self.assertEqual(Decimal('300.00'), cost3)  # Tier 3 (9 cases * $100 * 3.0)
        
        # Test extended service with different tiers
        cost1_ext = calculator.calculate_service_cost(self.customer_service_extended, order1)
        self.assertEqual(Decimal('225.00'), cost1_ext)  # Tier 1 (2 cases * $150 * 1.5)
        
        cost2_ext = calculator.calculate_service_cost(self.customer_service_extended, order2)
        self.assertEqual(Decimal('225.00'), cost2_ext)  # Tier 1 (5 cases * $150 * 1.5)
        
        cost3_ext = calculator.calculate_service_cost(self.customer_service_extended, order3)
        self.assertEqual(Decimal('375.00'), cost3_ext)  # Tier 2 (9 cases * $150 * 2.5)
    
    def test_excluded_skus_in_calculation(self):
        """Test price calculation with excluded SKUs."""
        # Create order with excluded SKUs
        order = self.create_test_order(
            "TEST201",
            {
                "SKU1": {"quantity": 10, "cases": 2},
                "SKU2": {"quantity": 15, "cases": 3},
                "EXCLUDE-SKU": {"quantity": 20, "cases": 4}
            }
        )
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        
        # Test standard service
        cost = calculator.calculate_service_cost(self.customer_service, order)
        self.assertEqual(Decimal('200.00'), cost)  # Tier 2 (5 cases * $100 * 2.0, excluding 4 cases)
        
        # Create order with only excluded SKUs
        excluded_order = self.create_test_order(
            "TEST202",
            {
                "EXCLUDE-SKU": {"quantity": 20, "cases": 4}
            }
        )
        
        cost_excluded = calculator.calculate_service_cost(self.customer_service, excluded_order)
        self.assertEqual(Decimal('0'), cost_excluded)  # No charge for excluded SKUs only
    
    def test_full_report_generation(self):
        """Test full report generation with multiple orders and services."""
        # Create orders in different tiers
        self.create_test_order(
            "TEST301",
            {
                "SKU1": {"quantity": 10, "cases": 2}
            }
        )
        
        self.create_test_order(
            "TEST302",
            {
                "SKU1": {"quantity": 10, "cases": 2},
                "SKU2": {"quantity": 15, "cases": 3}
            }
        )
        
        self.create_test_order(
            "TEST303",
            {
                "SKU1": {"quantity": 10, "cases": 2},
                "SKU2": {"quantity": 15, "cases": 3},
                "SKU3": {"quantity": 25, "cases": 5}
            }
        )
        
        # Create calculator and generate report
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Verify report contains all orders
        self.assertEqual(3, len(report.order_costs))
        
        # Calculate expected total
        # Order 1: $100 (standard) + $225 (extended) = $325
        # Order 2: $200 (standard) + $225 (extended) = $425
        # Order 3: $300 (standard) + $375 (extended) = $675
        expected_total = Decimal('325') + Decimal('425') + Decimal('675')
        
        # Check total amount
        self.assertEqual(expected_total, report.total_amount)
        
        # Check service totals
        self.assertEqual(Decimal('600'), report.service_totals[self.service.id])
        self.assertEqual(Decimal('825'), report.service_totals[self.service_extended.id])


if __name__ == '__main__':
    unittest.main()