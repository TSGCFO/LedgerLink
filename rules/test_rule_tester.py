from django.test import TestCase, RequestFactory
from django.http import JsonResponse
import json

from rules.views import test_rule, evaluate_condition

class RuleTesterTests(TestCase):
    """Test suite for the rule tester endpoint."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_rule_tester_ne_operator(self):
        """Test the rule tester with a 'ne' operator rule - the specific failing case."""
        
        # Create the test rule data
        rule_data = {
            "field": "ship_to_country",
            "operator": "ne",
            "value": "tom",
            "conditions": {},
            "calculations": [],
            "tier_config": {
                "ranges": [],
                "excluded_skus": []
            }
        }
        
        # Create sample order data
        sample_data = {
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
        
        # Verify that the direct condition evaluates correctly
        # Create a mock order object
        class MockOrder:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        mock_order = MockOrder(**sample_data)
        self.assertTrue(evaluate_condition(
            mock_order, 
            rule_data["field"], 
            rule_data["operator"], 
            rule_data["value"]
        ))
        
        # Now test the full test_rule view function
        request_data = {
            "rule": rule_data,
            "order": sample_data
        }
        
        # Create a request with the test data
        request = self.factory.post(
            '/api/v1/rules/test-rule/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Call the view function
        response = test_rule(request)
        
        # Convert the response to JSON
        response_data = json.loads(response.content)
        
        # Verify the response
        self.assertTrue(response_data['matches'], 
                      "The rule with 'ne' operator should match when the field value is different")
        self.assertIsNone(response_data['reason'],
                      "There should be no failure reason when the rule matches")

    def test_rule_tester_eq_operator(self):
        """Test the rule tester with an 'eq' operator rule."""
        
        # Create the test rule data - should match
        rule_data = {
            "field": "ship_to_country",
            "operator": "eq",
            "value": "US",
            "conditions": {},
            "calculations": [],
            "tier_config": {
                "ranges": [],
                "excluded_skus": []
            }
        }
        
        # Create sample order data
        sample_data = {
            "ship_to_country": "US",
            "weight_lb": "10"
        }
        
        # Create the request data
        request_data = {
            "rule": rule_data,
            "order": sample_data
        }
        
        # Create a request with the test data
        request = self.factory.post(
            '/api/v1/rules/test-rule/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Call the view function
        response = test_rule(request)
        
        # Convert the response to JSON
        response_data = json.loads(response.content)
        
        # Verify the response
        self.assertTrue(response_data['matches'], 
                      "The rule with 'eq' operator should match when values are equal")
        
        # Create the test rule data - should NOT match
        rule_data = {
            "field": "ship_to_country",
            "operator": "eq",
            "value": "CA",
            "conditions": {},
            "calculations": []
        }
        
        # Create the request data
        request_data = {
            "rule": rule_data,
            "order": sample_data
        }
        
        # Create a request with the test data
        request = self.factory.post(
            '/api/v1/rules/test-rule/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Call the view function
        response = test_rule(request)
        
        # Convert the response to JSON
        response_data = json.loads(response.content)
        
        # Verify the response
        self.assertFalse(response_data['matches'], 
                       "The rule with 'eq' operator should not match when values are different")
        self.assertIsNotNone(response_data['reason'],
                           "There should be a failure reason when the rule doesn't match")
                           
    def test_rule_tester_ncontains_operator(self):
        """Test the rule tester with an 'ncontains' operator rule."""
        
        # Create the test rule data - should match since "US" does not contain "tom"
        rule_data = {
            "field": "ship_to_country",
            "operator": "ncontains",
            "value": "tom",
            "conditions": {},
            "calculations": [],
            "tier_config": {
                "ranges": [],
                "excluded_skus": []
            }
        }
        
        # Create sample order data
        sample_data = {
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
            "order": sample_data
        }
        
        # Create a request with the test data
        request = self.factory.post(
            '/api/v1/rules/test-rule/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Call the view function
        response = test_rule(request)
        
        # Convert the response to JSON
        response_data = json.loads(response.content)
        
        # Verify the response - this should now pass with our fix
        self.assertTrue(response_data['matches'], 
                      "The rule with 'ncontains' operator should match when the field value doesn't contain the test value")
        self.assertIsNone(response_data['reason'],
                        "There should be no failure reason when the rule matches")
        
        # Test the negative case - should NOT match since "US" contains "US"
        rule_data = {
            "field": "ship_to_country",
            "operator": "ncontains",
            "value": "US",
            "conditions": {},
            "calculations": []
        }
        
        # Create the request data
        request_data = {
            "rule": rule_data,
            "order": sample_data
        }
        
        # Create a request with the test data
        request = self.factory.post(
            '/api/v1/rules/test-rule/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Call the view function
        response = test_rule(request)
        
        # Convert the response to JSON
        response_data = json.loads(response.content)
        
        # Verify the response
        self.assertFalse(response_data['matches'], 
                       "The rule with 'ncontains' operator should not match when the field value contains the test value")
        self.assertIsNotNone(response_data['reason'],
                           "There should be a failure reason when the rule doesn't match")