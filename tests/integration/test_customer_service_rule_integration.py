import pytest
import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from customers.models import Customer
from services.models import Service
from rules.models import RuleGroup, AdvancedRule
from customer_services.models import CustomerService
from conftest import MockCustomerServiceView


class CustomerServiceRuleIntegrationTest(TestCase):
    """Integration tests for Customer Services and Rules"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create test customers
        self.customer1 = Customer.objects.create(
            company_name="Large Company",
            contact_name="John Doe",
            email="john@large.com",
            phone="555-1234",
            is_active=True
        )
        
        self.customer2 = Customer.objects.create(
            company_name="Small Company",
            contact_name="Jane Smith",
            email="jane@small.com",
            phone="555-5678",
            is_active=True
        )
        
        # Create test services
        self.service1 = Service.objects.create(
            name="Premium Support",
            description="24/7 support service",
            base_price=100.00,
            charge_type="flat"
        )
        
        self.service2 = Service.objects.create(
            name="Design Service",
            description="Custom design service",
            base_price=75.00,
            charge_type="hourly"
        )
        
        # Create customer-specific services
        self.cs1 = CustomerService.objects.create(
            customer=self.customer1,
            service=self.service1,
            custom_price=80.00  # Discounted for large company
        )
        
        self.cs2 = CustomerService.objects.create(
            customer=self.customer2,
            service=self.service1,
            custom_price=120.00  # Premium price for small company
        )
        
        # Create rule group for service pricing
        self.rule_group = RuleGroup.objects.create(
            name="Service Rules",
            description="Rules for service pricing"
        )
        
        # Create advanced rule for volume discounts
        volume_rule_json = {
            "condition": {
                "field": "company_size",
                "operator": "gt",
                "value": 50
            },
            "calculation": {
                "type": "percent_discount",
                "value": 15.0
            }
        }
        
        self.volume_rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            name="Volume Discount",
            description="Discount for large companies",
            conditions=json.dumps(volume_rule_json["condition"]),
            calculations=json.dumps(volume_rule_json["calculation"])
        )
        
        # Create loyalty rule based on customer age
        loyalty_rule_json = {
            "condition": {
                "field": "customer_age",
                "operator": "gte",
                "value": 3
            },
            "calculation": {
                "type": "percent_discount",
                "value": 10.0
            }
        }
        
        self.loyalty_rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            name="Loyalty Discount",
            description="Discount for long-term customers",
            conditions=json.dumps(loyalty_rule_json["condition"]),
            calculations=json.dumps(loyalty_rule_json["calculation"])
        )
    
    def test_customer_service_with_rules(self):
        """Test that customer service pricing works with rule conditions"""
        # Mock the customer view results
        cs_view_results = [
            MockCustomerServiceView(
                id=self.cs1.id,
                customer_id=self.customer1.id,
                service_id=self.service1.id,
                custom_price=self.cs1.custom_price,
                service_name=self.service1.name,
                charge_type=self.service1.charge_type,
                company_name=self.customer1.company_name
            ),
            MockCustomerServiceView(
                id=self.cs2.id,
                customer_id=self.customer2.id,
                service_id=self.service1.id,
                custom_price=self.cs2.custom_price,
                service_name=self.service1.name,
                charge_type=self.service1.charge_type,
                company_name=self.customer2.company_name
            )
        ]
        
        # Test data for customer1 (large company)
        customer1_data = {
            "customer_id": self.customer1.id,
            "company_size": 100,  # Large company
            "customer_age": 5     # Long-term customer
        }
        
        # Test data for customer2 (small company)
        customer2_data = {
            "customer_id": self.customer2.id,
            "company_size": 10,   # Small company
            "customer_age": 1     # New customer
        }
        
        # Helper function to evaluate advanced rule
        def evaluate_rule(rule, data):
            conditions = json.loads(rule.conditions)
            calculations = json.loads(rule.calculations)
            
            # Check if rule conditions match
            field = conditions["field"]
            operator = conditions["operator"]
            value = conditions["value"]
            
            if field not in data:
                return 0.0
            
            field_value = data[field]
            condition_met = False
            
            if operator == "eq":
                condition_met = field_value == value
            elif operator == "gt":
                condition_met = field_value > value
            elif operator == "gte":
                condition_met = field_value >= value
            elif operator == "lt":
                condition_met = field_value < value
            elif operator == "lte":
                condition_met = field_value <= value
            
            if not condition_met:
                return 0.0
            
            # If condition met, calculate adjustment
            calc_type = calculations["type"]
            calc_value = calculations["value"]
            
            if calc_type == "percent_discount":
                return calc_value / 100.0  # Return as decimal percent
            elif calc_type == "fixed":
                return calc_value
            
            return 0.0
        
        # Calculate pricing for customer1
        cs1_view = cs_view_results[0]
        base_price = cs1_view.custom_price  # Use customer-specific price as base
        
        # Apply rules
        volume_discount = evaluate_rule(self.volume_rule, customer1_data)
        loyalty_discount = evaluate_rule(self.loyalty_rule, customer1_data)
        
        # Calculate total discount percentage (multiplicative)
        total_discount_multiplier = (1 - volume_discount) * (1 - loyalty_discount)
        final_price_customer1 = base_price * total_discount_multiplier
        
        # Expected price for customer1
        # 80.00 * (1 - 0.15) * (1 - 0.10) = 80.00 * 0.85 * 0.90 = 61.20
        expected_price_customer1 = Decimal('61.20')
        
        self.assertAlmostEqual(final_price_customer1, float(expected_price_customer1), places=2)
        
        # Calculate pricing for customer2
        cs2_view = cs_view_results[1]
        base_price = cs2_view.custom_price  # Use customer-specific price as base
        
        # Apply rules (neither should apply for customer2)
        volume_discount = evaluate_rule(self.volume_rule, customer2_data)
        loyalty_discount = evaluate_rule(self.loyalty_rule, customer2_data)
        
        total_discount_multiplier = (1 - volume_discount) * (1 - loyalty_discount)
        final_price_customer2 = base_price * total_discount_multiplier
        
        # Expected price for customer2 (no discounts apply)
        # 120.00 * (1 - 0) * (1 - 0) = 120.00
        expected_price_customer2 = Decimal('120.00')
        
        self.assertAlmostEqual(final_price_customer2, float(expected_price_customer2), places=2)
        
    def test_combined_rule_evaluation(self):
        """Test that complex combined rules are evaluated correctly"""
        # Create a complex rule with nested conditions
        complex_rule_json = {
            "condition": {
                "operator": "and",
                "conditions": [
                    {
                        "operator": "or",
                        "conditions": [
                            {
                                "field": "company_size",
                                "operator": "gt",
                                "value": 50
                            },
                            {
                                "field": "customer_age",
                                "operator": "gte",
                                "value": 5
                            }
                        ]
                    },
                    {
                        "field": "service_id",
                        "operator": "eq",
                        "value": self.service1.id
                    }
                ]
            },
            "calculation": {
                "type": "percent_discount",
                "value": 20.0
            }
        }
        
        self.complex_rule = AdvancedRule.objects.create(
            rule_group=self.rule_group,
            name="Complex Discount",
            description="Discount for large or loyal customers using premium service",
            conditions=json.dumps(complex_rule_json["condition"]),
            calculations=json.dumps(complex_rule_json["calculation"])
        )
        
        # Test data scenarios
        scenarios = [
            # Large company, loyal, premium service (matches)
            {
                "data": {
                    "company_size": 100,
                    "customer_age": 5,
                    "service_id": self.service1.id
                },
                "expected_match": True
            },
            # Small company, loyal, premium service (matches)
            {
                "data": {
                    "company_size": 10,
                    "customer_age": 5,
                    "service_id": self.service1.id
                },
                "expected_match": True
            },
            # Large company, new, premium service (matches)
            {
                "data": {
                    "company_size": 100,
                    "customer_age": 1,
                    "service_id": self.service1.id
                },
                "expected_match": True
            },
            # Small company, new, premium service (doesn't match)
            {
                "data": {
                    "company_size": 10,
                    "customer_age": 1,
                    "service_id": self.service1.id
                },
                "expected_match": False
            },
            # Large company, loyal, different service (doesn't match)
            {
                "data": {
                    "company_size": 100,
                    "customer_age": 5,
                    "service_id": self.service2.id
                },
                "expected_match": False
            }
        ]
        
        # Helper function to evaluate complex rule conditions
        def evaluate_complex_condition(condition, data):
            if "operator" in condition and condition["operator"] in ["and", "or"]:
                # Complex condition
                results = [evaluate_complex_condition(sub_cond, data) for sub_cond in condition["conditions"]]
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
                else:
                    return False
        
        # Test all scenarios
        for i, scenario in enumerate(scenarios):
            conditions = json.loads(self.complex_rule.conditions)
            result = evaluate_complex_condition(conditions, scenario["data"])
            
            self.assertEqual(
                result, 
                scenario["expected_match"], 
                f"Scenario {i+1} failed: expected {scenario['expected_match']} but got {result}"
            )