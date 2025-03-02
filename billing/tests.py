from django.test import TestCase

# Create your tests here.
# tests/test_billing_calculator.py

from decimal import Decimal
import json
from datetime import datetime, timezone
from django.test import TestCase
from django.core.exceptions import ValidationError

from billing.billing_calculator import (
    validate_sku_quantity,
    BillingCalculator,
    RuleEvaluator
)
from orders.models import Order
from customers.models import Customer
from services.models import Service
from rules.models import Rule, RuleGroup
from customer_services.models import CustomerService

class TestSKUQuantityValidation(TestCase):
    def test_valid_sku_quantity(self):
        """Test validation of valid SKU quantity data"""
        valid_data = [
            {"sku": "ABO-072", "quantity": 10}
        ]
        self.assertTrue(validate_sku_quantity(valid_data))

        valid_data_multiple = [
            {"sku": "ABO-012", "quantity": 12},
            {"sku": "ABO-022", "quantity": 12},
            {"sku": "ABO-032", "quantity": 12},
            {"sku": "ABO-117", "quantity": 12}
        ]
        self.assertTrue(validate_sku_quantity(valid_data_multiple))

    def test_invalid_sku_quantity(self):
        """Test validation of invalid SKU quantity data"""
        # Not a list
        invalid_data = {"sku": "ABO-072", "quantity": 10}
        self.assertFalse(validate_sku_quantity(invalid_data))

        # Missing required keys
        invalid_data = [{"sku": "ABO-072"}]
        self.assertFalse(validate_sku_quantity(invalid_data))

        # Invalid quantity
        invalid_data = [{"sku": "ABO-072", "quantity": -1}]
        self.assertFalse(validate_sku_quantity(invalid_data))

        # Empty SKU
        invalid_data = [{"sku": "", "quantity": 10}]
        self.assertFalse(validate_sku_quantity(invalid_data))

class TestBillingCalculator(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test customer
        cls.customer = Customer.objects.create(
            company_name="Test Company",
            email="test@example.com"
        )

        # Create services
        cls.sku_cost_service = Service.objects.create(
            service_name="SKU Cost",
            charge_type="quantity"
        )
        cls.single_service = Service.objects.create(
            service_name="Single Service",
            charge_type="single"
        )
        cls.quantity_service = Service.objects.create(
            service_name="Quantity Service",
            charge_type="quantity"
        )

        # Create customer services
        cls.sku_cost_cs = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.sku_cost_service,
            unit_price=Decimal("1.00")
        )
        cls.single_cs = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.single_service,
            unit_price=Decimal("10.00")
        )
        cls.quantity_cs = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.quantity_service,
            unit_price=Decimal("2.00")
        )

        # Create rule groups and rules
        cls.sku_cost_rule_group = RuleGroup.objects.create(
            customer_service=cls.sku_cost_cs,
            logic_operator='AND'
        )
        cls.single_rule_group = RuleGroup.objects.create(
            customer_service=cls.single_cs,
            logic_operator='AND'
        )
        cls.quantity_rule_group = RuleGroup.objects.create(
            customer_service=cls.quantity_cs,
            logic_operator='AND'
        )

        # Create rules
        Rule.objects.create(
            rule_group=cls.sku_cost_rule_group,
            field='total_item_qty',
            operator='gt',
            value='0'
        )
        Rule.objects.create(
            rule_group=cls.single_rule_group,
            field='total_item_qty',
            operator='gt',
            value='0'
        )
        Rule.objects.create(
            rule_group=cls.quantity_rule_group,
            field='total_item_qty',
            operator='gt',
            value='0'
        )

    def create_test_order(self, sku_quantity, total_item_qty):
        """Helper method to create test orders"""
        return Order.objects.create(
            customer=self.customer,
            transaction_id=f"TEST-{datetime.now().timestamp()}",
            close_date=datetime.now(timezone.utc),
            sku_quantity=json.dumps(sku_quantity) if isinstance(sku_quantity, list) else sku_quantity,
            total_item_qty=total_item_qty
        )

    def test_sku_cost_calculation(self):
        """Test SKU Cost service calculation"""
        # Test single SKU
        order1 = self.create_test_order(
            sku_quantity=[{"sku": "ABO-072", "quantity": 10}],
            total_item_qty=10
        )
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        cost = calculator.calculate_service_cost(self.sku_cost_cs, order1)
        self.assertEqual(cost, Decimal("1.00"))  # One unique SKU

        # Test multiple SKUs
        order2 = self.create_test_order(
            sku_quantity=[
                {"sku": "ABO-012", "quantity": 12},
                {"sku": "ABO-022", "quantity": 12},
                {"sku": "ABO-032", "quantity": 12},
                {"sku": "ABO-117", "quantity": 12}
            ],
            total_item_qty=48
        )
        cost = calculator.calculate_service_cost(self.sku_cost_cs, order2)
        self.assertEqual(cost, Decimal("4.00"))  # Four unique SKUs

    def test_single_service_calculation(self):
        """Test single charge service calculation"""
        order = self.create_test_order(
            sku_quantity=[{"sku": "ABO-072", "quantity": 10}],
            total_item_qty=10
        )
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        cost = calculator.calculate_service_cost(self.single_cs, order)
        self.assertEqual(cost, Decimal("10.00"))

    def test_quantity_service_calculation(self):
        """Test quantity-based service calculation"""
        order = self.create_test_order(
            sku_quantity=[{"sku": "ABO-072", "quantity": 10}],
            total_item_qty=10
        )
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        cost = calculator.calculate_service_cost(self.quantity_cs, order)
        self.assertEqual(cost, Decimal("20.00"))  # $2.00 × 10 items

    def test_generate_report(self):
        """Test report generation with multiple orders and services"""
        # Create test orders
        order1 = self.create_test_order(
            sku_quantity=[{"sku": "ABO-072", "quantity": 10}],
            total_item_qty=10
        )
        order2 = self.create_test_order(
            sku_quantity=[
                {"sku": "ABO-012", "quantity": 12},
                {"sku": "ABO-022", "quantity": 12}
            ],
            total_item_qty=24
        )

        # Generate report
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()

        # Verify report totals
        expected_total = Decimal("0")

        # Order 1: 1 SKU ($1) + Single charge ($10) + Quantity charge ($20)
        expected_total += Decimal("31.00")

        # Order 2: 2 SKUs ($2) + Single charge ($10) + Quantity charge ($48)
        expected_total += Decimal("60.00")

        self.assertEqual(report.total_amount, expected_total)

    def test_single_service_applied_once(self):
        """Test that single charge services are only applied once per order"""
        order = self.create_test_order(
            sku_quantity=[{"sku": "ABO-072", "quantity": 10}],
            total_item_qty=10
        )

        # Create multiple matching rule groups for the single service
        RuleGroup.objects.create(
            customer_service=self.single_cs,
            logic_operator='AND'
        )

        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()

        # Count how many times the single service appears in the order
        single_service_count = sum(
            1 for oc in report.order_costs
            for sc in oc.service_costs
            if sc.service_id == self.single_service.id
        )

        self.assertEqual(single_service_count, 1)

    def test_input_validation(self):
        """Test input validation"""
        # Test invalid customer
        with self.assertRaises(ValidationError):
            calculator = BillingCalculator(
                customer_id=99999,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc)
            )
            calculator.validate_input()

        # Test invalid date range
        with self.assertRaises(ValidationError):
            calculator = BillingCalculator(
                customer_id=self.customer.id,
                start_date=datetime.now(timezone.utc),
                end_date=datetime(2000, 1, 1, tzinfo=timezone.utc)
            )
            calculator.validate_input()

class TestRuleEvaluation(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup test data for rule evaluation
        cls.customer = Customer.objects.create(
            company_name="Test Company",
            email="test@example.com"
        )

    def test_numeric_rule_evaluation(self):
        """Test evaluation of numeric rules"""
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="TEST-123",
            total_item_qty=10
        )

        rule = Rule(
            field='total_item_qty',
            operator='gt',
            value='5'
        )
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))

        rule.operator = 'lt'
        rule.value = '20'
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))

    def test_string_rule_evaluation(self):
        """Test evaluation of string rules"""
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="TEST-123",
            carrier="UPS"
        )

        rule = Rule(
            field='carrier',
            operator='eq',
            value='UPS'
        )
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))

        rule.operator = 'contains'
        rule.value = 'UP'
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))

    def test_sku_quantity_rule_evaluation(self):
        """Test evaluation of SKU quantity rules"""
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="TEST-123",
            sku_quantity=json.dumps([
                {"sku": "ABO-012", "quantity": 12},
                {"sku": "ABO-022", "quantity": 12}
            ])
        )

        rule = Rule(
            field='sku_quantity',
            operator='contains',
            value='ABO-012'
        )
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))

        rule.operator = 'ncontains'
        rule.value = 'ABO-999'
        self.assertTrue(RuleEvaluator.evaluate_rule(rule, order))

class CaseBasedTierCalculationTest(TestCase):
    """Test case-based tier calculations in the billing calculator."""
    
    def setUp(self):
        """Set up test data for the billing calculator tests."""
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create test service with case-based tier pricing
        self.service = Service.objects.create(
            service_name="Case-Based Tier Service",
            description="Service with case-based tier pricing",
            charge_type="case_based_tier"
        )
        
        # Create customer service linking customer and service
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('100.00')
        )
        
        # Create rule group for the customer service
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator="AND"
        )
        
        # Create an advanced rule with case-based tier configuration
        from rules.models import AdvancedRule
        self.rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
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
        
        # Create a test order with SKUs and case quantities
        self.order = Order.objects.create(
            transaction_id="TEST001",
            customer=self.customer,
            reference_number="REF001",
            ship_to_name="Test Ship",
            ship_to_address1="123 Shipping St",
            ship_to_city="Ship City",
            ship_to_state="SS",
            ship_to_zip="12345",
            close_date=datetime.now(timezone.utc),
            sku_quantity=json.dumps({
                "SKU1": {"quantity": 20, "cases": 4},
                "EXCLUDE-SKU": {"quantity": 10, "cases": 2}
            })
        )
        
        # Add a method to Order that matches the evaluate_case_based_rule's expectations
        def get_case_summary(order, exclude_skus=None):
            skus = json.loads(order.sku_quantity)
            excluded = set(exclude_skus or [])
            
            # Calculate total cases, excluding any SKUs in the excluded list
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
            
        def has_only_excluded_skus(order, exclude_skus):
            if not exclude_skus:
                return False
                
            skus = json.loads(order.sku_quantity)
            for sku in skus.keys():
                if sku not in exclude_skus:
                    return False
            return True
        
        # Add these methods to the Order class
        Order.get_case_summary = get_case_summary
        Order.has_only_excluded_skus = has_only_excluded_skus
    
    def test_case_based_tier_evaluation(self):
        """Test evaluation of case-based tier rules."""
        from rules.models import RuleEvaluator
        
        # Verify the case-based tier evaluation
        applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(self.rule, self.order)
        
        # Should match tier 2 (4-6 cases) with multiplier 2.0
        self.assertTrue(applies, "Rule should apply to the order")
        self.assertEqual(Decimal('2.0'), multiplier, "Multiplier should be 2.0 for 4 cases")
        self.assertEqual(4, case_summary['total_cases'], "Should count 4 cases (excluding 2)")
    
    def test_case_based_service_cost_calculation(self):
        """Test the calculation of case-based tier service cost."""
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        
        # Calculate service cost
        cost = calculator.calculate_service_cost(self.customer_service, self.order)
        
        # Expected cost: base price ($100) * multiplier (2.0) = $200
        expected_cost = Decimal('200.00')
        self.assertEqual(expected_cost, cost, f"Expected cost ${expected_cost}, got ${cost}")
    
    def test_billing_report_with_case_based_tier(self):
        """Test the full billing report generation with case-based tier pricing."""
        # Create multiple orders with different case counts to test different tiers
        
        # Order in tier 3 (7-10 cases)
        Order.objects.create(
            transaction_id="TEST002",
            customer=self.customer,
            reference_number="REF002",
            ship_to_name="Test Ship 2",
            ship_to_address1="456 Shipping Ave",
            ship_to_city="Ship City",
            ship_to_state="SS",
            ship_to_zip="54321",
            close_date=datetime.now(timezone.utc),
            sku_quantity=json.dumps({
                "SKU1": {"quantity": 30, "cases": 3},
                "SKU2": {"quantity": 40, "cases": 4},
                "SKU3": {"quantity": 10, "cases": 1}
                # Total: 8 cases (tier 3)
            })
        )
        
        # Generate billing report
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Verify report contains both orders
        self.assertEqual(2, len(report.order_costs), "Should contain 2 orders")
        
        # Find order costs
        order1_cost = next((oc for oc in report.order_costs if oc.order_id == "TEST001"), None)
        order2_cost = next((oc for oc in report.order_costs if oc.order_id == "TEST002"), None)
        
        self.assertIsNotNone(order1_cost, "Should find order TEST001 in the report")
        self.assertIsNotNone(order2_cost, "Should find order TEST002 in the report")
        
        # Check service costs
        self.assertEqual(1, len(order1_cost.service_costs), "Should have 1 service cost")
        self.assertEqual(1, len(order2_cost.service_costs), "Should have 1 service cost")
        
        # Check tier multiplier application
        self.assertEqual(Decimal('200.00'), order1_cost.service_costs[0].amount, 
                         "Order 1 should use tier 2 multiplier (2.0)")
        self.assertEqual(Decimal('300.00'), order2_cost.service_costs[0].amount, 
                         "Order 2 should use tier 3 multiplier (3.0)")
        
        # Check total amounts
        self.assertEqual(Decimal('200.00'), order1_cost.total_amount)
        self.assertEqual(Decimal('300.00'), order2_cost.total_amount)
        self.assertEqual(Decimal('500.00'), report.total_amount, 
                        "Total should be $500 ($200 from first order + $300 from second)")