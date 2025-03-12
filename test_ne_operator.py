#!/usr/bin/env python
"""
Simple test script to verify the fix for the 'ne' operator bug.
This script runs outside of Django's test framework to avoid database issues.
"""

# Import the function we fixed
from rules.views import evaluate_condition

class MockOrder:
    """Mock order for testing condition evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def run_test():
    """Run tests for the evaluate_condition function."""
    # Create a mock order with US as the country
    order = MockOrder(ship_to_country="US")
    
    # Test the 'eq' operator with both matching and non-matching values
    eq_test_match = evaluate_condition(order, 'ship_to_country', 'eq', 'US')
    eq_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'eq', 'tom')
    
    # Test the 'ne' operator with both matching and non-matching values
    ne_test_match = evaluate_condition(order, 'ship_to_country', 'ne', 'tom')
    ne_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'ne', 'US')
    
    # Test the 'neq' operator alias with both matching and non-matching values
    neq_test_match = evaluate_condition(order, 'ship_to_country', 'neq', 'tom')
    neq_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'neq', 'US')
    
    # Test the 'ncontains' operator with both matching and non-matching values
    ncontains_test_match = evaluate_condition(order, 'ship_to_country', 'ncontains', 'tom') 
    ncontains_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'ncontains', 'US')
    
    # Print results
    print("\n===== Operator Test Results =====")
    print(f"'eq' with matching value: {eq_test_match} (should be True)")
    print(f"'eq' with non-matching value: {eq_test_nonmatch} (should be False)")
    print(f"'ne' with matching value: {ne_test_match} (should be True)")
    print(f"'ne' with non-matching value: {ne_test_nonmatch} (should be False)")
    print(f"'neq' with matching value: {neq_test_match} (should be True)")
    print(f"'neq' with non-matching value: {neq_test_nonmatch} (should be False)")
    print(f"'ncontains' with matching value: {ncontains_test_match} (should be True)") 
    print(f"'ncontains' with non-matching value: {ncontains_test_nonmatch} (should be False)")
    
    # Check if fix is working properly
    ne_fix_working = (ne_test_match and not ne_test_nonmatch and 
                      neq_test_match and not neq_test_nonmatch)
    ncontains_fix_working = (ncontains_test_match and not ncontains_test_nonmatch)
    
    if ne_fix_working and ncontains_fix_working:
        print("\n✅ TEST PASSED: The 'ne' and 'ncontains' operator fixes are working correctly!")
    elif ne_fix_working:
        print("\n❌ TEST FAILED: The 'ne' operator is fixed but 'ncontains' is still not working correctly.")
    elif ncontains_fix_working:
        print("\n❌ TEST FAILED: The 'ncontains' operator is fixed but 'ne' is still not working correctly.")
    else:
        print("\n❌ TEST FAILED: Both 'ne' and 'ncontains' operators are not working correctly.")

if __name__ == "__main__":
    run_test()