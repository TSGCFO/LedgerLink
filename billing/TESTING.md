# Billing App Testing Guide

This document provides guidance for testing the Billing app in the LedgerLink project. The Billing app is responsible for generating billing reports, calculating service costs based on rules, and providing various report formats for customers.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Test Categories](#test-categories)
3. [How to Run Tests](#how-to-run-tests)
4. [Test Data Setup](#test-data-setup)
5. [Common Fixtures](#common-fixtures)
6. [Testing the BillingCalculator](#testing-the-billingcalculator)
7. [Testing Case-Based Tiers](#testing-case-based-tiers)
8. [Testing Services and Views](#testing-services-and-views)
9. [Integration Testing](#integration-testing)
10. [Test Coverage](#test-coverage)

## Test Structure

The Billing app tests are organized into the following structure:

```
billing/
├── tests/
│   ├── __init__.py
│   ├── factories.py           # Factory classes for test data creation
│   ├── test_models/           # Tests for models
│   │   ├── __init__.py
│   │   ├── test_billing_report.py
│   │   └── test_billing_report_detail.py
│   ├── test_serializers/      # Tests for serializers
│   │   ├── __init__.py
│   │   ├── test_billing_report_serializer.py
│   │   └── test_report_request_serializer.py
│   ├── test_views/            # Tests for views
│   │   ├── __init__.py
│   │   ├── test_billing_report_list_view.py
│   │   └── test_generate_report_api_view.py
│   ├── test_integration/      # Integration tests
│   │   ├── __init__.py
│   │   ├── test_billing_calculator_with_rules.py
│   │   └── test_billing_integration.py
│   ├── test_utils.py          # Tests for utility functions
│   ├── test_services.py       # Tests for service layer
│   └── test_exporters.py      # Tests for exporters
├── conftest.py                # Common fixtures for billing tests
└── test_*.py                  # Top-level test files (legacy)
```

## Test Categories

The Billing app tests are divided into the following categories:

1. **Model Tests**: Tests for the `BillingReport` and `BillingReportDetail` models.
2. **Serializer Tests**: Tests for the serializers used in API responses.
3. **View Tests**: Tests for API endpoints and view logic.
4. **Service Tests**: Tests for the `BillingReportService` class.
5. **Utility Tests**: Tests for utility functions and helper classes.
6. **Calculator Tests**: Tests for the billing calculator logic.
7. **Integration Tests**: Tests for integration between components and apps.

## How to Run Tests

### Running All Billing Tests

```bash
# Using the provided script
./run_billing_tests.sh

# Using pytest directly
python -m pytest billing/
```

### Running Specific Test Files

```bash
# Running a specific test file
python -m pytest billing/tests/test_models/test_billing_report.py

# Running a specific test class
python -m pytest billing/tests/test_models/test_billing_report.py::TestBillingReportModel

# Running a specific test method
python -m pytest billing/tests/test_models/test_billing_report.py::TestBillingReportModel::test_create_billing_report
```

### Running Tests in Docker

```bash
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest billing/ -v
```

### Running Tests with TestContainers

```bash
USE_TESTCONTAINERS=True python -m pytest billing/ -v
```

## Test Data Setup

The Billing app tests use several fixtures and factory classes to set up test data. The primary factory classes are:

1. **BillingReportFactory**: Creates BillingReport instances with realistic data.
2. **BillingReportDetailFactory**: Creates BillingReportDetail instances.
3. **UserFactory**: Creates User instances for testing.

Example usage:

```python
from billing.tests.factories import BillingReportFactory

# Create a billing report
report = BillingReportFactory()

# Create a billing report with specific attributes
report = BillingReportFactory(
    customer=customer,
    total_amount=Decimal('150.00')
)
```

## Common Fixtures

The following fixtures are commonly used in Billing app tests:

1. **billing_user**: A user for billing tests.
2. **billing_customer**: A customer for billing tests.
3. **billing_order**: An order for billing tests with SKU data.
4. **basic_billing_report**: A basic billing report.
5. **billing_report_with_details**: A billing report with details.
6. **case_based_service**: A case-based service configuration.

These fixtures are defined in `billing/conftest.py` and can be used in any test function.

Example usage:

```python
def test_something(basic_billing_report):
    """Test something using the basic_billing_report fixture."""
    assert basic_billing_report.total_amount == Decimal('100.00')
```

## Testing the BillingCalculator

The `BillingCalculator` is a core component of the Billing app. It calculates service costs based on order data and service rules. Testing it thoroughly is essential for ensuring accurate billing.

Key aspects to test:

1. **Rule Evaluation**: Test individual rule evaluation logic.
2. **Service Cost Calculation**: Test the calculation of service costs for different service types.
3. **Report Generation**: Test the generation of billing reports.
4. **Data Conversion**: Test conversion of report data to various formats (JSON, CSV).

Example test:

```python
def test_billing_calculator(self, setup_test_data):
    """Test the BillingCalculator."""
    # Create calculator
    calculator = BillingCalculator(customer_id, start_date, end_date)
    
    # Generate report
    report = calculator.generate_report()
    
    # Verify report data
    assert report.total_amount == expected_amount
    assert len(report.order_costs) == expected_order_count
```

## Testing Case-Based Tiers

Case-based tiers are a complex feature of the Billing app. They allow pricing to be determined based on case quantities with different multipliers for different ranges.

Key aspects to test:

1. **Tier Range Handling**: Test tier range logic for min/max values.
2. **Excluded SKUs**: Test handling of excluded SKUs.
3. **Case Calculation**: Test case quantity calculation.
4. **Tier Selection**: Test selection of the correct tier based on case quantity.

Example test:

```python
def test_case_based_tier_evaluation(self, setup_test_data):
    """Test case-based tier evaluation."""
    # Set up order with case data
    order = create_order_with_cases(cases=5)
    
    # Evaluate rule
    applies, multiplier, case_summary = RuleEvaluator.evaluate_case_based_rule(rule, order)
    
    # Verify results
    assert applies is True
    assert multiplier == Decimal('2.0')  # Tier with range 4-6
    assert case_summary['total_cases'] == 5
```

## Testing Services and Views

Testing services and views ensures that the API endpoints and business logic work as expected.

Key aspects to test:

1. **API Request Validation**: Test validation of API request data.
2. **Report Generation**: Test report generation with different parameters.
3. **Caching**: Test caching of reports for performance.
4. **Error Handling**: Test error handling for various scenarios.

Example test:

```python
def test_generate_report_api(self, api_client, url, billing_customer):
    """Test report generation API."""
    # Prepare request data
    data = {
        'customer': billing_customer.id,
        'start_date': '2023-01-01',
        'end_date': '2023-01-31',
        'output_format': 'preview'
    }
    
    # Make request
    response = api_client.post(url, data=data, format='json')
    
    # Verify response
    assert response.status_code == 200
    assert response.data['success'] is True
    assert 'preview_data' in response.data['data']
```

## Integration Testing

Integration tests verify that different components of the Billing app work together correctly.

Key aspects to test:

1. **Rule Integration**: Test integration of rules with billing calculation.
2. **Cross-App Integration**: Test integration with other apps (Customers, Orders).
3. **Database Integration**: Test database operations with complex report data.

Example test:

```python
def test_cross_app_integration(self, billing_customer):
    """Test integration between billing, customers, and orders apps."""
    # Create order for customer
    order = Order.objects.create(customer=billing_customer, ...)
    
    # Create billing report
    report = BillingReport.objects.create(customer=billing_customer, ...)
    
    # Verify relationships
    assert order.customer == billing_customer
    assert report.customer == billing_customer
```

## Test Coverage

To generate a test coverage report for the Billing app:

```bash
# Generate coverage report
coverage run --source='billing' manage.py test billing
coverage report
coverage html  # For HTML report

# Using pytest with coverage
python -m pytest --cov=billing billing/
```

The goal is to maintain at least 90% test coverage for the Billing app, with particular focus on the billing calculator, rule evaluation, and service cost calculation logic.

### Key Areas to Cover

1. **Billing Calculator**: All methods and branches should be covered.
2. **Rule Evaluator**: All operators and field types should be covered.
3. **Service Logic**: All service types and charge types should be covered.
4. **Error Handling**: All error and edge cases should be covered.

---

For any questions or suggestions about testing the Billing app, please contact the development team.