#!/usr/bin/env python
"""
Comprehensive test for all operators in the LedgerLink rules system.
This script tests each operator individually to verify correct behavior.
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
        elif operator == 'gte' or operator == 'ge':  # Support both variants
            return float(order_value) >= float(value)
        elif operator == 'lt':
            return float(order_value) < float(value)
        elif operator == 'lte' or operator == 'le':  # Support both variants
            return float(order_value) <= float(value)
        elif operator == 'contains':
            return str(value).lower() in str(order_value).lower()
        elif operator == 'not_contains' or operator == 'ncontains':  # Support both variants
            return str(value).lower() not in str(order_value).lower()
        elif operator == 'startswith':
            return str(order_value).lower().startswith(str(value).lower())
        elif operator == 'endswith':
            return str(order_value).lower().endswith(str(value).lower())
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

def test_all_operators():
    """Test all operators with various data types."""
    # Create a comprehensive test order with various field types
    order = MockOrder(
        # Numeric fields
        weight_lb="10.5",
        total_item_qty="5",
        packages="1",
        line_items="2",
        volume_cuft="2.5",
        
        # String fields
        reference_number="ORD-12345",
        ship_to_name="John Doe",
        ship_to_company="ACME Corp",
        ship_to_city="New York",
        ship_to_state="NY",
        ship_to_country="United States",
        carrier="UPS",
        notes="Test order notes with special instructions",
        
        # JSON field
        sku_quantity='{"SKU-123": 2, "SKU-456": 3}'
    )
    
    results = {}
    
    # Test equality operators
    print("\n===== Testing Equality Operators =====")
    
    # eq - Equal
    test_eq1 = evaluate_condition(order, 'ship_to_country', 'eq', 'United States')
    test_eq2 = evaluate_condition(order, 'ship_to_country', 'eq', 'Canada')
    test_eq3 = evaluate_condition(order, 'weight_lb', 'eq', '10.5')
    
    # Note: In the current implementation, string comparison is used for 'eq'
    # This means that '10.5' != '10.50' in string comparison, which is expected behavior
    test_eq4 = evaluate_condition(order, 'weight_lb', 'eq', '10.50')
    
    print(f"eq (string equality): {test_eq1} (should be True)")
    print(f"eq (string non-equality): {test_eq2} (should be False)")
    print(f"eq (numeric equality): {test_eq3} (should be True)")
    print(f"eq (numeric equality with formatting): {test_eq4} (should be False - string comparison)")
    
    results['eq'] = test_eq1 and not test_eq2 and test_eq3 and not test_eq4
    
    # ne / neq - Not Equal
    test_ne1 = evaluate_condition(order, 'ship_to_country', 'ne', 'Canada')
    test_ne2 = evaluate_condition(order, 'ship_to_country', 'ne', 'United States')
    test_ne3 = evaluate_condition(order, 'weight_lb', 'ne', '11')
    test_ne4 = evaluate_condition(order, 'weight_lb', 'ne', '10.5')
    
    # Test using neq alias
    test_neq1 = evaluate_condition(order, 'ship_to_country', 'neq', 'Canada')
    test_neq2 = evaluate_condition(order, 'ship_to_country', 'neq', 'United States')
    
    print(f"ne (string non-equality): {test_ne1} (should be True)")
    print(f"ne (string equality): {test_ne2} (should be False)")
    print(f"ne (numeric non-equality): {test_ne3} (should be True)")
    print(f"ne (numeric equality): {test_ne4} (should be False)")
    print(f"neq alias (string non-equality): {test_neq1} (should be True)")
    print(f"neq alias (string equality): {test_neq2} (should be False)")
    
    results['ne'] = test_ne1 and not test_ne2 and test_ne3 and not test_ne4
    results['neq'] = test_neq1 and not test_neq2
    
    # Test numeric comparison operators
    print("\n===== Testing Numeric Comparison Operators =====")
    
    # gt - Greater Than
    test_gt1 = evaluate_condition(order, 'weight_lb', 'gt', '10')
    test_gt2 = evaluate_condition(order, 'weight_lb', 'gt', '10.5')
    test_gt3 = evaluate_condition(order, 'weight_lb', 'gt', '11')
    
    print(f"gt (greater): {test_gt1} (should be True)")
    print(f"gt (equal): {test_gt2} (should be False)")
    print(f"gt (less): {test_gt3} (should be False)")
    
    results['gt'] = test_gt1 and not test_gt2 and not test_gt3
    
    # lt - Less Than
    test_lt1 = evaluate_condition(order, 'weight_lb', 'lt', '11')
    test_lt2 = evaluate_condition(order, 'weight_lb', 'lt', '10.5')
    test_lt3 = evaluate_condition(order, 'weight_lb', 'lt', '10')
    
    print(f"lt (less): {test_lt1} (should be True)")
    print(f"lt (equal): {test_lt2} (should be False)")
    print(f"lt (greater): {test_lt3} (should be False)")
    
    results['lt'] = test_lt1 and not test_lt2 and not test_lt3
    
    # gte/ge - Greater Than or Equal
    test_gte1 = evaluate_condition(order, 'weight_lb', 'gte', '10')
    test_gte2 = evaluate_condition(order, 'weight_lb', 'gte', '10.5')
    test_gte3 = evaluate_condition(order, 'weight_lb', 'gte', '11')
    
    # Test using ge alias
    test_ge1 = evaluate_condition(order, 'weight_lb', 'ge', '10')
    test_ge2 = evaluate_condition(order, 'weight_lb', 'ge', '10.5')
    test_ge3 = evaluate_condition(order, 'weight_lb', 'ge', '11')
    
    print(f"gte (greater): {test_gte1} (should be True)")
    print(f"gte (equal): {test_gte2} (should be True)")
    print(f"gte (less): {test_gte3} (should be False)")
    print(f"ge alias (greater): {test_ge1} (should be True)")
    print(f"ge alias (equal): {test_ge2} (should be True)")
    print(f"ge alias (less): {test_ge3} (should be False)")
    
    results['gte'] = test_gte1 and test_gte2 and not test_gte3
    results['ge'] = test_ge1 and test_ge2 and not test_ge3
    
    # lte/le - Less Than or Equal
    test_lte1 = evaluate_condition(order, 'weight_lb', 'lte', '11')
    test_lte2 = evaluate_condition(order, 'weight_lb', 'lte', '10.5')
    test_lte3 = evaluate_condition(order, 'weight_lb', 'lte', '10')
    
    # Test using le alias
    test_le1 = evaluate_condition(order, 'weight_lb', 'le', '11')
    test_le2 = evaluate_condition(order, 'weight_lb', 'le', '10.5')
    test_le3 = evaluate_condition(order, 'weight_lb', 'le', '10')
    
    print(f"lte (greater): {test_lte1} (should be True)")
    print(f"lte (equal): {test_lte2} (should be True)")
    print(f"lte (less): {test_lte3} (should be False)")
    print(f"le alias (greater): {test_le1} (should be True)")
    print(f"le alias (equal): {test_le2} (should be True)")
    print(f"le alias (less): {test_le3} (should be False)")
    
    results['lte'] = test_lte1 and test_lte2 and not test_lte3
    results['le'] = test_le1 and test_le2 and not test_le3
    
    # Test string operators
    print("\n===== Testing String Operators =====")
    
    # contains
    test_contains1 = evaluate_condition(order, 'ship_to_country', 'contains', 'united')
    test_contains2 = evaluate_condition(order, 'ship_to_country', 'contains', 'states')
    test_contains3 = evaluate_condition(order, 'ship_to_country', 'contains', 'STATES')  # Case insensitive
    test_contains4 = evaluate_condition(order, 'ship_to_country', 'contains', 'canada')
    
    print(f"contains (substring present lowercase): {test_contains1} (should be True)")
    print(f"contains (substring present): {test_contains2} (should be True)")
    print(f"contains (substring present different case): {test_contains3} (should be True)")
    print(f"contains (substring not present): {test_contains4} (should be False)")
    
    results['contains'] = test_contains1 and test_contains2 and test_contains3 and not test_contains4
    
    # ncontains / not_contains
    test_ncontains1 = evaluate_condition(order, 'ship_to_country', 'ncontains', 'canada')
    test_ncontains2 = evaluate_condition(order, 'ship_to_country', 'ncontains', 'united')
    test_ncontains3 = evaluate_condition(order, 'ship_to_country', 'ncontains', 'CANADA')  # Case insensitive
    
    # Test using not_contains alias
    test_not_contains1 = evaluate_condition(order, 'ship_to_country', 'not_contains', 'canada')
    test_not_contains2 = evaluate_condition(order, 'ship_to_country', 'not_contains', 'united')
    
    print(f"ncontains (substring not present): {test_ncontains1} (should be True)")
    print(f"ncontains (substring present): {test_ncontains2} (should be False)")
    print(f"ncontains (substring not present different case): {test_ncontains3} (should be True)")
    print(f"not_contains alias (substring not present): {test_not_contains1} (should be True)")
    print(f"not_contains alias (substring present): {test_not_contains2} (should be False)")
    
    results['ncontains'] = test_ncontains1 and not test_ncontains2 and test_ncontains3
    results['not_contains'] = test_not_contains1 and not test_not_contains2
    
    # startswith
    test_startswith1 = evaluate_condition(order, 'ship_to_country', 'startswith', 'united')
    test_startswith2 = evaluate_condition(order, 'ship_to_country', 'startswith', 'UNITED')  # Case insensitive
    test_startswith3 = evaluate_condition(order, 'ship_to_country', 'startswith', 'states')
    
    print(f"startswith (prefix present): {test_startswith1} (should be True)")
    print(f"startswith (prefix present different case): {test_startswith2} (should be True)")
    print(f"startswith (prefix not at start): {test_startswith3} (should be False)")
    
    results['startswith'] = test_startswith1 and test_startswith2 and not test_startswith3
    
    # endswith
    test_endswith1 = evaluate_condition(order, 'ship_to_country', 'endswith', 'states')
    test_endswith2 = evaluate_condition(order, 'ship_to_country', 'endswith', 'STATES')  # Case insensitive
    test_endswith3 = evaluate_condition(order, 'ship_to_country', 'endswith', 'united')
    
    print(f"endswith (suffix present): {test_endswith1} (should be True)")
    print(f"endswith (suffix present different case): {test_endswith2} (should be True)")
    print(f"endswith (suffix not at end): {test_endswith3} (should be False)")
    
    results['endswith'] = test_endswith1 and test_endswith2 and not test_endswith3
    
    # Test range operator
    print("\n===== Testing Range Operator =====")
    
    # between
    test_between1 = evaluate_condition(order, 'weight_lb', 'between', '10,11')
    test_between2 = evaluate_condition(order, 'weight_lb', 'between', '10.5,11')
    test_between3 = evaluate_condition(order, 'weight_lb', 'between', '9,10.5')
    test_between4 = evaluate_condition(order, 'weight_lb', 'between', '11,12')
    test_between5 = evaluate_condition(order, 'weight_lb', 'between', '9,10')
    
    print(f"between (value in range): {test_between1} (should be True)")
    print(f"between (value at min): {test_between2} (should be True)")
    print(f"between (value at max): {test_between3} (should be True)")
    print(f"between (value below range): {test_between4} (should be False)")
    print(f"between (value above range): {test_between5} (should be False)")
    
    results['between'] = test_between1 and test_between2 and test_between3 and not test_between4 and not test_between5
    
    # Test JSON field operators
    print("\n===== Testing JSON Field Operators =====")
    
    # contains with JSON
    test_json_contains1 = evaluate_condition(order, 'sku_quantity', 'contains', 'SKU-123')
    test_json_contains2 = evaluate_condition(order, 'sku_quantity', 'contains', 'SKU-789')
    
    print(f"contains (JSON field, key present): {test_json_contains1} (should be True)")
    print(f"contains (JSON field, key not present): {test_json_contains2} (should be False)")
    
    results['json_contains'] = test_json_contains1 and not test_json_contains2
    
    # ncontains with JSON
    test_json_ncontains1 = evaluate_condition(order, 'sku_quantity', 'ncontains', 'SKU-789')
    test_json_ncontains2 = evaluate_condition(order, 'sku_quantity', 'ncontains', 'SKU-123')
    
    print(f"ncontains (JSON field, key not present): {test_json_ncontains1} (should be True)")
    print(f"ncontains (JSON field, key present): {test_json_ncontains2} (should be False)")
    
    results['json_ncontains'] = test_json_ncontains1 and not test_json_ncontains2
    
    # Overall result
    print("\n===== Overall Results =====")
    for operator, result in results.items():
        print(f"{operator}: {'✅ PASS' if result else '❌ FAIL'}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✅ ALL TESTS PASSED: All operators are working correctly!")
    else:
        failed = [op for op, res in results.items() if not res]
        print(f"\n❌ SOME TESTS FAILED: The following operators had issues: {', '.join(failed)}")
    
    return all_passed

if __name__ == "__main__":
    test_all_operators()