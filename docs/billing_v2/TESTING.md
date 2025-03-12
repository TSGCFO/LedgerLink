# Billing V2 Testing Guide

This document provides guidance on testing the Billing V2 application, including different approaches for testing the codebase effectively.

## Overview

The Billing_V2 application has comprehensive tests for:
- Models (BillingReport, OrderCost, ServiceCost)
- Utilities (sku_utils, rule_evaluator, calculator)
- API views and endpoints

## Testing Approaches

### 1. Standalone Unit Tests

The most reliable approach for basic testing is to create standalone test scripts that don't require database connections. These tests use mocking to isolate components and test them independently.

Example standalone test files:
- `test_standalone_utils.py`: Tests for SKU utility functions
- `test_standalone_rule_evaluator.py`: Tests for rule evaluation logic
- `test_standalone_calculator.py`: Tests for billing calculation

To run these tests:

```bash
python test_standalone_utils.py
python test_standalone_rule_evaluator.py
python test_standalone_calculator.py
```

### 2. Django Test Framework

For more comprehensive testing that involves models and database interactions, Django's test framework can be used:

```bash
python manage.py test Billing_V2
```

This requires a properly configured database connection.

### 3. TestContainers

For testing with a real PostgreSQL database in an isolated environment, TestContainers can be used:

```bash
export TC_CLOUD_TOKEN=your_testcontainers_token
USE_TESTCONTAINERS=True python -m pytest Billing_V2/
```

This approach requires setting up TestContainers Cloud agent and proper environment variables.

### 4. Docker Testing

For a completely isolated testing environment:

```bash
./run_docker_tests.sh Billing_V2
```

This requires Docker to be properly installed and configured.

## Test Structure

### 1. Model Tests (`test_models.py`)

Tests the database models and their relationships:
- Creating model instances
- Model methods (`add_order_cost`, `add_service_cost`, etc.)
- Serialization methods (`to_dict`, `to_json`)

### 2. Utility Tests (`test_utils.py`)

Tests utility functions that handle business logic:
- SKU normalization and validation
- Rule evaluation for various field types and operators
- Billing calculations for different service types

### 3. View Tests (`test_views.py`)

Tests API endpoints and view functionality:
- Listing and filtering reports
- Generating new reports
- Downloading reports in different formats
- Customer summary endpoint

## Mocking Patterns

Many components have external dependencies that need to be mocked for effective testing:

```python
# Mock the order and rule for rule evaluation
order = MagicMock()
rule = MagicMock()

# Set specific attributes
order.weight_lb = 100
rule.field = 'weight_lb'
rule.values = [50]
rule.operator = 'gt'

# Test evaluation
result = RuleEvaluator.evaluate_rule(rule, order)
self.assertTrue(result)
```

## Handling Database Connections

When testing with database connections:

1. **Test Database Configuration**: Ensure `settings.py` has proper test database settings
2. **Fixtures**: Use fixtures to set up test data
3. **Transactions**: Make use of Django's transaction management to isolate tests

## Code Coverage

To measure test coverage:

```bash
coverage run --source='Billing_V2' manage.py test Billing_V2
coverage report
coverage html  # Creates HTML report in htmlcov/
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues during testing:

1. Check database configuration in `settings.py`
2. Use standalone tests with mocks for components that don't need database access
3. Use `sqlite3` for testing to avoid PostgreSQL connection issues:

```python
# In settings.py or a test settings file
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
```

### Mock Configuration Issues

If tests fail due to mock configuration:

1. Check that mocked objects have all required attributes and methods
2. Ensure mocked objects return appropriate values
3. Verify patch paths are correct (should point to where the object is *used*, not where it's defined)

## Best Practices

1. **Isolate Tests**: Each test should be independent of others
2. **Mock External Dependencies**: Don't rely on external systems or databases when possible
3. **Test Edge Cases**: Include tests for boundary conditions and error cases
4. **Keep Tests Fast**: Avoid unnecessary database operations or complex setups
5. **Use Appropriate Assertions**: Choose the right assertion method for each test case
6. **Document Test Requirements**: Include setup instructions and requirements

## Example: Testing SKU Utils

```python
def test_normalize_sku():
    """Test normalize_sku function"""
    # Standard cases
    assert normalize_sku("ABC-123") == "ABC123"
    assert normalize_sku("abc 123") == "ABC123"
    
    # Edge cases
    assert normalize_sku(None) == ""
    assert normalize_sku("") == ""
    assert normalize_sku(123) == "123"
    
    print("All normalize_sku tests passed!")
```

## Example: Testing Rule Evaluator

```python
def test_evaluate_rule_with_numeric_field():
    """Test evaluating a rule with a numeric field"""
    # Create mocks
    order = MagicMock()
    rule = MagicMock()
    
    # Configure mocks
    order.weight_lb = 100
    rule.field = 'weight_lb'
    rule.values = [50]
    rule.operator = 'gt'
    
    # Test evaluation
    assert RuleEvaluator.evaluate_rule(rule, order) == True
    
    # Test different operator
    rule.operator = 'lt'
    assert RuleEvaluator.evaluate_rule(rule, order) == False
```

## Example: Testing Calculator

```python
def test_calculate_service_cost_single():
    """Test calculating cost for a single service"""
    # Create mocks
    service = MagicMock()
    service.charge_type = 'single'
    service.name = 'Test Service'
    
    customer_service = MagicMock()
    customer_service.service = service
    customer_service.unit_price = Decimal('100.00')
    
    order = MagicMock()
    
    # Create calculator and test
    calculator = BillingCalculator(
        customer_id=1,
        start_date="2023-01-01",
        end_date="2023-01-31"
    )
    
    # Calculate cost
    cost = calculator.calculate_service_cost(customer_service, order)
    
    # Verify result
    assert cost == Decimal('100.00')
```