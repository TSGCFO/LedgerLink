# Billing Tests

## Test Structure

The billing app tests are organized by test type to maintain a clean structure:

- **test_models/** - Tests for all model functionality and relationships
- **test_views/** - Tests for API views and endpoints
- **test_serializers/** - Tests for serializer functionality
- **test_integration/** - Integration tests across components
- **test_calculator/** - Tests for billing calculator logic
- **test_rules/** - Tests for rule operator handling
- **test_tiers/** - Tests for case-based tier calculations
- **test_exporters/** - Tests for report exporters
- **test_services/** - Tests for billing services
- **test_utils/** - Tests for utility functions

## Documentation

Comprehensive documentation for the billing test suite is available in:

- [../TESTING_GUIDE.md](../TESTING_GUIDE.md) - Complete testing guide with patterns and examples
- [../TESTING_QUICKSTART.md](../TESTING_QUICKSTART.md) - Quick reference for common testing tasks
- [../TESTING_AUTOMATION.md](../TESTING_AUTOMATION.md) - CI/CD and automation details

## Key Test Categories

### Core Billing Tests
- **Model Tests**: Validate model properties, constraints, and methods
- **Calculator Tests**: Test the core billing calculation logic including edge cases
- **Export Tests**: Validate export functionality for different formats (PDF, Excel, CSV)

### Integration Tests
- **Rules Integration**: Test integration between billing calculator and rules engine
- **Service Integration**: Test interactions with Orders, Customers, and Services

### Edge Case Tests
- **Case-Based Tier Testing**: Tests for tiered pricing logic with boundary conditions
- **Input Validation**: Test handling of invalid or edge case inputs
- **Export Edge Cases**: Test exports with special characters and large datasets

## Test Fixtures

Fixtures are defined in the conftest.py file and include:

- **billing_user** - A user for billing tests
- **billing_customer** - A customer for billing tests
- **billing_order** - An order with SKU data for testing
- **basic_billing_report** - A basic billing report
- **billing_report_with_details** - A billing report with detailed information
- **case_based_service** - A service configured with case-based tier pricing

## Factory Boy Factories

The `factories.py` file contains factory classes for generating test data:

- **UserFactory** - Creates User instances
- **BillingReportFactory** - Creates BillingReport instances with realistic data
- **BillingReportDetailFactory** - Creates BillingReportDetail instances

## Running Tests

To run all billing tests:

```bash
# Run directly with pytest
python -m pytest billing/tests/ -v

# Using the wrapper script
./run_billing_tests.sh

# With coverage report
coverage run --source='billing' manage.py test billing.tests
coverage report
coverage html
```

To run specific test categories:

```bash
# Run only model tests
python -m pytest billing/tests/test_models/ -v

# Run only calculator tests
python -m pytest billing/tests/test_calculator/ -v

# Run only exporter tests
python -m pytest billing/tests/test_exporters/ -v

# Run only case-based tier tests
python -m pytest billing/tests/test_tiers/ -v
```

## Docker Testing

Tests can be run in a Docker container for a consistent environment:

```bash
# Using Docker with the wrapper script
./run_billing_tests_docker.sh

# Manual Docker run
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test python -m pytest billing/tests/ -v
```

## Test Naming Conventions

Tests follow a consistent naming pattern:

- `test_<feature>_<scenario>.py`: Files are named to indicate the feature and scenario
- `test_<action>_<condition>`: Test methods are named to indicate the action being tested and conditions

## Mocking Strategy

Tests use the following mocking strategies to isolate components:

- Patch database queries to avoid database dependencies
- Mock related services to focus on billing functionality
- Mock methods that require heavy computation
- Use factory-generated fixtures for consistent test data

## New Tests Added

Recent additions to the test suite include:

1. **Edge Case Testing for Calculator** (`test_calculator/test_edge_cases.py`)
   - Tests for handling invalid SKU data
   - Tests for zero or negative quantities
   - Tests for invalid customer IDs and date ranges

2. **Enhanced Exporter Testing** (`test_exporters/test_exporters_detailed.py`)
   - Detailed validation of Excel, PDF, and CSV exports
   - Testing for empty data sets
   - Testing for special characters in exports
   - Testing for large data sets

3. **Advanced Case-Based Tier Testing** (`test_tiers/test_case_based_tiers_advanced.py`)
   - Boundary condition tests for tier ranges
   - Tests for excluded SKUs
   - Tests for multiple orders in different tiers
   - Tests for extremely large case counts

4. **Comprehensive API Testing** (`test_views/test_api_views.py`)
   - Testing for all API endpoints with different request parameters
   - Error handling tests
   - Testing for different export formats