# Billing App Testing Quick Start Guide

This document provides a quick reference for running and writing tests for the billing app.

## Running Tests

### Backend Tests

```bash
# Set up the testing environment
./billing/setup_test_env.sh

# Run all billing tests (recommended)
./run_billing_tests.sh

# Generate coverage report
./run_billing_coverage.sh

# Run specific test categories
python -m pytest billing/tests/test_models/ -v
python -m pytest billing/tests/test_serializers/ -v
python -m pytest billing/tests/test_views/ -v
python -m pytest billing/tests/test_integration/ -v

# Run core billing tests
python -m pytest billing/test_billing_calculator.py -v
python -m pytest billing/test_case_based_tiers.py -v

# Run with specific pytest options
python -m pytest billing/ -v --tb=short
python -m pytest billing/ -v -k "calculator"  # Run tests with "calculator" in the name
python -m pytest billing/ -v --no-header  # Hide pytest header
python -m pytest billing/ -v --showlocals  # Show local variables in tracebacks
```

### Frontend Tests

```bash
# Run from the frontend directory
cd frontend

# Run billing component tests
npm test -- --testPathPattern=src/components/billing

# Run with coverage
npm test -- --testPathPattern=src/components/billing --coverage

# Run accessibility tests
npm run test:a11y -- --testPathPattern=src/components/billing

# Run E2E tests for billing
npm run cypress:open
# Then select billing.cy.js in the Cypress UI

# Run E2E tests headlessly
npm run cypress:run -- --spec "cypress/e2e/billing.cy.js"
```

### Docker Tests

```bash
# Run tests in Docker environment (most reliable)
./run_billing_tests.sh

# Run specific tests in Docker
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test python -m pytest billing/tests/test_models/ -v
```

## Test Writing Reference

### Backend Test File Naming and Location

- Model tests: `billing/tests/test_models/test_<model_name>.py`
- Serializer tests: `billing/tests/test_serializers/test_<serializer_name>.py`
- View tests: `billing/tests/test_views/test_<view_name>.py`
- Integration tests: `billing/tests/test_integration/test_<feature>.py`
- Utility tests: `billing/test_utils.py`
- Calculator tests: `billing/test_billing_calculator.py`
- Tier-based pricing tests: `billing/test_case_based_tiers.py`

### Frontend Test File Naming and Location

- Component tests: `frontend/src/components/billing/__tests__/<Component>.test.jsx`
- Accessibility tests: `frontend/src/components/billing/__tests__/<Component>.a11y.test.jsx`
- E2E tests: `frontend/cypress/e2e/billing.cy.js`

### Test Class and Method Naming Conventions

```python
# For a model test
class BillingReportModelTest(TestCase):
    def test_billing_report_creation(self):
        """Test that a billing report can be created with valid data."""
        # Test code here
        
    def test_billing_report_str_method(self):
        """Test the string representation of the model."""
        # Test code here
```

### Common Testing Patterns

#### Model Test Pattern

```python
from django.test import TestCase
from billing.models import BillingReport

class BillingReportModelTest(TestCase):
    def setUp(self):
        self.billing_report = BillingReport.objects.create(
            name="Test Report",
            # Include required fields
        )
    
    def test_billing_report_attributes(self):
        """Test that the billing report has the correct attributes."""
        self.assertEqual(self.billing_report.name, "Test Report")
```

#### Serializer Test Pattern

```python
from django.test import TestCase
from billing.models import BillingReport
from billing.serializers import BillingReportSerializer

class BillingReportSerializerTest(TestCase):
    def setUp(self):
        self.billing_report = BillingReport.objects.create(
            name="Test Report",
            # Include required fields
        )
        self.serializer = BillingReportSerializer(instance=self.billing_report)
    
    def test_contains_expected_fields(self):
        """Test that the serializer contains expected fields."""
        data = self.serializer.data
        self.assertIn("name", data)
```

#### API View Test Pattern

```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from billing.models import BillingReport
from django.contrib.auth import get_user_model

User = get_user_model()

class BillingReportAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        
        self.billing_report = BillingReport.objects.create(
            name="Test Report",
            # Include required fields
        )
        
        self.url = reverse("billing-report-detail", kwargs={"pk": self.billing_report.pk})
    
    def test_get_billing_report(self):
        """Test retrieving a billing report."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Using Fixtures with pytest

```python
import pytest
from billing.models import BillingReport

@pytest.fixture
def billing_report():
    return BillingReport.objects.create(
        name="Test Report",
        # Include required fields
    )

def test_billing_report_name(billing_report):
    """Test billing report name using fixture."""
    assert billing_report.name == "Test Report"
```

### Mocking with pytest

```python
def test_with_mocked_service(mocker):
    """Test with a mocked service."""
    # Mock the service
    mock_service = mocker.patch('billing.services.ExternalService')
    mock_service.get_data.return_value = {'key': 'value'}
    
    # Use the service in your test
    from billing.services import BillingService
    service = BillingService()
    result = service.process_data()
    
    # Assert the mock was called
    mock_service.get_data.assert_called_once()
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize(
    "amount,tax_rate,expected",
    [
        (100, 0.1, 110),   # 10% tax
        (200, 0.2, 240),   # 20% tax
        (300, 0, 300),     # 0% tax
    ]
)
def test_tax_calculation(amount, tax_rate, expected):
    """Test tax calculation with different inputs."""
    from billing.services import BillingCalculator
    calculator = BillingCalculator()
    result = calculator.calculate_with_tax(amount, tax_rate)
    assert result == expected
```

### Frontend Component Test Pattern

```jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import BillingForm from '../BillingForm';

describe('BillingForm Component', () => {
  test('renders the form correctly', () => {
    render(<BillingForm />);
    expect(screen.getByLabelText(/report name/i)).toBeInTheDocument();
  });
  
  test('handles input changes', () => {
    render(<BillingForm />);
    const input = screen.getByLabelText(/report name/i);
    fireEvent.change(input, { target: { value: 'Test Report' } });
    expect(input.value).toBe('Test Report');
  });
});
```

## Common Issues and Solutions

### Missing Database Connection

If tests fail due to missing database connection:

1. Check that PostgreSQL is running
2. Verify database settings in `conftest.py` or Django settings
3. For Docker tests, try `docker compose -f docker-compose.test.yml down -v` then run tests again

### Test Database Not Created

If the test database doesn't exist:

```bash
# Run migrations manually
python manage.py migrate --settings=LedgerLink.settings
```

### Tests Skip Materialized Views

Add the `SKIP_MATERIALIZED_VIEWS=True` environment variable:

```bash
SKIP_MATERIALIZED_VIEWS=True python -m pytest billing/
```

### Frontend Tests Fail to Find Elements

1. Check the selectors being used
2. Use `screen.debug()` to see the rendered HTML
3. Make sure components are wrapped in necessary providers (Router, etc.)

## See Also

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing documentation
- [TESTING_AUTOMATION.md](TESTING_AUTOMATION.md) - CI/CD and automation details