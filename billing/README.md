# Billing App

The billing app is responsible for generating billing reports based on customer orders and services.

## Key Components

- **BillingReport**: Model for storing generated billing reports
- **BillingReportDetail**: Model for order-specific costs within a report
- **BillingCalculator**: Service for calculating billing amounts based on rules
- **RuleEvaluator**: Utility for evaluating rules against orders
- **Exporters**: Services for exporting billing reports to various formats

## Testing

The billing app has a comprehensive test suite organized by test type.

### Test Directory Structure

```
billing/
  tests/
    test_models/      - Model tests
    test_views/       - API endpoint tests
    test_serializers/ - Serializer tests
    test_calculator/  - Calculator logic tests
    test_integration/ - Integration tests
    test_rules/       - Rule evaluator tests
    test_tiers/       - Case-based tier tests
    test_exporters/   - Exporter tests
    test_services/    - Service tests
    test_utils/       - Utility function tests
```

### Running Tests

To run all billing tests:

```bash
# Using the fully integrated test script
./run_billing_tests.sh

# Run individual test components
docker compose -f docker-compose.test.yml run --rm -e SKIP_MATERIALIZED_VIEWS=True test python -m pytest billing/minimal_test.py -v
docker compose -f docker-compose.test.yml run --rm -e SKIP_MATERIALIZED_VIEWS=True test python -m pytest billing/test_direct.py -v
docker compose -f docker-compose.test.yml run --rm -e SKIP_MATERIALIZED_VIEWS=True test python -m pytest billing/tests/test_models/ -v
```

### Test Implementation

The billing app uses a multi-layered testing approach:

1. **Minimal Tests** (`minimal_test.py`): Basic functionality tests with minimal DB requirements
2. **Direct Tests** (`test_direct.py`): Django TestCase-based tests for reliable database setup
3. **Model Tests** (`tests/test_models/`): Tests for model validation and functionality
4. **Serializer Tests** (`tests/test_serializers/`): Tests for serialization and validation
5. **View Tests** (`tests/test_views/`): Tests for API endpoints
6. **Calculator Tests** (`tests/test_calculator/`): Tests for billing calculation logic
7. **Integration Tests** (`tests/test_integration/`): Tests that verify multiple components working together

The test fixtures in `tests/conftest.py` provide common test data and database setup.

For more details, see [billing/tests/README.md](tests/README.md).

## Implementation Notes

- The billing calculator uses the rules system to determine applicable services
- Rule evaluation supports various operators including equality, comparison, and containment
- Case-based tiers allow for quantity-based pricing with min/max thresholds
- All billing calculations are stored with full audit history