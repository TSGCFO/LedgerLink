import pytest
import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from customers.models import Customer
from orders.models import Order
from products.models import Product
from rules.models import RuleGroup, Rule, AdvancedRule
from billing.models import BillingReport
from billing.billing_calculator import BillingCalculator
from conftest import MockOrderSKUView, MockCustomerServiceView


class BillingRulesIntegrationTest(TestCase):
    """Integration tests for Billing and Rules systems"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="contact@test.com",
            phone="555-1234",
            is_active=True
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name="Test Product 1",
            sku="SKU001",
            description="Test product 1",
            price=10.00
        )
        
        self.product2 = Product.objects.create(
            name="Test Product 2",
            sku="SKU002",
            description="Test product 2",
            price=15.00
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            status="completed",
            order_date=timezone.now() - timedelta(days=5),
            priority="normal",
            sku_quantities=json.dumps({"SKU001": 10, "SKU002": 5})
        )
        
        # Create rule group
        self.rule_group = RuleGroup.objects.create(
            name="Test Rule Group",
            description="Test rule group for integration tests"
        )
        
        # Create basic rule
        self.basic_rule = Rule.objects.create(
            rule_group=self.rule_group,
            name="Quantity Rule",
            description="Rule based on quantity",
            field="quantity",
            operator="gt",
            value="5",
            price_adjustment=2.50,
            adjustment_type="per_item"
        )
        
        # Create advanced rule with tier-based pricing
        tier_config = {
            "tiers": [
                {"min": 0, "max": 5, "value": 1.00},
                {"min": 6, "max": 15, "value": 0.75},
                {"min": 16, "max": 999999, "value": 0.50}
            ]
        }
        
        advanced_rule_json = {
            "condition": {
                "field": "sku_id",
                "operator": "in",
                "value": ["SKU001", "SKU002"]
            },
            "calculation": {
                "type": "case_based_tier",
                "field": "quantity"
            },
            "tier_config": tier_config
        }
        
        self.advanced_rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            name="Tier-based Rule",
            description="Advanced rule with tier-based pricing",
            conditions=json.dumps(advanced_rule_json['condition']),
            calculations=json.dumps(advanced_rule_json['calculation']),
            tier_config=json.dumps(advanced_rule_json['tier_config'])
        )
    
    def test_billing_with_rules(self):
        """Test that billing calculation correctly applies rules"""
        # Mock the view results that would come from OrderSKUView
        sku_view_results = [
            MockOrderSKUView(
                id=self.order.id,
                status=self.order.status,
                order_date=self.order.order_date,
                priority=self.order.priority,
                customer_id=self.customer.id,
                sku_id="SKU001",
                quantity=10
            ),
            MockOrderSKUView(
                id=self.order.id,
                status=self.order.status,
                order_date=self.order.order_date,
                priority=self.order.priority,
                customer_id=self.customer.id,
                sku_id="SKU002",
                quantity=5
            )
        ]
        
        # Create a billing calculator
        calculator = BillingCalculator(self.customer)
        
        # Calculate billing for the order's SKUs
        # In a real scenario, these would come from the OrderSKUView
        billing_items = []
        for sku_view in sku_view_results:
            product = Product.objects.get(sku=sku_view.sku_id)
            
            # Calculate base line item
            item_total = product.price * sku_view.quantity
            
            # Check if basic rule applies
            rule_adjustments = []
            if sku_view.quantity > int(self.basic_rule.value):
                adjustment = self.basic_rule.price_adjustment * sku_view.quantity
                rule_adjustments.append({
                    'rule_id': self.basic_rule.id,
                    'rule_name': self.basic_rule.name,
                    'amount': adjustment
                })
                item_total += adjustment
            
            # Look up appropriate tier for advanced rule
            tier_config = json.loads(self.advanced_rule.tier_config)
            tier_value = None
            for tier in tier_config["tiers"]:
                if tier["min"] <= sku_view.quantity <= tier["max"]:
                    tier_value = tier["value"]
                    break
            
            if tier_value is not None:
                adjustment = tier_value * sku_view.quantity
                rule_adjustments.append({
                    'rule_id': self.advanced_rule.id,
                    'rule_name': self.advanced_rule.name,
                    'amount': adjustment
                })
                item_total += adjustment
            
            billing_items.append({
                'sku': sku_view.sku_id,
                'quantity': sku_view.quantity,
                'base_price': product.price,
                'rule_adjustments': rule_adjustments,
                'total': item_total
            })
        
        # Calculate expected totals
        expected_sku001_total = (10 * 10.00) + (10 * 2.50) + (10 * 0.75)  # Base + basic rule + tier
        expected_sku002_total = (5 * 15.00) + (5 * 1.00)  # Base + tier (not enough for basic rule)
        expected_total = expected_sku001_total + expected_sku002_total
        
        # Create billing report
        report = BillingReport.objects.create(
            customer=self.customer,
            billing_date=timezone.now(),
            total_amount=expected_total,
            created_by=self.user,
            details=json.dumps(billing_items)
        )
        
        # Verify the report details
        report_details = json.loads(report.details)
        self.assertEqual(len(report_details), 2)
        
        # Check first item (SKU001)
        sku001_item = next(item for item in report_details if item['sku'] == 'SKU001')
        self.assertEqual(sku001_item['quantity'], 10)
        self.assertEqual(Decimal(sku001_item['total']), Decimal(expected_sku001_total))
        
        # Check second item (SKU002)
        sku002_item = next(item for item in report_details if item['sku'] == 'SKU002')
        self.assertEqual(sku002_item['quantity'], 5)
        self.assertEqual(Decimal(sku002_item['total']), Decimal(expected_sku002_total))
        
        # Verify total amount
        self.assertEqual(report.total_amount, Decimal(expected_total))
        
    def test_rule_condition_evaluator(self):
        """Test the rule condition evaluator integration with order data"""
        # Create an advanced rule with complex conditions
        complex_rule_json = {
            "condition": {
                "operator": "and",
                "conditions": [
                    {
                        "field": "sku_id",
                        "operator": "eq",
                        "value": "SKU001"
                    },
                    {
                        "field": "quantity",
                        "operator": "gte",
                        "value": 5
                    }
                ]
            },
            "calculation": {
                "type": "fixed",
                "value": 5.00
            }
        }
        
        complex_rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            name="Complex Rule",
            description="Rule with complex conditions",
            conditions=json.dumps(complex_rule_json['condition']),
            calculations=json.dumps(complex_rule_json['calculation'])
        )
        
        # Mock order SKU data
        sku_data = {
            "sku_id": "SKU001",
            "quantity": 10
        }
        
        # Evaluate the rule conditions
        conditions = json.loads(complex_rule.conditions)
        
        # Helper functions to evaluate conditions (simplified version)
        def evaluate_condition(condition, data):
            if "operator" in condition and condition["operator"] in ["and", "or"]:
                # Complex condition
                results = [evaluate_condition(sub_cond, data) for sub_cond in condition["conditions"]]
                if condition["operator"] == "and":
                    return all(results)
                else:  # "or"
                    return any(results)
            else:
                # Simple condition
                field = condition["field"]
                operator = condition["operator"]
                value = condition["value"]
                
                if field not in data:
                    return False
                
                field_value = data[field]
                
                if operator == "eq":
                    return field_value == value
                elif operator == "ne":
                    return field_value != value
                elif operator == "gt":
                    return field_value > value if isinstance(field_value, (int, float)) else False
                elif operator == "gte":
                    return field_value >= value if isinstance(field_value, (int, float)) else False
                elif operator == "lt":
                    return field_value < value if isinstance(field_value, (int, float)) else False
                elif operator == "lte":
                    return field_value <= value if isinstance(field_value, (int, float)) else False
                elif operator == "in":
                    return field_value in value if isinstance(value, list) else False
                else:
                    return False
        
        # Evaluate the rule
        result = evaluate_condition(conditions, sku_data)
        
        # This rule should match our test data
        self.assertTrue(result)
        
        # Now test with data that shouldn't match
        non_matching_data = {
            "sku_id": "SKU002",  # Different SKU
            "quantity": 10
        }
        
        # Evaluate again
        result = evaluate_condition(conditions, non_matching_data)
        
        # This should not match
        self.assertFalse(result)