"""
Tests for the integration between the rules system and billing calculator.

These tests verify that the billing system correctly applies rules
from the rule system when calculating billing reports.
"""

from django.test import TestCase
from decimal import Decimal
import json
from datetime import datetime, timezone

from customers.models import Customer
from services.models import Service
from customer_services.models import CustomerService
from rules.models import Rule, RuleGroup, AdvancedRule
from orders.models import Order
from billing.billing_calculator import BillingCalculator, RuleEvaluator


class RuleIntegrationTest(TestCase):
    """Test integration between rules and billing systems."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for rule integration tests."""
        # Create test customer
        cls.customer = Customer.objects.create(
            company_name="Rule Integration Test Co",
            contact_name="Test Contact",
            email="rule-integration@example.com"
        )
        
        # Create test services with different charge types
        cls.service1 = Service.objects.create(
            service_name="Conditional Service 1",
            description="Service with basic rules",
            charge_type="single"
        )
        
        cls.service2 = Service.objects.create(
            service_name="Conditional Service 2",
            description="Service with advanced rules",
            charge_type="quantity"
        )
        
        cls.service3 = Service.objects.create(
            service_name="Always Apply Service",
            description="Service with no rules (always applies)",
            charge_type="single"
        )
        
        # Create customer services
        cls.customer_service1 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service1,
            unit_price=Decimal('50.00')
        )
        
        cls.customer_service2 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service2,
            unit_price=Decimal('10.00')
        )
        
        cls.customer_service3 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service3,
            unit_price=Decimal('25.00')
        )
        
        # Create rule groups
        cls.rule_group1 = RuleGroup.objects.create(
            customer_service=cls.customer_service1,
            logic_operator="AND"
        )
        
        cls.rule_group2 = RuleGroup.objects.create(
            customer_service=cls.customer_service2,
            logic_operator="OR"
        )
        
        # Create basic rules
        cls.rule1 = Rule.objects.create(
            rule_group=cls.rule_group1,
            field="weight_lb",
            operator="gt",
            value="20"
        )
        
        cls.rule2 = Rule.objects.create(
            rule_group=cls.rule_group1,
            field="ship_to_country",
            operator="eq",
            value="US"
        )
        
        cls.rule3 = Rule.objects.create(
            rule_group=cls.rule_group2,
            field="carrier",
            operator="contains",
            value="UPS"
        )
        
        cls.rule4 = Rule.objects.create(
            rule_group=cls.rule_group2,
            field="sku_quantity",
            operator="contains",
            value="PREMIUM-SKU"
        )
        
        # Add methods to Order for case-based calculations if needed
        def get_case_summary(order, exclude_skus=None):
            skus = json.loads(order.sku_quantity) if order.sku_quantity else {}
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
                
            skus = json.loads(order.sku_quantity) if order.sku_quantity else {}
            for sku in skus.keys():
                if sku not in exclude_skus:
                    return False
            return True
        
        # Add methods to Order model
        Order.get_case_summary = get_case_summary
        Order.has_only_excluded_skus = has_only_excluded_skus
    
    def create_test_order(self, **kwargs):
        """Helper method to create test orders with default values."""
        defaults = {
            'transaction_id': f"TEST-{datetime.now().timestamp()}",
            'customer': self.customer,
            'reference_number': 'REF-001',
            'ship_to_name': 'Test Recipient',
            'ship_to_company': 'Test Company',
            'ship_to_address1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_to_country': 'US',
            'weight_lb': 25,
            'carrier': 'UPS Ground',
            'close_date': datetime.now(timezone.utc),
            'total_item_qty': 10,
            'line_items': 2,
            'sku_quantity': json.dumps([
                {"sku": "REGULAR-SKU", "quantity": 5},
                {"sku": "PREMIUM-SKU", "quantity": 5}
            ])
        }
        
        # Update defaults with provided values
        defaults.update(kwargs)
        
        return Order.objects.create(**defaults)
    
    def test_all_rules_apply(self):
        """Test when all rules apply to an order."""
        order = self.create_test_order()
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # All services should apply to this order
        service_ids = {sc.service_id for oc in report.order_costs for sc in oc.service_costs}
        self.assertEqual(3, len(service_ids))
        self.assertIn(self.service1.id, service_ids)
        self.assertIn(self.service2.id, service_ids)
        self.assertIn(self.service3.id, service_ids)
        
        # Calculate expected costs
        # Service 1: $50 (single charge)
        # Service 2: $100 (quantity charge: $10 × 10 items)
        # Service 3: $25 (always applies)
        expected_total = Decimal('175.00')
        
        # Find this order in the report
        order_cost = next((oc for oc in report.order_costs if oc.order_id == order.transaction_id), None)
        self.assertIsNotNone(order_cost)
        self.assertEqual(expected_total, order_cost.total_amount)
    
    def test_weight_rule_not_apply(self):
        """Test when weight rule doesn't apply."""
        order = self.create_test_order(weight_lb=15)  # Below 20 lb threshold
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Service 1 should not apply (weight rule fails)
        service_ids = {sc.service_id for oc in report.order_costs for sc in oc.service_costs}
        self.assertEqual(2, len(service_ids))
        self.assertNotIn(self.service1.id, service_ids)
        self.assertIn(self.service2.id, service_ids)
        self.assertIn(self.service3.id, service_ids)
        
        # Calculate expected costs
        # Service 2: $100 (quantity charge: $10 × 10 items)
        # Service 3: $25 (always applies)
        expected_total = Decimal('125.00')
        
        # Find this order in the report
        order_cost = next((oc for oc in report.order_costs if oc.order_id == order.transaction_id), None)
        self.assertIsNotNone(order_cost)
        self.assertEqual(expected_total, order_cost.total_amount)
    
    def test_country_rule_not_apply(self):
        """Test when country rule doesn't apply."""
        order = self.create_test_order(ship_to_country='CA')  # Not US
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Service 1 should not apply (country rule fails)
        service_ids = {sc.service_id for oc in report.order_costs for sc in oc.service_costs}
        self.assertEqual(2, len(service_ids))
        self.assertNotIn(self.service1.id, service_ids)
        self.assertIn(self.service2.id, service_ids)
        self.assertIn(self.service3.id, service_ids)
    
    def test_carrier_and_sku_rules_not_apply(self):
        """Test when both carrier and SKU rules don't apply (OR group)."""
        # Create order with FedEx carrier and no PREMIUM-SKU
        order = self.create_test_order(
            carrier='FedEx Ground',
            sku_quantity=json.dumps([
                {"sku": "REGULAR-SKU", "quantity": 10}
            ])
        )
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Service 2 should not apply (both carrier and SKU rules fail in OR group)
        service_ids = {sc.service_id for oc in report.order_costs for sc in oc.service_costs}
        self.assertEqual(2, len(service_ids))
        self.assertIn(self.service1.id, service_ids)
        self.assertNotIn(self.service2.id, service_ids)
        self.assertIn(self.service3.id, service_ids)
        
        # Calculate expected costs
        # Service 1: $50 (single charge)
        # Service 3: $25 (always applies)
        expected_total = Decimal('75.00')
        
        # Find this order in the report
        order_cost = next((oc for oc in report.order_costs if oc.order_id == order.transaction_id), None)
        self.assertIsNotNone(order_cost)
        self.assertEqual(expected_total, order_cost.total_amount)
    
    def test_carrier_rule_applies_but_sku_rule_not(self):
        """Test when carrier rule applies but SKU rule doesn't (OR group)."""
        # Create order with UPS carrier but no PREMIUM-SKU
        order = self.create_test_order(
            sku_quantity=json.dumps([
                {"sku": "REGULAR-SKU", "quantity": 10}
            ])
        )
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Service 2 should apply (carrier rule passes in OR group)
        service_ids = {sc.service_id for oc in report.order_costs for sc in oc.service_costs}
        self.assertEqual(3, len(service_ids))
        self.assertIn(self.service1.id, service_ids)
        self.assertIn(self.service2.id, service_ids)
        self.assertIn(self.service3.id, service_ids)
    
    def test_rule_group_logic_operators(self):
        """Test different logic operators in rule groups."""
        # Create a new rule group with NOT logic
        rule_group3 = RuleGroup.objects.create(
            customer_service=self.customer_service2,
            logic_operator="NOT"
        )
        
        # Add a rule to exclude domestic shipments
        Rule.objects.create(
            rule_group=rule_group3,
            field="ship_to_country",
            operator="eq",
            value="US"
        )
        
        # Create orders for domestic and international shipments
        domestic_order = self.create_test_order(
            transaction_id="DOMESTIC-ORDER",
            ship_to_country="US"
        )
        
        international_order = self.create_test_order(
            transaction_id="INTL-ORDER",
            ship_to_country="GB"
        )
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Find orders in the report
        domestic_cost = next((oc for oc in report.order_costs if oc.order_id == "DOMESTIC-ORDER"), None)
        intl_cost = next((oc for oc in report.order_costs if oc.order_id == "INTL-ORDER"), None)
        
        self.assertIsNotNone(domestic_cost)
        self.assertIsNotNone(intl_cost)
        
        # Check service 2 (NOT rule should exclude domestic, but OR rule from rule_group2 includes it)
        domestic_service2 = any(sc.service_id == self.service2.id for sc in domestic_cost.service_costs)
        intl_service2 = any(sc.service_id == self.service2.id for sc in intl_cost.service_costs)
        
        # Both should have service 2 because the OR rule from rule_group2 will include them
        self.assertTrue(domestic_service2)
        self.assertTrue(intl_service2)
        
        # Now remove the original rule group to see the effect of just the NOT rule
        self.rule_group2.delete()
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Find orders in the report
        domestic_cost = next((oc for oc in report.order_costs if oc.order_id == "DOMESTIC-ORDER"), None)
        intl_cost = next((oc for oc in report.order_costs if oc.order_id == "INTL-ORDER"), None)
        
        # Check service 2 (NOT rule should exclude domestic orders but include international)
        domestic_service2 = any(sc.service_id == self.service2.id for sc in domestic_cost.service_costs)
        intl_service2 = any(sc.service_id == self.service2.id for sc in intl_cost.service_costs)
        
        self.assertFalse(domestic_service2)  # Domestic should NOT get the service
        self.assertTrue(intl_service2)       # International should get the service
    
    def test_advanced_rule_integration(self):
        """Test integration with advanced rules."""
        # Create a new service with advanced rule
        service_adv = Service.objects.create(
            service_name="Advanced Rule Service",
            description="Service with advanced rules",
            charge_type="quantity"
        )
        
        customer_service_adv = CustomerService.objects.create(
            customer=self.customer,
            service=service_adv,
            unit_price=Decimal('15.00')
        )
        
        rule_group_adv = RuleGroup.objects.create(
            customer_service=customer_service_adv,
            logic_operator="AND"
        )
        
        # Create advanced rule
        advanced_rule = AdvancedRule.objects.create(
            rule_group=rule_group_adv,
            field="weight_lb",
            operator="gt",
            value="0",
            conditions={
                "type": "and",
                "conditions": [
                    {"field": "weight_lb", "operator": "gt", "value": 15},
                    {"field": "ship_to_country", "operator": "in", "value": ["US", "CA"]}
                ]
            },
            calculations=[
                {"type": "base", "value": 1.0}
            ]
        )
        
        # Create orders with different weights and countries
        order1 = self.create_test_order(
            transaction_id="ADV-ORDER-1",
            weight_lb=20,
            ship_to_country="US"
        )
        
        order2 = self.create_test_order(
            transaction_id="ADV-ORDER-2",
            weight_lb=10,  # Below threshold
            ship_to_country="US"
        )
        
        order3 = self.create_test_order(
            transaction_id="ADV-ORDER-3",
            weight_lb=20,
            ship_to_country="FR"  # Not in the list
        )
        
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Find orders in the report
        order1_cost = next((oc for oc in report.order_costs if oc.order_id == "ADV-ORDER-1"), None)
        order2_cost = next((oc for oc in report.order_costs if oc.order_id == "ADV-ORDER-2"), None)
        order3_cost = next((oc for oc in report.order_costs if oc.order_id == "ADV-ORDER-3"), None)
        
        # Check advanced service (should only apply to order1)
        order1_adv = any(sc.service_id == service_adv.id for sc in order1_cost.service_costs)
        order2_adv = any(sc.service_id == service_adv.id for sc in order2_cost.service_costs)
        order3_adv = any(sc.service_id == service_adv.id for sc in order3_cost.service_costs)
        
        self.assertTrue(order1_adv)    # Meets all conditions
        self.assertFalse(order2_adv)   # Weight too low
        self.assertFalse(order3_adv)   # Wrong country


class RuleOperatorIntegrationTest(TestCase):
    """Test specific operator integration between rules and billing."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for operator integration tests."""
        # Create test customer
        cls.customer = Customer.objects.create(
            company_name="Operator Test Co",
            contact_name="Test Contact",
            email="operator-test@example.com"
        )
        
        # Create test service
        cls.service = Service.objects.create(
            service_name="Operator Test Service",
            description="Service for operator testing",
            charge_type="single"
        )
        
        # Create customer service
        cls.customer_service = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('50.00')
        )
    
    def create_rule_group(self, logic_operator="AND"):
        """Helper to create a rule group."""
        return RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator=logic_operator
        )
    
    def create_rule(self, rule_group, field, operator, value):
        """Helper to create a rule."""
        return Rule.objects.create(
            rule_group=rule_group,
            field=field,
            operator=operator,
            value=value
        )
    
    def create_test_order(self, **kwargs):
        """Helper to create a test order."""
        defaults = {
            'transaction_id': f"OP-TEST-{datetime.now().timestamp()}",
            'customer': self.customer,
            'reference_number': 'REF-OP-001',
            'ship_to_name': 'Operator Test',
            'ship_to_company': 'Operator Co',
            'ship_to_address1': '123 Operator St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_to_country': 'US',
            'close_date': datetime.now(timezone.utc)
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)
    
    def test_ne_neq_operators(self):
        """Test ne/neq operators in rules integration."""
        # Create rule groups for different operator tests
        rule_group_ne = self.create_rule_group()
        rule_group_neq = self.create_rule_group()
        
        # Create rules with ne and neq operators
        self.create_rule(rule_group_ne, "ship_to_country", "ne", "CA")
        self.create_rule(rule_group_neq, "ship_to_country", "neq", "CA")
        
        # Create test orders
        order_us = self.create_test_order(
            transaction_id="OP-NE-US",
            ship_to_country="US"
        )
        
        order_ca = self.create_test_order(
            transaction_id="OP-NE-CA",
            ship_to_country="CA"
        )
        
        # Replace customer service with ne rule group
        self.customer_service.rulegroup_set.all().delete()
        rule_group_ne.customer_service = self.customer_service
        rule_group_ne.save()
        
        # Calculate with ne rule
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report_ne = calculator.generate_report()
        
        # Replace with neq rule group
        self.customer_service.rulegroup_set.all().delete()
        rule_group_neq.customer_service = self.customer_service
        rule_group_neq.save()
        
        # Calculate with neq rule
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report_neq = calculator.generate_report()
        
        # Verify both operators behave identically
        ne_us_has_service = any(
            oc.order_id == "OP-NE-US" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_ne.order_costs
        )
        
        ne_ca_has_service = any(
            oc.order_id == "OP-NE-CA" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_ne.order_costs
        )
        
        neq_us_has_service = any(
            oc.order_id == "OP-NE-US" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_neq.order_costs
        )
        
        neq_ca_has_service = any(
            oc.order_id == "OP-NE-CA" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_neq.order_costs
        )
        
        # US orders should have the service, CA orders should not
        self.assertTrue(ne_us_has_service)
        self.assertFalse(ne_ca_has_service)
        self.assertTrue(neq_us_has_service)
        self.assertFalse(neq_ca_has_service)
    
    def test_ncontains_not_contains_operators(self):
        """Test ncontains/not_contains operators in rules integration."""
        # Create rule groups for different operator tests
        rule_group_ncontains = self.create_rule_group()
        rule_group_not_contains = self.create_rule_group()
        
        # Create rules with ncontains and not_contains operators
        self.create_rule(rule_group_ncontains, "ship_to_name", "ncontains", "Premium")
        self.create_rule(rule_group_not_contains, "ship_to_name", "not_contains", "Premium")
        
        # Create test orders
        order_regular = self.create_test_order(
            transaction_id="OP-NC-REG",
            ship_to_name="Regular Customer"
        )
        
        order_premium = self.create_test_order(
            transaction_id="OP-NC-PREM",
            ship_to_name="Premium Customer"
        )
        
        # Replace customer service with ncontains rule group
        self.customer_service.rulegroup_set.all().delete()
        rule_group_ncontains.customer_service = self.customer_service
        rule_group_ncontains.save()
        
        # Calculate with ncontains rule
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report_ncontains = calculator.generate_report()
        
        # Replace with not_contains rule group
        self.customer_service.rulegroup_set.all().delete()
        rule_group_not_contains.customer_service = self.customer_service
        rule_group_not_contains.save()
        
        # Calculate with not_contains rule
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report_not_contains = calculator.generate_report()
        
        # Verify both operators behave identically
        nc_reg_has_service = any(
            oc.order_id == "OP-NC-REG" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_ncontains.order_costs
        )
        
        nc_prem_has_service = any(
            oc.order_id == "OP-NC-PREM" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_ncontains.order_costs
        )
        
        notc_reg_has_service = any(
            oc.order_id == "OP-NC-REG" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_not_contains.order_costs
        )
        
        notc_prem_has_service = any(
            oc.order_id == "OP-NC-PREM" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report_not_contains.order_costs
        )
        
        # Regular orders should have the service, Premium orders should not
        self.assertTrue(nc_reg_has_service)
        self.assertFalse(nc_prem_has_service)
        self.assertTrue(notc_reg_has_service)
        self.assertFalse(notc_prem_has_service)
    
    def test_sku_operators(self):
        """Test SKU-specific operators in rules integration."""
        # Create rule group for SKU tests
        rule_group = self.create_rule_group()
        
        # Create rule that only includes orders with premium SKUs
        self.create_rule(rule_group, "sku_quantity", "contains", "PREMIUM")
        
        # Create test orders
        order_premium = self.create_test_order(
            transaction_id="SKU-PREM",
            sku_quantity=json.dumps([
                {"sku": "PREMIUM-123", "quantity": 5},
                {"sku": "REG-456", "quantity": 10}
            ])
        )
        
        order_regular = self.create_test_order(
            transaction_id="SKU-REG",
            sku_quantity=json.dumps([
                {"sku": "REG-456", "quantity": 10},
                {"sku": "REG-789", "quantity": 15}
            ])
        )
        
        # Use the rule group
        self.customer_service.rulegroup_set.all().delete()
        rule_group.customer_service = self.customer_service
        rule_group.save()
        
        # Calculate billing
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Verify SKU-based rule application
        premium_has_service = any(
            oc.order_id == "SKU-PREM" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report.order_costs
        )
        
        regular_has_service = any(
            oc.order_id == "SKU-REG" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report.order_costs
        )
        
        # Premium order should have the service, regular order should not
        self.assertTrue(premium_has_service)
        self.assertFalse(regular_has_service)
        
        # Now create a rule that excludes orders with premium SKUs
        rule_group_exclude = self.create_rule_group()
        self.create_rule(rule_group_exclude, "sku_quantity", "ncontains", "PREMIUM")
        
        # Use this rule group
        self.customer_service.rulegroup_set.all().delete()
        rule_group_exclude.customer_service = self.customer_service
        rule_group_exclude.save()
        
        # Calculate billing
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc)
        )
        report = calculator.generate_report()
        
        # Verify SKU-based rule application
        premium_has_service = any(
            oc.order_id == "SKU-PREM" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report.order_costs
        )
        
        regular_has_service = any(
            oc.order_id == "SKU-REG" and any(sc.service_id == self.service.id for sc in oc.service_costs)
            for oc in report.order_costs
        )
        
        # Premium order should NOT have the service, regular order should
        self.assertFalse(premium_has_service)
        self.assertTrue(regular_has_service)


if __name__ == '__main__':
    unittest.main()