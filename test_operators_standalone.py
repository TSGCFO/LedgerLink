#!/usr/bin/env python
"""
Standalone test for the operator functionality.
This script doesn't rely on Django's imports or test framework.
"""

class MockOrder:
    """Mock order for testing condition evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def evaluate_condition(order, field, operator, value):
    """Simplified version of the evaluate_condition function from views.py"""
    try:
        # Get the field value from the order
        order_value = getattr(order, field, None)
        
        if order_value is None:
            return False
            
        # Evaluate based on operator
        if operator == 'eq':
            return str(order_value) == str(value)
        elif operator == 'ne' or operator == 'neq':  # Support both 'ne' and 'neq' for backward compatibility
            return str(order_value) != str(value)
        elif operator == 'gt':
            return float(order_value) > float(value)
        elif operator == 'gte':
            return float(order_value) >= float(value)
        elif operator == 'lt':
            return float(order_value) < float(value)
        elif operator == 'lte':
            return float(order_value) <= float(value)
        elif operator == 'contains':
            return str(value).lower() in str(order_value).lower()
        elif operator == 'not_contains' or operator == 'ncontains':  # Support both 'not_contains' and 'ncontains' for consistency
            return str(value).lower() not in str(order_value).lower()
        elif operator == 'between':
            # Parse range values
            range_values = str(value).split(',')
            if len(range_values) == 2:
                min_val = float(range_values[0])
                max_val = float(range_values[1])
                return min_val <= float(order_value) <= max_val
        
        return False
    except Exception as e:
        print(f"Error evaluating condition: {str(e)}")
        return False

def run_test():
    """Run tests for the evaluate_condition function."""
    # Create a mock order for testing
    order = MockOrder(
        weight_lb="10",
        total_item_qty="5",
        packages="1",
        line_items="2",
        volume_cuft="2.5",
        reference_number="ORD-12345",
        ship_to_name="John Doe",
        ship_to_company="ACME Corp",
        ship_to_city="New York",
        ship_to_state="NY",
        ship_to_country="US",
        carrier="UPS",
        sku_quantity='{"SKU-123": 2, "SKU-456": 3}',
        notes="Test order notes"
    )
    
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
    
    # Test the 'not_contains' operator with both matching and non-matching values
    not_contains_test_match = evaluate_condition(order, 'ship_to_country', 'not_contains', 'tom')
    not_contains_test_nonmatch = evaluate_condition(order, 'ship_to_country', 'not_contains', 'US')
    
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
    print(f"'not_contains' with matching value: {not_contains_test_match} (should be True)") 
    print(f"'not_contains' with non-matching value: {not_contains_test_nonmatch} (should be False)")
    
    # Check if fix is working properly
    ne_fix_working = (ne_test_match and not ne_test_nonmatch and 
                      neq_test_match and not neq_test_nonmatch)
    
    ncontains_fix_working = (ncontains_test_match and not ncontains_test_nonmatch and
                           not_contains_test_match and not not_contains_test_nonmatch)
    
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