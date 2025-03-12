# LedgerLink Integration Tests

This directory contains integration tests for the LedgerLink application. These tests verify that different modules and components work together correctly.

## Test Organization

- **conftest.py** - Contains pytest fixtures and mock objects used across integration tests
- **test_order_service_integration.py** - Tests Order and Service module interactions
- **test_billing_rules_integration.py** - Tests Billing and Rules system integration
- **test_customer_service_rule_integration.py** - Tests Customer Service and Rules integration
- **test_performance.py** - Tests system performance with realistic data volumes
- **pact-contract-setup.py** - Defines API contracts for consumer-driven contract tests
- **pact-provider-verify.py** - Verifies backend implementation against API contracts

## Test Setup

Integration tests require PostgreSQL for full compatibility with LedgerLink's features (materialized views, JSON operations, etc.).

### Database Setup

```bash
# Create test database
createdb ledgerlink_test

# Run migrations on test database
DATABASE_URL=postgres://username:password@localhost/ledgerlink_test python manage.py migrate

# Run tests with specific database
DATABASE_URL=postgres://username:password@localhost/ledgerlink_test python -m pytest tests/integration/
```

### Running Tests

```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific integration test
python -m pytest tests/integration/test_billing_rules_integration.py

# Run with verbose output
python -m pytest tests/integration/ -v

# Run tests and print coverage
python -m pytest tests/integration/ --cov=.

# Skip slow tests (e.g., performance tests)
python -m pytest tests/integration/ -k "not slow"
```

## Understanding the Tests

### Order-Service Integration

Tests in `test_order_service_integration.py` verify that:
- Orders correctly use customer-specific service pricing
- SKU quantities are calculated properly
- Service charges apply according to configured rules
- Custom pricing overrides base pricing

### Billing-Rules Integration

Tests in `test_billing_rules_integration.py` verify that:
- Billing calculations correctly apply rule conditions
- Tiered pricing is calculated correctly
- Complex rule conditions are evaluated properly
- Billing reports aggregate results correctly

### Customer Service-Rule Integration

Tests in `test_customer_service_rule_integration.py` verify that:
- Customer service pricing works with rule conditions
- Multiple rule discounts combine correctly
- Complex nested conditions are evaluated correctly
- Different customer profiles receive appropriate pricing

### Performance Testing

Tests in `test_performance.py` verify that:
- Key API endpoints respond within acceptable time limits
- Database queries are optimized (limited number of queries)
- Performance scales reasonably with data volume
- Complex rule evaluations complete within acceptable time

### Contract Testing

Contract tests ensure that the API contracts between frontend and backend are maintained:

1. **Create Contract**: Use `pact-contract-setup.py` to define consumer contracts
2. **Verify Provider**: Use `pact-provider-verify.py` to verify backend implementation

## Test Utilities

### Mock Objects

`conftest.py` provides mock objects for testing database views and external services:

- `MockOrderSKUView` - Simulates the `OrderSKUView` database view
- `MockCustomerServiceView` - Simulates the `CustomerServiceView` database view

Example usage:
```python
from tests.integration.conftest import MockOrderSKUView

# Create mock view result
view_result = MockOrderSKUView(
    id=1,
    status='pending',
    order_date=timezone.now(),
    priority='normal',
    customer_id=1,
    sku_id='SKU001',
    quantity=10
)
```

### Testing JSON Fields

Many models in LedgerLink use JSON fields. Test them like this:

```python
# Create order with JSON data
order = Order.objects.create(
    customer=customer,
    status='pending',
    sku_quantities=json.dumps({'SKU001': 5, 'SKU002': 10})
)

# Verify JSON field data
sku_quantities = json.loads(order.sku_quantities)
self.assertEqual(sku_quantities['SKU001'], 5)
self.assertEqual(sku_quantities['SKU002'], 10)
```

## Best Practices

1. **Use PostgreSQL**: Always run integration tests with PostgreSQL to test real database features
2. **Mock Carefully**: Use the provided mock objects for views but avoid excessive mocking
3. **Clean Up Test Data**: Use test transactions when possible, clean up in tearDown() when needed
4. **Test Realistic Scenarios**: Create tests that mirror real business operations
5. **Test Edge Cases**: Include tests for boundary conditions and error scenarios
6. **Keep Tests Fast**: Optimize test performance to maintain quick feedback loops
7. **Document Test Intent**: Clearly explain what each test is verifying

## Troubleshooting

### Common Issues

1. **Missing Database Views**:
   - Check that `conftest.py` is creating necessary views
   - Verify migration state with `python manage.py showmigrations`

2. **JSON Field Errors**:
   - Remember to use `json.dumps()` when storing, `json.loads()` when reading
   - PostgreSQL may show errors if the JSON is invalid

3. **Slow Tests**:
   - Profile tests with `pytest --duration=10` to identify slow tests
   - Use `@pytest.mark.slow` for tests that are inherently slow

4. **Database Transactions**:
   - If tests interfere with each other, they may be modifying shared state
   - Use TestCase (transaction per test) or clean up carefully in tearDown()

### Debugging Tips

1. **Print Query Count**:
   ```python
   from django.db import connection
   print(len(connection.queries))
   ```

2. **Print Actual Queries**:
   ```python
   for query in connection.queries:
       print(query['sql'])
   ```

3. **Track Test Duration**:
   ```bash
   python -m pytest tests/integration/ --duration=10
   ```

## Need Help?

If you're having trouble with the integration tests:

1. Check the documentation in `tests/integration/README.md`
2. Review the test and expected behavior to understand test intent
3. Examine test fixtures and setup in `conftest.py`
4. Check model definitions in the relevant app `models.py` files