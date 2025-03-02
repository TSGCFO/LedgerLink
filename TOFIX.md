# TODO

**Based on the analysis, here are the key findings:**

FILENAME: frontend/src/utils/apiClient.js
ISSUE: URL mismatch between frontend calls and backend endpoints
FIX: Standardize on `/api/v1/<resource>/` pattern across frontend and backend
SEVERITY: Medium

FILENAME: rules/models.py
ISSUE: N+1 query in RuleEvaluator.evaluate_rule_group method
FIX: Use select_related() and prefetch_related() to optimize queries
SEVERITY: Medium

FILENAME: frontend/src/components/rules/constants.js:67
ISSUE: Missing `sku_name` and `case_based_tier` options that exist in backend models
FIX: Sync frontend constants with backend model choices
SEVERITY: Medium

FILENAME: billing/billing_calculator.py
ISSUE: Nested loops with database queries causing performance issues
FIX: Refactor to use Django aggregation and prefetch related data
SEVERITY: High

FILENAME: frontend/src/components/orders/OrderList.jsx
ISSUE: Loading all data without pagination causes performance issues
FIX: Implement proper pagination with backend support
SEVERITY: Medium

FILENAME: import_orders.py:77-120
ISSUE: Missing input validation in JSON parsing could lead to code injection
FIX: Add proper validation and sanitization of imported data
SEVERITY: High

FILENAME: frontend/src/components/orders/OrderForm.jsx
ISSUE: Doesn't validate transaction_id uniqueness that's required by backend model
FIX: Add frontend validation matching backend constraints
SEVERITY: Medium

FILENAME: middleware.py
ISSUE: Incomplete sensitive data masking in logging middleware
FIX: Implement recursive masking for nested structures
SEVERITY: High
