
# LedgerLink Testing Guide

This guide provides comprehensive documentation on testing the LedgerLink application. It covers the different types of tests, how to run them, how to write new tests, and best practices for each testing approach.

## Table of Contents

1. [Testing Strategy Overview](#testing-strategy-overview)
2. [Backend Testing (Django/pytest)](#backend-testing)
3. [Frontend Testing (React Testing Library)](#frontend-testing)
4. [End-to-End Testing (Cypress)](#end-to-end-testing)
5. [Contract Testing (Pact)](#contract-testing)
6. [Continuous Integration](#continuous-integration)
7. [Test Coverage](#test-coverage)
8. [Troubleshooting](#troubleshooting)

## Testing Strategy Overview

LedgerLink employs a comprehensive testing strategy that includes:

- **Unit Tests**: Test individual functions, classes, and components in isolation
- **Integration Tests**: Test interactions between components and with external dependencies
- **End-to-End Tests**: Test complete user flows through the application
- **Contract Tests**: Ensure frontend and backend agree on API contracts
- **Accessibility Tests**: Ensure the application is accessible to all users

### Testing Pyramid

The testing strategy follows the "testing pyramid" approach, with:

- Many fast, focused unit tests at the base
- Fewer integration tests in the middle
- A smaller number of comprehensive end-to-end tests at the top

```
    /\
   /  \
  /E2E \
 /------\
/        \
/ Integra-\
/ tion     \
/-----------\
/             \
/    Unit      \
/               \
-----------------
```

### Test Environment Setup

LedgerLink uses separate settings for testing to ensure tests run consistently and don't impact development or production data:

- **Backend**: Uses `LedgerLink/test_settings.py` with a dedicated test database
- **Frontend**: Uses Jest with mock API responses
- **End-to-End**: Runs against a test database with test data

## Backend Testing

Backend tests use pytest with Django's test framework to test models, views, serializers, and business logic.

### Running Backend Tests

```bash
# Run all backend tests
./run_tests.sh

# Run specific tests
python -m pytest customers/tests.py -v

# Run with coverage
./run_tests.sh --cov
```

### Test Types

#### Model Tests
Test Django models, including validation, methods, and constraints.

```python
# Example model test
@pytest.mark.django_db
def test_customer_creation(test_user):
    customer = CustomerFactory(
        company_name="Test Company",
        created_by=test_user
    )
    assert customer.pk is not None
    assert customer.company_name == "Test Company"
```

#### View Tests
Test Django views and their responses.

```python
# Example view test
def test_order_list_view(self):
    response = self.get_response(self.list_url)    
    assert response.status_code == 200
    assert 'orders' in response.context
    assert len(response.context['orders']) == 3
```

#### API Tests
Test REST API endpoints using Django REST Framework's test utilities.

```python
# Example API test
def test_list_customers(self):
    response = self.get_json_response(self.list_url)
    assert len(response['results']) == 3
    assert response['count'] == 3
```

#### Service Tests
Test business logic and service classes.

```python
# Example service test
def test_calculate_subtotal(self):
    self.calculator._get_order_items = lambda: [
        {'quantity': 2, 'unit_price': Decimal('100.00')},
        {'quantity': 1, 'unit_price': Decimal('50.00')}
    ]
    
    subtotal = self.calculator.calculate_subtotal()
    assert subtotal == Decimal('250.00')
```

### Testing Utilities

#### Factories
Use factories to create test objects quickly:

```python
# Using factories
customer = CustomerFactory()
product = ProductFactory(price=Decimal('100.00'))
order = OrderFactory(customer=customer)
```

#### Fixtures
Common test fixtures are defined in `conftest.py`:

```python
# Using fixtures
def test_with_fixtures(test_user, test_customer, test_product):
    # Test using fixtures
    assert test_customer.created_by == test_user
```

#### Test Mixins
Common test functionality is available through mixins:

```python
# API test with mixins
class TestCustomerAPI(APITestMixin):
    def test_something(self):
        response = self.get_json_response('/api/endpoint/')
        # assertions...
```

### Backend Testing Best Practices

1. **Use factories** for creating test data
2. **Isolate tests** from each other
3. **Mock external dependencies** like APIs or services
4. **Use descriptive test names** that indicate what's being tested
5. **Test edge cases** and error conditions
6. **Use database transaction** for each test
7. **Clean up after tests** (automatically handled by pytest-django)
8. **Use parametrized tests** for similar test cases with different inputs

## Frontend Testing

Frontend tests use Jest and React Testing Library to test React components, hooks, and utilities.

### Running Frontend Tests

```bash
# From the project root
cd frontend

# Run all tests
npm test

# Run specific tests
npm test -- components/customers

# Run with coverage
npm test -- --coverage
```

### Test Types

#### Component Tests
Test React components, their rendering, and user interactions.

```javascript
// Example component test
it('renders the form in create mode', () => {
    render(<CustomerForm />);
    
    expect(screen.getByText('New Customer')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create customer/i })).toBeInTheDocument();
});
```

#### Hook Tests
Test custom React hooks.

```javascript
// Example hook test
it('fetches customers list', async () => {
    const { result } = renderHook(() => useCustomerData());
    
    act(() => {
        result.current.fetchCustomers();
    });
    
    await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.customers).toEqual(mockCustomers);
    });
});
```

#### Utility Tests
Test utility functions and services.

```javascript
// Example utility test
it('formats currency correctly', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
    expect(formatCurrency(0)).toBe('$0.00');
});
```

### Frontend Testing Utilities

#### User Event
Simulate user interactions:

```javascript
// Using user events
const user = userEvent.setup();
await user.type(screen.getByLabelText(/email/i), 'test@example.com');
await user.click(screen.getByRole('button', { name: /submit/i }));
```

#### Mock Functions
Mock dependencies, API calls, and callbacks:

```javascript
// Mocking API calls
const mockApi = vi.fn(() => Promise.resolve({ data: mockData }));
vi.mock('../api', () => ({ api: { get: mockApi } }));
```

#### Testing Library Queries
Use Testing Library's queries to find elements:

```javascript
// Finding elements
const submitButton = screen.getByRole('button', { name: /submit/i });
const nameInput = screen.getByLabelText(/name/i);
const errorMessage = screen.queryByText(/error/i);
```

### Frontend Testing Best Practices

1. **Test behavior, not implementation** details
2. **Use screen queries** that match how users find elements
3. **Prefer user-event over fireEvent** for more realistic interactions
4. **Mock API calls** and external dependencies
5. **Test accessibility** aspects like focus management and screen reader support
6. **Test error states** and loading indicators
7. **Use `data-testid` attributes** sparingly for items that are hard to query otherwise
8. **Use toHaveAccessibleName** and other a11y-related matchers

## End-to-End Testing

End-to-end tests use Cypress to test complete user flows through the application.

### Running E2E Tests

```bash
# Open Cypress GUI
npm run cypress:open

# Run all tests in headless mode
npm run cypress:run

# Run specific test file
npx cypress run --spec "cypress/e2e/auth.cy.js"
```

### Test Examples

#### Authentication Flow
Test login and logout.

```javascript
// Example auth test
it('logs in successfully', () => {
    cy.visit('/login');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome, testuser');
});
```

#### Form Submission
Test form validations and submissions.

```javascript
// Example form test
it('validates required fields', () => {
    cy.visit('/customers/new');
    cy.get('button[type="submit"]').click();
    cy.contains('Company name is required');
    cy.contains('Email is required');
});
```

#### Data Interactions
Test CRUD operations through the UI.

```javascript
// Example data test
it('creates a new customer', () => {
    cy.login();
    cy.visit('/customers/new');
    cy.get('input[name="company_name"]').type('New Company');
    cy.get('input[name="email"]').type('new@example.com');
    cy.get('button[type="submit"]').click();
    cy.contains('Customer created successfully');
    cy.contains('New Company');
});
```

### Cypress Custom Commands

Custom commands simplify common operations:

```javascript
// Using custom commands
cy.login('admin', 'password');
cy.createCustomer({ name: 'Test Company' });
cy.checkA11y(); // Run accessibility checks
```

### E2E Testing Best Practices

1. **Test critical user flows** like authentication, main features
2. **Use custom commands** for repeated actions
3. **Set up test data** programmatically instead of through UI
4. **Wait for API responses** rather than using arbitrary timeouts
5. **Use data-testid attributes** for stable element selection
6. **Run accessibility checks** on key pages
7. **Clean up test data** after tests to keep the test environment clean
8. **Use API interceptions** to test error states and loading behavior

## Contract Testing

Contract tests use Pact to ensure frontend and backend agree on API structure. For details, see [CONTRACT_TESTING.md](CONTRACT_TESTING.md).

### Running Contract Tests

```bash
# Run consumer tests
npm run test:pact

# Run provider verification
npm run test:pact:verify
```

### Contract Testing Best Practices

1. **Focus on structure, not data** using matchers
2. **Keep provider states simple**
3. **Run verification regularly** in CI/CD
4. **Document provider states** clearly
5. **Version your contracts** for backward compatibility

## Continuous Integration

LedgerLink uses GitHub Actions for continuous integration.

### CI Workflow

The CI pipeline includes:

1. **Linting**: Check code style and formatting
2. **Unit Tests**: Run backend and frontend unit tests
3. **Contract Tests**: Verify API contracts
4. **E2E Tests**: Run Cypress tests headlessly
5. **Coverage Reports**: Generate and publish coverage reports

### Running Tests Locally Before Commit

```bash
# Run quick checks before committing
npm run lint
./run_tests.sh
npm test
```

## Test Coverage

LedgerLink monitors test coverage to ensure adequate testing.

### Coverage Goals

- **Backend**: 80% code coverage
- **Frontend**: 70% code coverage
- **Critical paths**: 100% coverage

### Checking Coverage

```bash
# Backend coverage
./run_tests.sh --cov

# Frontend coverage
cd frontend && npm test -- --coverage
```

## Troubleshooting

### Common Testing Issues

#### Backend Tests

- **Database errors**: Check if migrations are applied to the test database
- **Fixture errors**: Ensure dependencies are correctly defined in conftest.py
- **Permission issues**: Test with different user roles

#### Frontend Tests

- **Act warnings**: Wrap state changes in act()
- **Element not found**: Check the rendered output with screen.debug()
- **Async issues**: Use waitFor or findBy queries for async operations

#### E2E Tests

- **Selectors not working**: Use Cypress GUI to inspect elements
- **Timing issues**: Use cy.wait() for network requests
- **Test data problems**: Use cy.task() to set up data directly

### Getting Help

- Check the [Pytest Documentation](https://docs.pytest.org/)
- Check the [React Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)
- Check the [Cypress Documentation](https://docs.cypress.io/)
- Ask in the #testing Slack channel for help