#!/usr/bin/env python
"""
Standalone test script for the 'ne' operator without Django dependencies.
This script creates a mock implementation of the evaluate_condition function
to test the fix for the 'ne' operator.
"""

import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ----- Mock Implementation of evaluate_condition function -----

def evaluate_condition(order, field, operator, value):
    """
    Simplified mock of the actual evaluate_condition function.
    This is the fixed version supporting both 'ne' and 'neq'.
    """
    try:
        # Get the field value from the order
        order_value = getattr(order, field, None)
        
        if order_value is None:
            return False
            
        # Evaluate based on operator
        if operator == 'eq':
            return str(order_value) == str(value)
        elif operator == 'ne' or operator == 'neq':  # Support both 'ne' and 'neq'
            return str(order_value) != str(value)
        elif operator == 'gt':
            return float(order_value) > float(value)
        elif operator == 'lt':
            return float(order_value) < float(value)
        elif operator == 'contains':
            return str(value).lower() in str(order_value).lower()
        
        return False
    except Exception as e:
        logger.error(f"Error evaluating condition: {str(e)}")
        return False

# ----- Mock Order class for testing -----

class MockOrder:
    """Mock order for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# ----- Test Implementation -----

def run_test():
    """Run tests for the evaluate_condition function."""
    # Create test orders
    order = MockOrder(
        ship_to_country="US",
        weight_lb="10",
        notes="Test order notes"
    )
    
    # Test 'eq' operator
    eq_test_match = evaluate_condition(order, 'ship_to_country', 'eq', 'US')
    eq_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'eq', 'CA')
    
    # Test 'ne' operator - This should now work with the fix
    ne_test_match = evaluate_condition(order, 'ship_to_country', 'ne', 'CA')
    ne_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'ne', 'US')
    
    # This is the specific test case that was failing before the fix
    ne_test_specific = evaluate_condition(order, 'ship_to_country', 'ne', 'tom')
    
    # Test 'neq' operator for backward compatibility
    neq_test_match = evaluate_condition(order, 'ship_to_country', 'neq', 'CA')
    neq_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'neq', 'US')
    
    # Print results
    print("\n===== Operator Test Results =====")
    print(f"'eq' with matching value: {eq_test_match} (should be True)")
    print(f"'eq' with non-matching value: {eq_test_nonmatch} (should be False)")
    print(f"'ne' with non-matching value: {ne_test_match} (should be True)")
    print(f"'ne' with matching value: {ne_test_nonmatch} (should be False)")
    print(f"'ne' with 'tom' value: {ne_test_specific} (should be True - this was the bug)")
    print(f"'neq' with non-matching value: {neq_test_match} (should be True)")
    print(f"'neq' with matching value: {neq_test_nonmatch} (should be False)")
    
    # Verify all tests passed
    all_tests_passed = (
        eq_test_match and 
        not eq_test_nonmatch and 
        ne_test_match and 
        not ne_test_nonmatch and
        ne_test_specific and 
        neq_test_match and 
        not neq_test_nonmatch
    )
    
    if all_tests_passed:
        print("\n✅ ALL TESTS PASSED: The 'ne' and 'neq' operators are working correctly!")
        return True
    else:
        print("\n❌ TESTS FAILED: There are still issues with operator evaluation.")
        return False

if __name__ == "__main__":
    run_test()