# Full System Testing Guide for LedgerLink

This guide outlines the comprehensive approach to full system testing for the LedgerLink application, including integration testing, performance testing, and contract testing.

## Table of Contents

1. [Integration Testing](#integration-testing)
2. [Contract Testing with Pact](#contract-testing-with-pact)
3. [Performance Testing](#performance-testing)
4. [Setting Up Test Environment](#setting-up-test-environment)
5. [Continuous Integration](#continuous-integration)

## Integration Testing

Integration tests verify that different parts of the application work together correctly. We focus on key integration points:

### Order-Service Integration

Tests in `tests/integration/test_order_service_integration.py` verify that:
- Orders correctly use customer-specific service pricing
- SKU quantities are calculated properly
- Service charges apply according to configured rules
- Custom pricing overrides base pricing

### Billing-Rules Integration

Tests in `tests/integration/test_billing_rules_integration.py` verify that:
- Billing calculations correctly apply rule conditions
- Tiered pricing is calculated correctly
- Complex rule conditions are evaluated properly
- Billing reports aggregate results correctly

### Customer Service-Rule Integration

Tests in `tests/integration/test_customer_service_rule_integration.py` verify that:
- Customer service pricing works with rule conditions
- Multiple rule discounts combine correctly
- Complex nested conditions are evaluated correctly
- Different customer profiles receive appropriate pricing

### Running Integration Tests

```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific integration test
python -m pytest tests/integration/test_billing_rules_integration.py

# Run with verbose output
python -m pytest tests/integration/ -v
```

## Contract Testing with Pact

Contract tests ensure that the API contracts between frontend and backend are maintained.

### Setting Up Pact

1. **Create Contract**: Use `tests/integration/pact-contract-setup.py` to define consumer contracts
2. **Verify Provider**: Use `tests/integration/pact-provider-verify.py` to verify backend implementation
3. **Integrate with CI**: Set up contract verification in your CI pipeline

### Contract Test Structure

- Order API endpoints: GET, POST, PUT operations
- Rules API endpoints: Complex rule structures and nested conditions
- Billing API endpoints: Calculation requests and report generations

### Running Pact Tests

```bash
# Generate Pact contract files
python tests/integration/pact-contract-setup.py

# Verify backend against contracts
python tests/integration/pact-provider-verify.py
```

## Performance Testing

Performance tests ensure the application can handle expected load and identify bottlenecks.

### Key Performance Metrics

- **Query Count**: Number of database queries per request
- **Response Time**: Time to process and respond to requests
- **Scaling Performance**: How response time scales with data size

### Performance Test Categories

1. **API Endpoint Performance**: Tests in `tests/integration/test_performance.py`
   - Order list endpoint query count and response time
   - Rules endpoint performance with complex conditions
   - Billing calculation performance with many line items

2. **Scaling Tests**: Verify performance with increasing data volumes
   - Response time scaling with larger page sizes
   - Rule evaluation performance with complex conditions
   - Optimization of database queries

### Running Performance Tests

```bash
# Run all performance tests
python -m pytest tests/integration/test_performance.py

# Skip slow tests
python -m pytest tests/integration/test_performance.py -k "not slow"

# Run with detailed output
python -m pytest tests/integration/test_performance.py -v
```

## Setting Up Test Environment

### Database Setup

LedgerLink tests require PostgreSQL for full compatibility due to:
- Materialized views (`orders_orderskuview`, `customer_services_customerserviceview`)
- JSON field operations
- Complex query optimizations

The test database is configured in `tests/integration/conftest.py` which:
1. Sets up the database connection
2. Creates necessary views
3. Provides mock objects for view testing

### Environment Configuration

1. **Local Development**:
   ```bash
   # Set up test database
   createdb ledgerlink_test
   
   # Run migrations on test database
   DATABASE_URL=postgres://username:password@localhost/ledgerlink_test python manage.py migrate
   
   # Run tests using test database
   DATABASE_URL=postgres://username:password@localhost/ledgerlink_test python -m pytest
   ```

2. **CI Environment**:
   - CI pipeline uses PostgreSQL service containers
   - Test databases are created and destroyed for each test run
   - Environment variables configure database connection

## Continuous Integration

Integration tests are run in the CI pipeline defined in `.github/workflows/ci.yml`:

1. **Test Database Setup**:
   - PostgreSQL service container is created
   - Test database is initialized
   - Migrations are applied

2. **Test Execution**:
   - Unit tests are run first
   - Integration tests are run once unit tests pass
   - Performance tests are run on schedule (not per PR)

3. **Contract Verification**:
   - Pact files are verified in dedicated job
   - Results are published to Pact Broker (if configured)

### Example CI Workflow

```yaml
# Excerpt from CI workflow
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests]
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run integration tests
        run: python -m pytest tests/integration/
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
```

## Best Practices

1. **Write Focused Tests**: Each test should verify a specific integration point
2. **Use Representative Data**: Test data should reflect real-world scenarios
3. **Isolate Test Runs**: Tests should not depend on each other's state
4. **Measure Performance**: Include assertions about performance characteristics
5. **Keep Contract Tests Updated**: Update contract tests when API changes
6. **Test Edge Cases**: Include tests for boundary conditions and error cases
7. **Test Real Database Features**: Don't use SQLite for PostgreSQL-specific features

## Further Resources

- See `tests/integration/README.md` for detailed integration test documentation
- Refer to `docs/PACT_TESTING.md` for more on contract testing
- Check `docs/PERFORMANCE_CONSIDERATIONS.md` for optimization tips