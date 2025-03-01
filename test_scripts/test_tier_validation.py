"""
Test script for case-based tier validation without requiring Django test framework.
This tests the validators.py logic directly without database dependencies.
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# Import the validator function
from rules.utils.validators import validate_calculation

def run_tests():
    """Run validation tests for case-based tiers"""
    print("Running Case-Based Tier Validation Tests")
    print("-" * 50)
    
    # Test cases that mirror the Django and React test cases
    test_cases = [
        {
            "name": "Valid configuration",
            "calculation": {'value': 1.0},
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
            "calculation": {'value': 1.0},
            "tier_config": {
                'excluded_skus': ['SKU3']
            },
            "expected_valid": False,
            "expected_error": "ranges"
        },
        {
            "name": "Invalid min/max relationship",
            "calculation": {'value': 1.0},
            "tier_config": {
                'ranges': [
                    {'min': 5, 'max': 3, 'multiplier': 1.0}
                ],
                'excluded_skus': []
            },
            "expected_valid": False,
            "expected_error": "Min value (5.0) cannot be greater than max value (3.0)"
        },
        {
            "name": "Missing required fields",
            "calculation": {'value': 1.0},
            "tier_config": {
                'ranges': [
                    {'min': 1, 'multiplier': 1.0}  # missing max
                ]
            },
            "expected_valid": False,
            "expected_error": "must have min, max, and multiplier"
        },
        {
            "name": "Negative values",
            "calculation": {'value': 1.0},
            "tier_config": {
                'ranges': [
                    {'min': -1, 'max': 3, 'multiplier': 1.0}
                ],
                'excluded_skus': []
            },
            "expected_valid": False,
            "expected_error": "must be non-negative"
        },
        {
            "name": "Invalid excluded_skus format",
            "calculation": {'value': 1.0},
            "tier_config": {
                'ranges': [
                    {'min': 1, 'max': 3, 'multiplier': 1.0}
                ],
                'excluded_skus': "SKU1,SKU2"  # should be list
            },
            "expected_valid": False,
            "expected_error": "excluded_skus must be a list"
        }
    ]
    
    # Run all the test cases
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        is_valid, error = validate_calculation('case_based_tier', test['calculation'], test['tier_config'])
        
        if is_valid == test['expected_valid']:
            print(f"✅ Validation result: {is_valid} (Expected: {test['expected_valid']})")
        else:
            print(f"❌ Validation result: {is_valid} (Expected: {test['expected_valid']})")
        
        if not test['expected_valid']:
            if error is None:
                print(f"❌ Expected error but got None")
            elif test['expected_error'].lower() in error.lower():
                print(f"✅ Error contains expected text: '{test['expected_error']}'")
                print(f"   Full error: {error}")
            else:
                print(f"❌ Error doesn't contain expected text: '{test['expected_error']}'")
                print(f"   Full error: {error}")
    
    print("\n" + "-" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    run_tests()