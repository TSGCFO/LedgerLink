# Billing App Testing Guide

This comprehensive guide documents the testing architecture for the LedgerLink Billing application, providing detailed information on how to write, run, and maintain tests.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Directory Structure](#test-directory-structure)
3. [Backend Testing](#backend-testing)
   - [Unit Tests](#unit-tests)
   - [Integration Tests](#integration-tests)
   - [Contract Tests](#contract-tests)
4. [Frontend Testing](#frontend-testing)
   - [Component Tests](#component-tests)
   - [Accessibility Tests](#accessibility-tests)
   - [End-to-End Tests](#end-to-end-tests)
5. [Test Data](#test-data)
6. [Mocking and Fixtures](#mocking-and-fixtures)
7. [Testing in Docker](#testing-in-docker)
8. [Continuous Integration](#continuous-integration)
9. [Common Testing Patterns](#common-testing-patterns)
10. [Troubleshooting](#troubleshooting)

## Testing Philosophy

The Billing app follows a comprehensive testing strategy to ensure code quality and prevent regressions:

- **Test Pyramid**: We follow the standard test pyramid with many unit tests, fewer integration tests, and a small number of E2E tests.
- **Test-First Development**: Whenever possible, write tests before implementing new features.
- **Comprehensive Coverage**: Aim for high test coverage (>80%) across all modules.
- **Isolated Tests**: Unit tests should be isolated from external dependencies and run quickly.
- **Real-World Testing**: Integration and E2E tests should mimic real user scenarios.

## Test Directory Structure

The billing app testing structure is organized as follows:

```
billing/
├── tests/                      # Main test directory
│   ├── test_models/            # Tests for Django models
│   ├── test_serializers/       # Tests for DRF serializers
│   ├── test_views/             # Tests for Django views
│   └── test_integration/       # Integration tests
├── test_billing_calculator.py  # Tests for the billing calculator
├── test_case_based_tiers.py    # Tests for tier-based pricing
├── test_services.py            # Tests for service classes
├── test_utils.py               # Tests for utility functions
└── conftest.py                 # pytest fixtures and configuration
```

Frontend tests are located in:

```
frontend/
├── src/
│   ├── components/
│   │   ├── billing/
│   │   │   ├── __tests__/          # React component tests
│   │   │   │   ├── BillingForm.test.jsx
│   │   │   │   ├── BillingList.test.jsx
│   │   │   │   ├── BillingForm.a11y.test.jsx
│   │   │   │   └── BillingList.a11y.test.jsx
├── cypress/
│   ├── e2e/
│   │   ├── billing.cy.js      # Cypress E2E tests for billing
```

## Backend Testing

### Unit Tests

Unit tests verify individual components in isolation. For the billing app, unit tests cover:

- **Models**: Testing model methods, validations, and signals
- **Serializers**: Testing serialization, deserialization, and validation
- **Views**: Testing API endpoints, permissions, and error handling
- **Utilities**: Testing helper functions and utilities
- **Billing Calculator**: Testing calculation logic

#### Writing Model Tests

```python
import pytest
from django.test import TestCase
from billing.models import BillingReport

class BillingReportModelTest(TestCase):
    def setUp(self):
        # Set up test data
        self.billing_report = BillingReport.objects.create(
            name="Test Report",
            # Include required fields
        )
    
    def test_billing_report_creation(self):
        """Test that a billing report can be created with valid data."""
        self.assertEqual(self.billing_report.name, "Test Report")
        
    def test_billing_report_str_method(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.billing_report), "Test Report")
        
    # Add more tests for model methods and properties
```

#### Writing Serializer Tests

```python
import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from billing.models import BillingReport
from billing.serializers import BillingReportSerializer

class BillingReportSerializerTest(TestCase):
    def setUp(self):
        self.billing_report_data = {
            "name": "Test Report",
            # Include required fields
        }
        self.billing_report = BillingReport.objects.create(**self.billing_report_data)
        self.serializer = BillingReportSerializer(instance=self.billing_report)
        
    def test_contains_expected_fields(self):
        """Test that the serializer contains expected fields."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(["id", "name", "created_at", "updated_at"]))
        
    def test_name_field_content(self):
        """Test that the name field content is correct."""
        data = self.serializer.data
        self.assertEqual(data["name"], "Test Report")
        
    def test_validation_error_on_invalid_data(self):
        """Test that validation fails on invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            # Other required fields
        }
        serializer = BillingReportSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
```

#### Writing View Tests

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from billing.models import BillingReport
from django.contrib.auth import get_user_model

User = get_user_model()

class BillingReportViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.billing_report = BillingReport.objects.create(
            name="Test Report",
            # Other required fields
        )
        self.url = reverse("billing-report-detail", kwargs={"pk": self.billing_report.pk})
        
    def test_get_billing_report(self):
        """Test retrieving a billing report."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Report")
        
    def test_update_billing_report(self):
        """Test updating a billing report."""
        data = {"name": "Updated Report"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.billing_report.refresh_from_db()
        self.assertEqual(self.billing_report.name, "Updated Report")
        
    def test_delete_billing_report(self):
        """Test deleting a billing report."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BillingReport.objects.count(), 0)
```

### Integration Tests

Integration tests verify that different components work together correctly. For the billing app, integration tests focus on:

- **API Workflows**: Testing complete API workflows from request to response
- **Database Interactions**: Testing ORM interactions with the database
- **Service Integration**: Testing integration between various services

#### Example Integration Test

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from billing.models import BillingReport
from django.contrib.auth import get_user_model
from rules.models import Rule

User = get_user_model()

class BillingIntegrationTest(APITestCase):
    def setUp(self):
        # Set up test data including related models
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        
        # Create related rule
        self.rule = Rule.objects.create(
            name="Test Rule",
            # Other required fields
        )
        
        # Set up billing report with rule
        self.billing_report = BillingReport.objects.create(
            name="Test Report",
            rule=self.rule,
            # Other required fields
        )
        
    def test_billing_workflow(self):
        """Test a complete billing workflow."""
        # 1. Create a new billing report
        create_url = reverse("billing-report-list")
        create_data = {
            "name": "New Report",
            "rule": self.rule.id,
            # Other required fields
        }
        response = self.client.post(create_url, create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report_id = response.data["id"]
        
        # 2. Update the report
        update_url = reverse("billing-report-detail", kwargs={"pk": report_id})
        update_data = {"name": "Updated Report"}
        response = self.client.patch(update_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Generate billing calculations
        calculate_url = reverse("billing-report-calculate", kwargs={"pk": report_id})
        response = self.client.post(calculate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        
        # 4. Verify the results in the database
        billing_report = BillingReport.objects.get(id=report_id)
        self.assertEqual(billing_report.name, "Updated Report")
        self.assertIsNotNone(billing_report.calculation_results)
```

### Contract Tests

Contract tests verify that API contracts are maintained between frontend and backend. We use Pact for consumer-driven contract testing.

```python
import pytest
from pact import Consumer, Provider
from billing.models import BillingReport
from billing.services import BillingService

def test_billing_service_pact():
    """Test that the billing service meets the contract expected by the frontend."""
    pact = Consumer('BillingFrontend').has_pact_with(Provider('BillingAPI'))
    
    # Define the expected request and response
    pact.given(
        'a billing report exists',
        {'report_id': '1', 'name': 'Test Report'}
    ).upon_receiving(
        'a request for a billing report'
    ).with_request(
        'GET', '/api/billing/reports/1/'
    ).will_respond_with(
        200,
        body={
            'id': '1',
            'name': 'Test Report',
            'created_at': pact.like('2021-01-01T00:00:00Z'),
            'rule': pact.like('1')
        }
    )
    
    # Run the test
    with pact:
        service = BillingService()
        result = service.get_report(1)
        assert result['name'] == 'Test Report'
```

## Frontend Testing

### Component Tests

Component tests verify that React components render correctly and handle user interactions properly.

```jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import BillingForm from '../BillingForm';
import { BrowserRouter } from 'react-router-dom';

// Mock the API client
jest.mock('../../../../utils/apiClient', () => ({
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn(),
}));

describe('BillingForm Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders the form correctly', () => {
    render(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );
    
    expect(screen.getByLabelText(/report name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });
  
  test('handles form submission correctly', async () => {
    const apiClient = require('../../../../utils/apiClient');
    apiClient.post.mockResolvedValueOnce({ data: { id: 1, name: 'Test Report' } });
    
    render(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/report name/i), {
      target: { value: 'Test Report' },
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    
    // Verify API was called with correct data
    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/billing/reports/',
        expect.objectContaining({ name: 'Test Report' })
      );
    });
  });
  
  test('displays validation errors', async () => {
    render(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );
    
    // Submit without filling required fields
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    
    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/report name is required/i)).toBeInTheDocument();
    });
  });
});
```

### Accessibility Tests

Accessibility tests ensure that components meet accessibility standards.

```jsx
import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import BillingForm from '../BillingForm';
import { BrowserRouter } from 'react-router-dom';

expect.extend(toHaveNoViolations);

describe('BillingForm Accessibility', () => {
  test('should not have accessibility violations', async () => {
    const { container } = render(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### End-to-End Tests

E2E tests verify complete user workflows from end to end using Cypress.

```javascript
// frontend/cypress/e2e/billing.cy.js
describe('Billing Workflows', () => {
  beforeEach(() => {
    // Log in before each test
    cy.login('testuser', 'testpassword');
  });
  
  it('should create a new billing report', () => {
    // Visit the billing reports page
    cy.visit('/billing/reports');
    
    // Click the create new report button
    cy.findByRole('button', { name: /create new report/i }).click();
    
    // Fill out the form
    cy.findByLabelText(/report name/i).type('E2E Test Report');
    cy.findByLabelText(/rule/i).select('Test Rule');
    
    // Submit the form
    cy.findByRole('button', { name: /save/i }).click();
    
    // Verify the report was created
    cy.url().should('include', '/billing/reports');
    cy.findByText('E2E Test Report').should('be.visible');
  });
  
  it('should edit an existing billing report', () => {
    // Create a report first
    cy.createBillingReport('Report to Edit');
    
    // Visit the billing reports page
    cy.visit('/billing/reports');
    
    // Click the edit button for the report
    cy.findByText('Report to Edit')
      .parent()
      .findByRole('button', { name: /edit/i })
      .click();
    
    // Update the name
    cy.findByLabelText(/report name/i).clear().type('Updated Report');
    
    // Save changes
    cy.findByRole('button', { name: /save/i }).click();
    
    // Verify the report was updated
    cy.url().should('include', '/billing/reports');
    cy.findByText('Updated Report').should('be.visible');
  });
  
  it('should delete a billing report', () => {
    // Create a report first
    cy.createBillingReport('Report to Delete');
    
    // Visit the billing reports page
    cy.visit('/billing/reports');
    
    // Click the delete button for the report
    cy.findByText('Report to Delete')
      .parent()
      .findByRole('button', { name: /delete/i })
      .click();
    
    // Confirm deletion
    cy.findByRole('button', { name: /confirm/i }).click();
    
    // Verify the report was deleted
    cy.findByText('Report to Delete').should('not.exist');
  });
});
```

## Test Data

### Factory Pattern

We use the factory_boy library to create test data:

```python
import factory
from billing.models import BillingReport
from django.contrib.auth import get_user_model
from rules.models import Rule

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password')

class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule
    
    name = factory.Sequence(lambda n: f"Rule {n}")
    # Set other required fields

class BillingReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BillingReport
    
    name = factory.Sequence(lambda n: f"Report {n}")
    created_by = factory.SubFactory(UserFactory)
    rule = factory.SubFactory(RuleFactory)
    # Set other required fields
```

### Fixtures

We use pytest fixtures to set up test data:

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .factories import UserFactory, RuleFactory, BillingReportFactory

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user

@pytest.fixture
def rule():
    return RuleFactory()

@pytest.fixture
def billing_report(rule):
    return BillingReportFactory(rule=rule)

@pytest.fixture
def multiple_billing_reports(rule):
    return [BillingReportFactory(rule=rule) for _ in range(3)]
```

## Mocking and Fixtures

### Mocking External Services

Use pytest-mock to mock external services:

```python
def test_billing_calculator_with_mocked_service(mocker):
    # Mock the external service
    mock_service = mocker.patch('billing.services.ExternalRateService')
    mock_service.get_rate.return_value = 1.5
    
    # Test the billing calculator
    calculator = BillingCalculator()
    result = calculator.calculate_with_external_rate(100)
    
    # Assertions
    assert result == 150  # 100 * 1.5
    mock_service.get_rate.assert_called_once()
```

### Database Fixtures

For tests requiring database interactions:

```python
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

@pytest.mark.django_db
def test_billing_query_performance(billing_report):
    # Test database query performance
    with CaptureQueriesContext(connection) as context:
        BillingReport.objects.filter(id=billing_report.id).first()
    
    # Assert only one query was executed
    assert len(context.captured_queries) == 1
```

## Testing in Docker

We use Docker containers for consistent test environments. This ensures tests run in an environment that matches production.

### Running Tests in Docker

```bash
# Run all billing tests in Docker
./run_billing_tests.sh

# Run specific tests
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test python -m pytest billing/tests/test_models/ -v
```

See [TESTING_AUTOMATION.md](TESTING_AUTOMATION.md) for more details on Docker-based testing.

## Continuous Integration

Our CI pipeline automatically runs all tests when changes are pushed. See [TESTING_AUTOMATION.md](TESTING_AUTOMATION.md) for details on the CI setup.

## Common Testing Patterns

### Testing Calculations with Parameterized Tests

```python
import pytest

@pytest.mark.parametrize(
    "amount,expected",
    [
        (100, 110),  # 10% tax
        (200, 220),  # 10% tax
        (0, 0),      # Edge case
        (-100, -110) # Negative case
    ]
)
def test_tax_calculation(amount, expected):
    calculator = BillingCalculator()
    result = calculator.calculate_with_tax(amount, 0.1)
    assert result == expected
```

### Testing Error Handling

```python
def test_division_by_zero_error():
    calculator = BillingCalculator()
    with pytest.raises(ZeroDivisionError):
        calculator.divide(10, 0)
```

### Testing Asynchronous Code

```python
import pytest
from asyncio import Future

@pytest.mark.asyncio
async def test_async_billing_calculation(mocker):
    # Mock async function
    mock_async_rate = mocker.patch('billing.services.get_async_rate')
    future = Future()
    future.set_result(1.5)
    mock_async_rate.return_value = future
    
    # Test async calculation
    calculator = BillingCalculator()
    result = await calculator.calculate_async(100)
    
    # Assertions
    assert result == 150
```

## Troubleshooting

### Common Test Failures

- **Database connection issues**: Ensure the test database is running and accessible.
- **Missing migrations**: Run `python manage.py migrate` before tests.
- **Fixture errors**: Check that fixture dependencies are properly set up.
- **Isolation issues**: Ensure tests clean up after themselves to avoid affecting other tests.

### Debugging Tests

```python
import pytest
import logging

# Set up debugging logger
logger = logging.getLogger(__name__)

def test_with_debugging(caplog):
    caplog.set_level(logging.DEBUG)
    logger.debug("Debug information")
    
    # Your test code here
    
    # Check logs
    assert "Debug information" in caplog.text
```

### Using pytest-django debugging tools

```python
@pytest.mark.django_db
def test_with_django_debug_toolbar(client, settings):
    settings.DEBUG = True
    settings.INSTALLED_APPS += ['debug_toolbar']
    
    # Your test code here
```

## Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Cypress Documentation](https://docs.cypress.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)