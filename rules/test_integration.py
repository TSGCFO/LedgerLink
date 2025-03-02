"""
Integration tests for the rules API.
Tests the ne operator fix in combination with Django models and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
import json

from rules.models import Rule, RuleGroup, AdvancedRule
from customer_services.models import CustomerService, Service
from customers.models import Customer
from orders.models import Order

class RuleApiIntegrationTest(TestCase):
    """Integration tests for rule evaluation API."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Legal Name",
            email="test@example.com",
        )
        
        # Create a test service
        self.service = Service.objects.create(
            service_name="Test Service",
            description="Test service description",
            charge_type="per_order"
        )
        
        # Create a customer service association
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('10.00')
        )
        
        # Create a rule group
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        # Create a client for API testing
        self.client = Client()
    
    def test_ne_operator_in_rule_tester(self):
        """Test that the 'ne' operator works correctly in the rule tester."""
        # URL for the rule tester API endpoint
        url = reverse('test_rule')
        
        # Create test rule data with 'ne' operator
        rule_data = {
            "field": "ship_to_country",
            "operator": "ne",
            "value": "CA", 
            "conditions": {},
            "calculations": []
        }
        
        # Create sample order data with US as the country
        order_data = {
            "weight_lb": "10",
            "total_item_qty": "5",
            "packages": "1",
            "line_items": "2",
            "volume_cuft": "2.5",
            "reference_number": "ORD-12345",
            "ship_to_name": "John Doe",
            "ship_to_company": "ACME Corp",
            "ship_to_city": "New York",
            "ship_to_state": "NY",
            "ship_to_country": "US",
            "carrier": "UPS",
            "sku_quantity": '{"SKU-123": 2, "SKU-456": 3}',
            "notes": "Test order notes"
        }
        
        # Create the request data
        request_data = {
            "rule": rule_data,
            "order": order_data
        }
        
        # Make the API request
        response = self.client.post(
            url, 
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the response data
        response_data = json.loads(response.content)
        
        # Check that the rule matches (US is not equal to CA)
        self.assertTrue(response_data['matches'])
        self.assertIsNone(response_data['reason'])
        
        # Now change the rule to test a non-matching case
        rule_data["value"] = "US"
        request_data = {
            "rule": rule_data,
            "order": order_data
        }
        
        # Make the API request again
        response = self.client.post(
            url, 
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        # Check that the rule doesn't match (US is equal to US)
        self.assertFalse(response_data['matches'])
        self.assertIsNotNone(response_data['reason'])
        
    def test_neq_operator_backward_compatibility(self):
        """Test that the 'neq' operator still works for backward compatibility."""
        # URL for the rule tester API endpoint
        url = reverse('test_rule')
        
        # Create test rule data with 'neq' operator
        rule_data = {
            "field": "ship_to_country",
            "operator": "neq",
            "value": "CA", 
            "conditions": {},
            "calculations": []
        }
        
        # Create sample order data with US as the country
        order_data = {
            "ship_to_country": "US"
        }
        
        # Create the request data
        request_data = {
            "rule": rule_data,
            "order": order_data
        }
        
        # Make the API request
        response = self.client.post(
            url, 
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the response data
        response_data = json.loads(response.content)
        
        # Check that the rule matches (US is not equal to CA)
        self.assertTrue(response_data['matches'])
        
        # Now change the rule to test a non-matching case
        rule_data["value"] = "US"
        request_data = {
            "rule": rule_data,
            "order": order_data
        }
        
        # Make the API request again
        response = self.client.post(
            url, 
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        # Check that the rule doesn't match (US is equal to US)
        self.assertFalse(response_data['matches'])
    
    def test_create_and_evaluate_ne_rule(self):
        """Test creating a rule with 'ne' operator and evaluating it."""
        # Create a rule with 'ne' operator
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field="ship_to_country",
            operator="ne",
            value="CA",
            adjustment_amount=Decimal('5.00')
        )
        
        # Create a mock order
        order = type('Order', (), {
            'transaction_id': 'ORD-12345',
            'ship_to_country': 'US'
        })
        
        # Evaluate the rule
        from rules.models import RuleEvaluator
        evaluator = RuleEvaluator()
        result = evaluator.evaluate_rule(rule, order)
        
        # US is not equal to CA, so the rule should match
        self.assertTrue(result)
        
        # Change the rule value to match
        rule.value = "US"
        rule.save()
        
        # Evaluate again
        result = evaluator.evaluate_rule(rule, order)
        
        # US is equal to US, so the rule should not match with 'ne'
        self.assertFalse(result)