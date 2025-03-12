# Customer Services Testing Guide

## Overview

This document outlines the testing approach for the CustomerServices app, including test types, patterns, and examples.

## Test Types

We implement four main types of tests for the CustomerServices app:

1. **Unit Tests**: Test individual components in isolation 
2. **Integration Tests**: Test interactions between components
3. **Contract Tests**: Ensure API compatibility with frontend using Pact
4. **Performance Tests**: Verify system performance under load

## Database Testing Challenges

The CustomerServices app has specific testing challenges due to:

1. **Materialized View Dependencies**: Uses CustomerServiceView materialized view
2. **Complex Schema Requirements**: Multiple required fields and relationships 
3. **Database Connectivity Issues**: Problems with pytest-django and connections

## Factory Testing Pattern

We use a custom factory pattern to create test data reliably:

```python
# Create factories
customer_factory = CustomerFactory(conn)
service_factory = ServiceFactory(conn)
cs_factory = CustomerServiceFactory(conn)

# Create test data with relationships
customer = customer_factory.create(
    company_name="Test Company", 
    email="test@example.com"
)
service = service_factory.create(
    name="Test Service", 
    price=Decimal('100.00')
)

# Create with relationships
cs = cs_factory.create(
    customer=customer,
    service=service,
    unit_price=Decimal('99.99')
)
```

This pattern:
- Creates database schema when needed
- Handles required fields automatically
- Supports relationships between models
- Properly isolates tests with clean setup/teardown

## Test Implementation Files

### Unit Tests

- `test_models.py`: Tests for Customer Service model behavior
  - Data validation
  - Foreign key constraints
  - Unique constraints
  - Instance methods

- `test_serializers.py`: Tests for serialization/deserialization
  - Field validation
  - Data transformation
  - Read/write permissions

### Integration Tests

- `test_integration.py`: Tests for component interactions
  - Integration with billing system
  - Integration with rules engine
  - API workflow tests

### Contract Tests

- `test_pact_provider.py`: Tests API compatibility with frontend
  - Verifies contract with frontend
  - Tests API responses match expectations
  - Ensures breaking changes are detected

### Performance Tests

- `test_performance.py`: Tests system performance
  - Load tests for API endpoints
  - Database query performance
  - Optimizations for high volume operations

## Running Tests

Run specific test types:

```bash
# Run all customer_services tests
./run_customer_services_tests.sh

# Run only model tests using our reliable factory approach
./run_factory_test.sh

# Run contract tests
./run_customer_services_contract_tests.sh
```

## Best Practices

1. **Implement unit tests first** to ensure model behavior is correct
2. **Add integration tests** to verify interactions with other components
3. **Create contract tests** to ensure API compatibility with frontend
4. **Finish with performance tests** to optimize under load

## Debugging Test Issues

If you encounter database connection issues:

1. Use the factory pattern approach (`run_factory_test.sh`)
2. Set `SKIP_MATERIALIZED_VIEWS=True` to bypass view creation issues
3. Run in Docker for a reliable PostgreSQL environment

## Test Coverage Goals

We aim for the following coverage targets:
- Unit Tests: 90%+ coverage of models and serializers
- Integration Tests: 80%+ coverage of component interactions
- Contract Tests: 100% coverage of public API endpoints
- Performance Tests: Cover all critical database operations