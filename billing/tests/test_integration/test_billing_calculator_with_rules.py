"""
Integration tests for the BillingCalculator with rules.
"""

import pytest
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

from billing.billing_calculator import BillingCalculator, RuleEvaluator
from customers.models import Customer
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from rules.models import RuleGroup, Rule

pytestmark = pytest.mark.django_db

class TestBillingCalculatorWithRules:
    """Integration tests for the BillingCalculator with rules."""
    
    @pytest.fixture
    def setup_test_data(self):
        """Set up test data for billing calculation with rules."""
        # Create customer
        customer = Customer.objects.create(
            company_name="Test Calculator Company",
            contact_email="calculator@test.com",
            phone_number="555-123-4567"
        )
        
        # Create services
        shipping_service = Service.objects.create(
            service_name="Shipping",
            description="Standard shipping service",
            charge_type="single"
        )
        
        handling_service = Service.objects.create(
            service_name="Handling",
            description="Package handling service",
            charge_type="quantity"
        )
        
        # Create customer services
        cs_shipping = CustomerService.objects.create(
            customer=customer,
            service=shipping_service,
            unit_price=Decimal("15.00")  # Flat $15 per order
        )
        
        cs_handling = CustomerService.objects.create(
            customer=customer,
            service=handling_service,
            unit_price=Decimal("2.50")  # $2.50 per item
        )
        
        # Create rule groups
        weight_rule_group = RuleGroup.objects.create(
            customer_service=cs_shipping,
            name="Weight Rules",
            logic_operator="AND"
        )
        
        # Create rule for weight
        weight_rule = Rule.objects.create(
            rule_group=weight_rule_group,
            field="weight_lb",
            operator="gt",
            value="10.0"  # Only apply shipping fee for orders over 10 lbs
        )
        
        # Create orders
        order1 = Order.objects.create(
            customer=customer,
            transaction_id="CALC-001",
            reference_number="REF-001",
            weight_lb=5.0,  # Below weight threshold
            total_item_qty=3,
            close_date=timezone.now() - timedelta(days=5),
            sku_quantity=json.dumps([
                {"sku": "CALC-SKU-1", "quantity": 1},
                {"sku": "CALC-SKU-2", "quantity": 2}
            ])
        )
        
        order2 = Order.objects.create(
            customer=customer,
            transaction_id="CALC-002",
            reference_number="REF-002",
            weight_lb=15.0,  # Above weight threshold
            total_item_qty=5,
            close_date=timezone.now() - timedelta(days=3),
            sku_quantity=json.dumps([
                {"sku": "CALC-SKU-1", "quantity": 2},
                {"sku": "CALC-SKU-2", "quantity": 3}
            ])
        )
        
        return {
            "customer": customer,
            "services": {
                "shipping": shipping_service,
                "handling": handling_service
            },
            "customer_services": {
                "shipping": cs_shipping,
                "handling": cs_handling
            },
            "rule_groups": {
                "weight": weight_rule_group
            },
            "rules": {
                "weight": weight_rule
            },
            "orders": {
                "order1": order1,
                "order2": order2
            }
        }
    
    def test_rule_evaluation(self, setup_test_data):
        """Test rule evaluation using the RuleEvaluator."""
        # Extract test data
        weight_rule = setup_test_data["rules"]["weight"]
        order1 = setup_test_data["orders"]["order1"]
        order2 = setup_test_data["orders"]["order2"]
        
        # Evaluate weight rule on orders
        result1 = RuleEvaluator.evaluate_rule(weight_rule, order1)
        result2 = RuleEvaluator.evaluate_rule(weight_rule, order2)
        
        # Order 1 is below weight threshold, so rule should not apply
        assert result1 is False
        
        # Order 2 is above weight threshold, so rule should apply
        assert result2 is True
    
    def test_rule_group_evaluation(self, setup_test_data):
        """Test rule group evaluation using the RuleEvaluator."""
        # Extract test data
        weight_rule_group = setup_test_data["rule_groups"]["weight"]
        order1 = setup_test_data["orders"]["order1"]
        order2 = setup_test_data["orders"]["order2"]
        
        # Evaluate weight rule group on orders
        result1 = RuleEvaluator.evaluate_rule_group(weight_rule_group, order1)
        result2 = RuleEvaluator.evaluate_rule_group(weight_rule_group, order2)
        
        # Order 1 is below weight threshold, so rule group should not apply
        assert result1 is False
        
        # Order 2 is above weight threshold, so rule group should apply
        assert result2 is True
    
    def test_billing_calculator_with_rules(self, setup_test_data):
        """Test billing calculation with rules."""
        # Extract test data
        customer = setup_test_data["customer"]
        
        # Create calculator for date range including both orders
        start_date = timezone.now() - timedelta(days=10)
        end_date = timezone.now()
        calculator = BillingCalculator(customer.id, start_date, end_date)
        
        # Generate report
        report = calculator.generate_report()
        
        # Verify the report
        assert report.customer_id == customer.id
        assert len(report.order_costs) == 2
        
        # Check order costs
        for order_cost in report.order_costs:
            if order_cost.order_id == "CALC-001":
                # Order 1: Below weight threshold, so only handling fee applies
                # Handling: 3 items * $2.50 = $7.50
                assert len(order_cost.service_costs) == 1
                assert any(sc.service_name == "Handling" for sc in order_cost.service_costs)
                assert order_cost.total_amount == Decimal("7.50")
            elif order_cost.order_id == "CALC-002":
                # Order 2: Above weight threshold, so both shipping and handling fees apply
                # Shipping: $15.00 (flat fee)
                # Handling: 5 items * $2.50 = $12.50
                # Total: $27.50
                assert len(order_cost.service_costs) == 2
                assert any(sc.service_name == "Shipping" for sc in order_cost.service_costs)
                assert any(sc.service_name == "Handling" for sc in order_cost.service_costs)
                assert order_cost.total_amount == Decimal("27.50")
        
        # Check service totals
        # Handling: $7.50 + $12.50 = $20.00
        # Shipping: $0.00 + $15.00 = $15.00
        # Total: $35.00
        shipping_service_id = setup_test_data["services"]["shipping"].id
        handling_service_id = setup_test_data["services"]["handling"].id
        
        assert report.service_totals[handling_service_id] == Decimal("20.00")
        assert report.service_totals[shipping_service_id] == Decimal("15.00")
        assert report.total_amount == Decimal("35.00")
    
    def test_data_format_conversion(self, setup_test_data):
        """Test the data format conversion for the billing calculator."""
        # Extract test data
        customer = setup_test_data["customer"]
        
        # Create calculator
        start_date = timezone.now() - timedelta(days=10)
        end_date = timezone.now()
        calculator = BillingCalculator(customer.id, start_date, end_date)
        
        # Generate report
        report = calculator.generate_report()
        
        # Convert to dictionary and JSON formats
        report_dict = calculator.to_dict()
        report_json = calculator.to_json()
        
        # Verify dictionary format
        assert report_dict["customer_id"] == customer.id
        assert "orders" in report_dict
        assert "service_totals" in report_dict
        assert "total_amount" in report_dict
        
        # Verify JSON format
        assert isinstance(report_json, str)
        # Should be valid JSON
        json_data = json.loads(report_json)
        assert json_data["customer_id"] == customer.id
    
    def test_csv_format(self, setup_test_data):
        """Test the CSV format for the billing calculator."""
        # Extract test data
        customer = setup_test_data["customer"]
        
        # Create calculator
        start_date = timezone.now() - timedelta(days=10)
        end_date = timezone.now()
        calculator = BillingCalculator(customer.id, start_date, end_date)
        
        # Generate report
        report = calculator.generate_report()
        
        # Convert to CSV format
        csv_data = calculator.to_csv()
        
        # Verify CSV format
        assert isinstance(csv_data, str)
        
        # Check header
        assert "Order ID,Service ID,Service Name,Amount" in csv_data
        
        # Check content
        lines = csv_data.strip().split("\n")
        assert len(lines) == 3  # Header + 2 orders with at least one service each
        
        # Verify the first data line contains an order ID
        assert any(order.transaction_id in lines[1] for order in 
                 [setup_test_data["orders"]["order1"], setup_test_data["orders"]["order2"]])
    
    def test_multiple_rule_groups(self, setup_test_data):
        """Test billing calculation with multiple rule groups."""
        # Extract test data
        customer = setup_test_data["customer"]
        cs_handling = setup_test_data["customer_services"]["handling"]
        
        # Create another rule group for the handling service
        sku_rule_group = RuleGroup.objects.create(
            customer_service=cs_handling,
            name="SKU Rules",
            logic_operator="OR"
        )
        
        # Add rule to apply handling fee only for specific SKUs
        sku_rule = Rule.objects.create(
            rule_group=sku_rule_group,
            field="sku_quantity",
            operator="contains",
            value="CALC-SKU-1"  # Only apply handling fee for this SKU
        )
        
        # Create a new order with only the other SKU
        order3 = Order.objects.create(
            customer=customer,
            transaction_id="CALC-003",
            reference_number="REF-003",
            weight_lb=15.0,  # Above weight threshold
            total_item_qty=2,
            close_date=timezone.now() - timedelta(days=1),
            sku_quantity=json.dumps([
                {"sku": "CALC-SKU-3", "quantity": 2}  # Not the SKU in the rule
            ])
        )
        
        # Create calculator for date range including all orders
        start_date = timezone.now() - timedelta(days=10)
        end_date = timezone.now()
        calculator = BillingCalculator(customer.id, start_date, end_date)
        
        # Generate report
        report = calculator.generate_report()
        
        # Check the new order
        for order_cost in report.order_costs:
            if order_cost.order_id == "CALC-003":
                # Order 3: Above weight threshold but doesn't have the required SKU
                # Shipping: $15.00 (flat fee)
                # Handling: $0.00 (doesn't contain the required SKU)
                # Total: $15.00
                assert len(order_cost.service_costs) == 1
                assert order_cost.service_costs[0].service_name == "Shipping"
                assert order_cost.total_amount == Decimal("15.00")