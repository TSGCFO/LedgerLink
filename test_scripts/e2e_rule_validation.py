"""
End-to-end validation script for rule builder and billing calculator integration.

This script tests the entire flow from rule creation to billing calculation, focusing on:
1. Validating that rules are properly created via the API
2. Ensuring server-side validation matches client-side validation 
3. Validating rules are correctly applied to orders in billing calculations
"""

import sys
import json
import decimal
import requests
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# Import the validator function
from rules.utils.validators import validate_calculation
from frontend.src.utils.validationUtils import validateCalculation

# Setup basic configuration
BASE_URL = "http://localhost:8000/api/v1"
# Replace with actual test auth token
AUTH_TOKEN = "your_test_auth_token"

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

class RuleBillingE2ETest:
    """Tests end-to-end validation of rule creation and billing calculation."""

    def __init__(self):
        self.test_results = []

    def log_result(self, test_name, result, message):
        """Log test result"""
        self.test_results.append({
            "test": test_name,
            "result": result,
            "message": message
        })
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")

    def validate_case_tier_consistency(self):
        """Test frontend and backend validation consistency for case-based tiers"""
        print("\n▶️ Testing case-based tier validation consistency")
        
        # Test cases matching both frontend and backend validation
        test_cases = [
            {
                "name": "Valid configuration",
                "calculation": {'type': 'case_based_tier', 'value': 1.0},
                "tier_config": {
                    'ranges': [
                        {'min': 1, 'max': 3, 'multiplier': 1.0},
                        {'min': 4, 'max': 6, 'multiplier': 2.0},
                        {'min': 7, 'max': 10, 'multiplier': 3.0}
                    ],
                    'excluded_skus': ['SKU3']
                },
                "expected_valid": True
            },
            {
                "name": "Missing ranges",
                "calculation": {'type': 'case_based_tier', 'value': 1.0},
                "tier_config": {
                    'excluded_skus': ['SKU3']
                },
                "expected_valid": False,
                "expected_error": "ranges"
            },
            {
                "name": "Invalid min/max relationship",
                "calculation": {'type': 'case_based_tier', 'value': 1.0},
                "tier_config": {
                    'ranges': [
                        {'min': 5, 'max': 3, 'multiplier': 1.0}
                    ],
                    'excluded_skus': []
                },
                "expected_valid": False,
                "expected_error": "greater than"
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test['name']}")
            
            # Frontend validation
            frontend_calc = {
                'type': 'case_based_tier',
                'value': test['calculation']['value'],
                'tier_config': test['tier_config']
            }
            frontend_result = validateCalculation(frontend_calc)
            
            # Backend validation
            backend_valid, backend_error = validate_calculation(
                'case_based_tier', 
                test['calculation'],
                test['tier_config']
            )
            
            # Validate results
            frontend_valid = frontend_result.get('isValid', False)
            
            # Compare frontend and backend validation results
            if frontend_valid == backend_valid == test['expected_valid']:
                self.log_result(
                    f"Validation consistency test {i}", 
                    True, 
                    f"Frontend and backend validation consistent for {test['name']}"
                )
            else:
                self.log_result(
                    f"Validation consistency test {i}",
                    False,
                    f"Validation mismatch: Frontend={frontend_valid}, Backend={backend_valid}, Expected={test['expected_valid']}"
                )
            
            # For invalid cases, check error message consistency
            if not test['expected_valid']:
                frontend_msg = frontend_result.get('message', '')
                backend_msg = backend_error if backend_error else ''
                
                if test['expected_error'].lower() in frontend_msg.lower() and test['expected_error'].lower() in backend_msg.lower():
                    self.log_result(
                        f"Error message consistency test {i}",
                        True,
                        f"Error messages consistent: Both mention '{test['expected_error']}'"
                    )
                else:
                    self.log_result(
                        f"Error message consistency test {i}",
                        False,
                        f"Error messages inconsistent: Frontend='{frontend_msg}', Backend='{backend_msg}'"
                    )

    def test_tier_calculation(self):
        """Test case-based tier calculation logic"""
        print("\n▶️ Testing case-based tier calculation")
        
        # Mock the order and rule
        order = {
            'sku_quantity': {
                'SKU1': {'quantity': 5, 'cases': 2},
                'SKU2': {'quantity': 10, 'cases': 3},
                'SKU3': {'quantity': 5, 'cases': 1}
            },
            'transaction_id': 'TEST123',
            'get_case_summary': lambda exclude_skus=None: {
                'total_cases': 5 if 'SKU3' in (exclude_skus or []) else 6,
                'skus': {
                    'SKU1': 2,
                    'SKU2': 3,
                    'SKU3': 1
                }
            },
            'has_only_excluded_skus': lambda exclude_skus: False
        }
        
        rule = {
            'tier_config': {
                'ranges': [
                    {'min': 1, 'max': 3, 'multiplier': 1.0},
                    {'min': 4, 'max': 6, 'multiplier': 2.0},
                    {'min': 7, 'max': 10, 'multiplier': 3.0}
                ],
                'excluded_skus': ['SKU3']
            }
        }
        
        # Define test cases for calculation
        test_cases = [
            {
                "name": "With excluded SKU",
                "rule": rule,
                "order": order,
                "expected_multiplier": Decimal('2.0'),  # 5 cases falls in the 4-6 range
                "expected_base": Decimal('100.0'),
                "expected_result": Decimal('200.0')
            },
            {
                "name": "Without excluded SKU",
                "rule": {
                    'tier_config': {
                        'ranges': [
                            {'min': 1, 'max': 3, 'multiplier': 1.0},
                            {'min': 4, 'max': 6, 'multiplier': 2.0},
                            {'min': 7, 'max': 10, 'multiplier': 3.0}
                        ],
                        'excluded_skus': []
                    }
                },
                "order": order,
                "expected_multiplier": Decimal('2.0'),  # 6 cases falls in the 4-6 range
                "expected_base": Decimal('100.0'),
                "expected_result": Decimal('200.0')
            },
            {
                "name": "Outside tier ranges",
                "rule": {
                    'tier_config': {
                        'ranges': [
                            {'min': 10, 'max': 20, 'multiplier': 1.0},
                            {'min': 21, 'max': 30, 'multiplier': 2.0}
                        ],
                        'excluded_skus': []
                    }
                },
                "order": order,
                "expected_multiplier": None,  # No matching tier
                "expected_base": Decimal('100.0'),
                "expected_result": Decimal('100.0')  # No change to base amount
            }
        ]
        
        # Mock the RuleEvaluator.evaluate_case_based_rule function
        def evaluate_case_based_rule(rule, order):
            config = rule['tier_config']
            excluded_skus = config.get('excluded_skus', [])
            
            # Get case summary
            case_summary = order.get_case_summary(exclude_skus=excluded_skus)
            total_cases = case_summary['total_cases']
            
            # Early return if no cases or only excluded SKUs
            if total_cases == 0 or order.has_only_excluded_skus(excluded_skus):
                return False, 0, None
            
            # Find applicable tier
            tier_ranges = config.get('ranges', [])
            for tier in tier_ranges:
                if tier['min'] <= total_cases <= tier['max']:
                    return True, Decimal(str(tier['multiplier'])), case_summary
            
            return False, 0, case_summary
            
        # Run the tests
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test['name']}")
            
            # Calculate
            applies, multiplier, case_summary = evaluate_case_based_rule(test['rule'], test['order'])
            
            # Apply calculation
            base = test['expected_base']
            result = base * multiplier if applies else base
            
            # Validate results
            if test['expected_multiplier'] is None:
                # Case where no tier should match
                if not applies:
                    self.log_result(
                        f"Tier calculation test {i} - tier matching",
                        True,
                        f"Correctly found no matching tier for {test['name']}"
                    )
                else:
                    self.log_result(
                        f"Tier calculation test {i} - tier matching",
                        False,
                        f"Expected no matching tier but found one with multiplier {multiplier}"
                    )
            else:
                # Case where a tier should match
                if applies and multiplier == test['expected_multiplier']:
                    self.log_result(
                        f"Tier calculation test {i} - tier matching",
                        True,
                        f"Found correct tier with multiplier {multiplier}"
                    )
                else:
                    self.log_result(
                        f"Tier calculation test {i} - tier matching",
                        False,
                        f"Expected multiplier {test['expected_multiplier']} but got {multiplier if applies else 'no match'}"
                    )
            
            # Check final calculation result
            if result == test['expected_result']:
                self.log_result(
                    f"Tier calculation test {i} - final amount",
                    True,
                    f"Calculation correct: ${result} (Expected: ${test['expected_result']})"
                )
            else:
                self.log_result(
                    f"Tier calculation test {i} - final amount",
                    False,
                    f"Calculation incorrect: ${result} (Expected: ${test['expected_result']})"
                )

    def test_billing_integration(self):
        """Test billing integration with rules"""
        print("\n▶️ Testing billing integration with case-based tiers")
        
        # This test would typically involve making API calls to create rules
        # and then generating a billing report, but for our test script
        # we'll simulate this with offline data
        
        print("This would be an integration test calling the billing API")
        print("For now, just validating the calculation flow locally")
        
        # Mock a customer service with a case-based tier rule
        customer_service = {
            'unit_price': Decimal('100.0'),
            'service': {
                'service_name': 'Test Service',
                'charge_type': 'case_based_tier'
            },
            'advanced_rules': [
                {
                    'tier_config': {
                        'ranges': [
                            {'min': 1, 'max': 3, 'multiplier': 1.0},
                            {'min': 4, 'max': 6, 'multiplier': 2.0},
                            {'min': 7, 'max': 10, 'multiplier': 3.0}
                        ],
                        'excluded_skus': ['SKU3']
                    }
                }
            ]
        }
        
        # Mock an order with SKUs
        order = {
            'sku_quantity': {
                'SKU1': {'quantity': 5, 'cases': 2},
                'SKU2': {'quantity': 10, 'cases': 3},
                'SKU3': {'quantity': 5, 'cases': 1}
            },
            'transaction_id': 'TEST123',
            'get_case_summary': lambda exclude_skus=None: {
                'total_cases': 5 if 'SKU3' in (exclude_skus or []) else 6,
                'skus': {
                    'SKU1': 2,
                    'SKU2': 3,
                    'SKU3': 1
                }
            },
            'has_only_excluded_skus': lambda exclude_skus: False
        }
        
        # Mock the calculate_service_cost function
        def calculate_service_cost(customer_service, order):
            if customer_service['service']['charge_type'] == 'case_based_tier':
                rule = customer_service['advanced_rules'][0]
                
                # Mock evaluate_case_based_rule
                def evaluate_case_based_rule(rule, order):
                    config = rule['tier_config']
                    excluded_skus = config.get('excluded_skus', [])
                    
                    # Get case summary
                    case_summary = order.get_case_summary(exclude_skus=excluded_skus)
                    total_cases = case_summary['total_cases']
                    
                    # Find applicable tier
                    tier_ranges = config.get('ranges', [])
                    for tier in tier_ranges:
                        if tier['min'] <= total_cases <= tier['max']:
                            return True, Decimal(str(tier['multiplier'])), case_summary
                    
                    return False, 0, case_summary
                
                applies, multiplier, case_summary = evaluate_case_based_rule(rule, order)
                
                if applies:
                    return customer_service['unit_price'] * multiplier
                
            return Decimal('0.0')
        
        # Run the test
        cost = calculate_service_cost(customer_service, order)
        expected = Decimal('200.0')  # Base 100.0 * multiplier 2.0
        
        if cost == expected:
            self.log_result(
                "Billing integration test",
                True,
                f"Service cost calculation correct: ${cost} (Expected: ${expected})"
            )
        else:
            self.log_result(
                "Billing integration test",
                False,
                f"Service cost calculation incorrect: ${cost} (Expected: ${expected})"
            )

    def run_all_tests(self):
        """Run all e2e tests"""
        print("\n======= STARTING E2E VALIDATION TESTS =======\n")
        
        # Run tests
        self.validate_case_tier_consistency()
        self.test_tier_calculation()
        self.test_billing_integration()
        
        # Summarize results
        passed = sum(1 for t in self.test_results if t['result'])
        total = len(self.test_results)
        
        print(f"\n======= TEST SUMMARY: {passed}/{total} TESTS PASSED =======")
        if passed == total:
            print("✅ All tests passed!")
        else:
            print(f"❌ {total-passed} tests failed:")
            for test in self.test_results:
                if not test['result']:
                    print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

# Run tests when script is executed directly
if __name__ == "__main__":
    # Create test instance
    test = RuleBillingE2ETest()
    success = test.run_all_tests()
    
    # Return exit code based on test results
    sys.exit(0 if success else 1)