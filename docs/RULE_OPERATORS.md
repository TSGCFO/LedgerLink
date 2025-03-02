# Rule Operators Documentation

## Overview

This document describes the operators available in the LedgerLink Rules System, with special attention to the "not equals" (`ne`) and "not contains" (`ncontains`) operators that were fixed in March 2025.

## Available Operators

The Rule System supports the following operators for condition evaluation:

| Operator | Description | Example | Notes |
|----------|-------------|---------|-------|
| `eq` | Equals | `ship_to_country eq US` | |
| `ne` | Not Equals | `ship_to_country ne CA` | Fixed March 2025 |
| `neq` | Not Equals | `ship_to_country neq CA` | Alias for `ne` |
| `gt` | Greater Than | `weight_lb gt 10` | |
| `lt` | Less Than | `weight_lb lt 10` | |
| `ge` | Greater Than or Equal | `weight_lb ge 10` | |
| `le` | Less Than or Equal | `weight_lb le 10` | |
| `contains` | Contains Substring | `notes contains urgent` | |
| `ncontains` | Does Not Contain | `notes ncontains cancel` | Fixed March 2025 |
| `not_contains` | Does Not Contain | `notes not_contains cancel` | Alias for `ncontains` |
| `between` | Value is in Range | `weight_lb between 5,15` | |

## Critical Bug Fixes

### Issue 1: "Not Equals" Operator

#### Issue Description

A critical bug was identified in March 2025 where the "not equals" operator (`ne`) was incorrectly evaluated in the `evaluate_condition` function. The function was looking for the operator `neq` instead of `ne`, causing all "not equals" conditions to fail even when they should have succeeded.

#### Impact

This bug affected:
- Rule evaluation
- Billing calculations
- Business logic decisions
- Rule testing results

### Issue 2: "Not Contains" Operator

#### Issue Description

A similar bug was discovered with the "not contains" operator (`ncontains`). The evaluation function was looking for `not_contains` instead of `ncontains`, causing all "not contains" conditions to fail.

#### Impact

This bug affected:
- String field comparisons (e.g., checking if a field does not contain certain text)
- JSON field evaluations (e.g., checking if SKU data doesn't include certain items)
- Rule testing results for conditions using `ncontains`

### Root Causes

Both bugs had similar root causes in the `evaluate_condition` function in `/LedgerLink/rules/views.py`:

#### "Not Equals" Bug

```python
# Before fix (incorrect)
def evaluate_condition(order, field, operator, value):
    # ...
    if operator == 'eq':
        return str(order_value) == str(value)
    elif operator == 'neq':  # ← BUG: using 'neq' instead of 'ne'
        return str(order_value) != str(value)
    # ...
```

The models and frontend were using `ne` as the operator code for "not equals", but the evaluation function was looking for `neq`, causing a mismatch.

#### "Not Contains" Bug

```python
# Before fix (incorrect)
def evaluate_condition(order, field, operator, value):
    # ...
    elif operator == 'contains':
        return str(value).lower() in str(order_value).lower()
    elif operator == 'not_contains':  # ← BUG: using 'not_contains' instead of 'ncontains'
        return str(value).lower() not in str(order_value).lower()
    # ...
```

Similarly, the frontend was using `ncontains` but the evaluation function was only checking for `not_contains`.

### Fixes Applied

#### "Not Equals" Fix

```python
# After fix (correct)
def evaluate_condition(order, field, operator, value):
    # ...
    if operator == 'eq':
        return str(order_value) == str(value)
    elif operator == 'ne' or operator == 'neq':  # ← FIXED: supporting both 'ne' and 'neq'
        return str(order_value) != str(value)
    # ...
```

#### "Not Contains" Fix

```python
# After fix (correct)
def evaluate_condition(order, field, operator, value):
    # ...
    elif operator == 'contains':
        return str(value).lower() in str(order_value).lower()
    elif operator == 'not_contains' or operator == 'ncontains':  # ← FIXED: supporting both variants
        return str(value).lower() not in str(order_value).lower()
    # ...
```

### Testing

Comprehensive testing was implemented to verify both fixes:

- **Unit tests** in `rules/test_condition_evaluator.py`:
  - Testing all operators including `ne`, `neq`, `ncontains`, and `not_contains`
  - Testing positive and negative cases for each operator
  - Testing with various data types (strings, numbers, JSON)

- **Rule tester tests** in `rules/test_rule_tester.py`:
  - API-level tests to verify rule evaluation through the API
  - Testing the specific examples that were failing
  - Verifying proper responses from the rule tester

- **Standalone tests**:
  - `test_operators_standalone.py` for direct testing without Django dependencies
  - Isolated verification of the fixed operators

- **Manual testing** via the Rule Tester UI:
  - Verifying the UI correctly processes rules with fixed operators
  - Testing different field types with each operator

## Best Practices for Rule Creation

1. **Use the standard operator codes**
   - Always use the standard operator codes listed in the table above
   - For "not equals" conditions, prefer `ne` over `neq`
   - For "not contains" conditions, prefer `ncontains` over `not_contains`

2. **Test rules thoroughly**
   - Use the Rule Tester UI to verify rule behavior
   - Test both positive and negative cases
   - Verify complex conditions with multiple operators
   - Double-check rules using negative operators (`ne`, `ncontains`)

3. **Review billing calculations**
   - Periodically review billing rules, especially those using negative operators
   - Verify calculations against expected outcomes
   - Test rules with edge cases

## Implementation Details

The rule evaluation is implemented in several key components:

1. **`evaluate_condition` Function**
   - Located in `rules/views.py`
   - Evaluates a single condition against order data
   - Handles all operator types and data conversions

2. **Rule Models**
   - `Rule` - Base rule class with field, operator, value
   - `AdvancedRule` - Extends Rule with additional conditions and calculations

3. **Rule Evaluator**
   - Handles complete rule evaluation including logic operators
   - Processes rule groups with AND, OR, NOT logic

## Troubleshooting

If rules with negative operators are not evaluating as expected:

1. **For "not equals" issues**:
   - Verify that you're using the `ne` operator code
   - Check the rule evaluation in the Rule Tester UI
   - Verify that the fix has been applied to your deployment
   - For legacy systems, consider updating any hard-coded `neq` references

2. **For "not contains" issues**:
   - Verify that you're using the `ncontains` operator code
   - Test with the Rule Tester UI to verify behavior
   - For legacy systems, consider updating any hard-coded `not_contains` references

3. **For both operators**:
   - Check if the value being compared is properly formatted
   - Verify case sensitivity is not causing issues (all string comparisons are case-insensitive)
   - Test with different sample data to isolate the issue

## Common Mistakes

1. **Operator choice**:
   - Using `ne` for string values that should use `ncontains` instead
   - Using `ncontains` for exact matching when `ne` would be more appropriate

2. **Value formatting**:
   - Forgetting quotes around string values
   - Using spaces in `between` range values (should be comma-separated without spaces)
   - Not escaping special characters in string values

3. **Data types**:
   - Using string operators on numeric fields
   - Using numeric operators on string fields
   - Not handling null or empty values correctly

## References

- [Rule System Documentation](/cline_docs/rules_system.md)
- [Testing Documentation](/docs/TESTING_GUIDE.md)