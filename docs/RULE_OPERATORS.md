# Rule Operators Documentation

## Overview

This document describes the operators available in the LedgerLink Rules System, with special attention to the "not equals" (`ne`) operator that was fixed in the March 2025.

## Available Operators

The Rule System supports the following operators for condition evaluation:

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `ship_to_country eq US` |
| `ne` | Not Equals | `ship_to_country ne CA` |
| `gt` | Greater Than | `weight_lb gt 10` |
| `lt` | Less Than | `weight_lb lt 10` |
| `ge` | Greater Than or Equal | `weight_lb ge 10` |
| `le` | Less Than or Equal | `weight_lb le 10` |
| `contains` | Contains Substring | `notes contains urgent` |
| `not_contains` | Does Not Contain | `notes not_contains cancel` |
| `between` | Value is in Range | `weight_lb between 5,15` |

## Critical Bug Fix: "Not Equals" Operator

### Issue Description

A critical bug was identified in March 2025 where the "not equals" operator (`ne`) was incorrectly evaluated in the `evaluate_condition` function. The function was looking for the operator `neq` instead of `ne`, causing all "not equals" conditions to fail even when they should have succeeded.

### Impact

This bug affected:
- Rule evaluation
- Billing calculations
- Business logic decisions
- Rule testing results

### Root Cause

The bug was in the `evaluate_condition` function in `/LedgerLink/rules/views.py`:

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

### Fix Applied

The bug was fixed by updating the `evaluate_condition` function to accept both `ne` and `neq` for backward compatibility:

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

### Testing

A comprehensive testing plan was created in `TODO.md` including:
- Unit tests for the `evaluate_condition` function
- Integration tests for rule evaluation
- Manual testing via the Rule Tester UI

## Best Practices for Rule Creation

1. **Use the correct operator codes**
   - Always use the standard operator codes listed in the table above
   - For "not equals" conditions, use the `ne` operator

2. **Test rules thoroughly**
   - Use the Rule Tester UI to verify rule behavior
   - Test both positive and negative cases
   - Verify complex conditions with multiple operators

3. **Review billing calculations**
   - Periodically review billing rules, especially those using the `ne` operator
   - Verify calculations against expected outcomes

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

If rules with the "not equals" operator are not evaluating as expected:

1. Verify that you're using the `ne` operator code, not `neq`
2. Check the rule evaluation in the Rule Tester UI
3. Verify that the fix has been applied to your deployment
4. For legacy systems, consider updating any hard-coded `neq` references

## References

- [Rule System Documentation](/cline_docs/rules_system.md)
- [TODO: Testing the `ne` Operator Fix](/TODO.md)