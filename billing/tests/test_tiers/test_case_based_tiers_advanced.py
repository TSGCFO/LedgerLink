import pytest
import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone

from billing.billing_calculator import BillingCalculator, RuleEvaluator
from customers.models import Customer
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from rules.models import RuleGroup, AdvancedRule


class CaseBasedTierTests(TestCase):
    """Advanced tests for case-based tier calculations."""
    
    def setUp(self):
        """Set up test data for case-based tier tests."""
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Tier Test Company",
            contact_email="tier@test.com",
            phone_number="555-789-1234"
        )
        
        # Create a case-based tier service
        self.service = Service.objects.create(
            service_name="Case-Based Shipping",
            description="Shipping charged based on case tiers",
            charge_type="case_based_tier"
        )
        
        # Create a customer service with base price
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal("100.00")
        )
        
        # Create a rule group
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            name="Case Tier Rules",
            logic_operator="AND"
        )
        
        # Create an advanced rule with tier configuration
        self.rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            field="sku_quantity",
            operator="contains",
            value="TEST-CASE",
            calculations=[
                {"type": "case_based_tier", "value": 1.0}
            ],
            # 3 tiers: 1-3 cases, 4-10 cases, 11+ cases with different multipliers
            tier_config={
                "ranges": [
                    {"min": 1, "max": 3, "multiplier": 1.0},   # Base price
                    {"min": 4, "max": 10, "multiplier": 0.9},  # 10% discount
                    {"min": 11, "max": 999999, "multiplier": 0.75}  # 25% discount
                ],
                "excluded_skus": ["EXCLUDE-SKU"]
            }
        )
        
        # Create dates for the billing period
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
    
    def create_order_with_cases(self, order_id, case_quantities, close_date=None):
        """Helper to create an order with specified case quantities."""
        skus = []
        for sku_index, quantity in enumerate(case_quantities):
            skus.append({
                "sku": f"TEST-CASE-{sku_index+1}",
                "quantity": quantity * 10  # 10 items per case for test
            })
        
        if not close_date:
            close_date = timezone.now()
        
        return Order.objects.create(
            customer=self.customer,
            transaction_id=order_id,
            reference_number=f"REF-{order_id}",
            close_date=close_date,
            sku_quantity=json.dumps(skus)
        )
    
    def calculate_report(self, orders):
        """Calculate billing report for the given orders."""
        # Patch the Order.objects.filter method to return our orders
        with patch('billing.billing_calculator.Order.objects.filter') as mock_order_filter:
            mock_order_filter.return_value = orders
            
            # Create calculator
            calculator = BillingCalculator(
                customer_id=self.customer.id,
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Generate report
            report = calculator.generate_report()
            return report
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_tier_1_calculation(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation for the first tier (1-3 cases)."""
        # Create order with 2 cases
        order = self.create_order_with_cases("TIER-001", [2])
        
        # Mock the case summary methods
        mock_get_case_summary.return_value = {
            "total_cases": 2,
            "skus": {"TEST-CASE-1": 2}
        }
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Expected calculation: 2 cases x $100 base price x 1.0 multiplier = $200
        self.assertEqual(report.total_amount, Decimal('200.00'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_tier_2_calculation(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation for the second tier (4-10 cases)."""
        # Create order with 8 cases
        order = self.create_order_with_cases("TIER-002", [8])
        
        # Mock the case summary methods
        mock_get_case_summary.return_value = {
            "total_cases": 8,
            "skus": {"TEST-CASE-1": 8}
        }
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Expected calculation: 8 cases x $100 base price x 0.9 multiplier = $720
        self.assertEqual(report.total_amount, Decimal('720.00'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_tier_3_calculation(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation for the third tier (11+ cases)."""
        # Create order with 15 cases
        order = self.create_order_with_cases("TIER-003", [15])
        
        # Mock the case summary methods
        mock_get_case_summary.return_value = {
            "total_cases": 15,
            "skus": {"TEST-CASE-1": 15}
        }
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Expected calculation: 15 cases x $100 base price x 0.75 multiplier = $1125
        self.assertEqual(report.total_amount, Decimal('1125.00'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_excluded_skus(self, mock_has_only_excluded, mock_get_case_summary):
        """Test that excluded SKUs are not counted in the tier calculation."""
        # Create order with 5 cases
        order = self.create_order_with_cases("TIER-004", [5])
        
        # Mock the case summary to show excluded SKUs were skipped
        mock_get_case_summary.return_value = {
            "total_cases": 3,  # Should match tier 1, not tier 2
            "skus": {"TEST-CASE-1": 3}
        }
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Expected calculation: 3 cases x $100 base price x 1.0 multiplier = $300
        self.assertEqual(report.total_amount, Decimal('300.00'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_only_excluded_skus(self, mock_has_only_excluded, mock_get_case_summary):
        """Test that order with only excluded SKUs has zero cost."""
        # Create order
        order = self.create_order_with_cases("TIER-005", [5])
        
        # Mock that order has only excluded SKUs
        mock_has_only_excluded.return_value = True
        mock_get_case_summary.return_value = {
            "total_cases": 0,
            "skus": {}
        }
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Expected calculation: should be 0 as all SKUs are excluded
        self.assertEqual(report.total_amount, Decimal('0'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_multiple_orders_different_tiers(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation for multiple orders in different tiers."""
        # Create orders in different tiers
        order1 = self.create_order_with_cases("TIER-006", [2])  # Tier 1
        order2 = self.create_order_with_cases("TIER-007", [7])  # Tier 2
        order3 = self.create_order_with_cases("TIER-008", [12]) # Tier 3
        
        # Setup mocks to return different values for different orders
        def get_case_summary_side_effect(exclude_skus=None):
            if mock_get_case_summary.call_count == 1:
                return {"total_cases": 2, "skus": {"TEST-CASE-1": 2}}
            elif mock_get_case_summary.call_count == 2:
                return {"total_cases": 7, "skus": {"TEST-CASE-1": 7}}
            else:
                return {"total_cases": 12, "skus": {"TEST-CASE-1": 12}}
        
        mock_get_case_summary.side_effect = get_case_summary_side_effect
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order1, order2, order3])
        
        # Expected calculations:
        # Order 1: 2 cases x $100 x 1.0 = $200
        # Order 2: 7 cases x $100 x 0.9 = $630
        # Order 3: 12 cases x $100 x 0.75 = $900
        # Total: $1730
        self.assertEqual(report.total_amount, Decimal('1730.00'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_edge_case_tier_boundaries(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation at the boundary of tiers."""
        # Create orders at tier boundaries
        order1 = self.create_order_with_cases("TIER-009", [3])  # Upper boundary of tier 1
        order2 = self.create_order_with_cases("TIER-010", [4])  # Lower boundary of tier 2
        order3 = self.create_order_with_cases("TIER-011", [10]) # Upper boundary of tier 2
        order4 = self.create_order_with_cases("TIER-012", [11]) # Lower boundary of tier 3
        
        test_cases = [
            # order, total_cases, expected_amount
            (order1, 3, Decimal('300.00')),   # 3 cases * $100 * 1.0
            (order2, 4, Decimal('360.00')),   # 4 cases * $100 * 0.9
            (order3, 10, Decimal('900.00')),  # 10 cases * $100 * 0.9
            (order4, 11, Decimal('825.00')),  # 11 cases * $100 * 0.75
        ]
        
        for test_order, case_count, expected_amount in test_cases:
            # Reset the mocks
            mock_get_case_summary.reset_mock()
            mock_has_only_excluded.reset_mock()
            
            # Setup mocks for this test case
            mock_get_case_summary.return_value = {
                "total_cases": case_count,
                "skus": {"TEST-CASE-1": case_count}
            }
            mock_has_only_excluded.return_value = False
            
            # Calculate report for this order
            report = self.calculate_report([test_order])
            
            # Check amount matches expected
            self.assertEqual(report.total_amount, expected_amount)
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_zero_cases(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation with zero cases."""
        # Create order but mock it to have 0 cases
        order = self.create_order_with_cases("TIER-013", [0])
        
        # Mock the case summary methods
        mock_get_case_summary.return_value = {
            "total_cases": 0,
            "skus": {}
        }
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Should be 0 cost since no cases
        self.assertEqual(report.total_amount, Decimal('0'))
    
    @patch('orders.models.Order.get_case_summary')
    @patch('orders.models.Order.has_only_excluded_skus')
    def test_cases_above_tier_maximum(self, mock_has_only_excluded, mock_get_case_summary):
        """Test calculation with case count above the maximum defined in tiers."""
        # Create order with extremely high case count
        order = self.create_order_with_cases("TIER-014", [10000])
        
        # Mock the case summary methods
        mock_get_case_summary.return_value = {
            "total_cases": 10000,
            "skus": {"TEST-CASE-1": 10000}
        }
        mock_has_only_excluded.return_value = False
        
        # Calculate report
        report = self.calculate_report([order])
        
        # Expected calculation: 10000 cases x $100 base price x 0.75 multiplier = $750000
        self.assertEqual(report.total_amount, Decimal('750000.00'))