# LedgerLink Testing Setup Guide

This guide provides step-by-step instructions for setting up your local environment to run tests in the LedgerLink project.

## Prerequisites

Before setting up the testing environment, ensure you have the following installed:

- Python 3.9+
- Node.js 16+
- npm 7+
- PostgreSQL 13+
- Git

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/company/ledgerlink.git
cd ledgerlink
```

### 2. Backend Setup

#### Create a Python Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Test Database

```bash
# Create a test database
createdb ledgerlink_test

# Configure database connection in LedgerLink/test_settings.py
# The default configuration is:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ledgerlink_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Run Migrations on Test Database

```bash
python manage.py migrate --settings=LedgerLink.test_settings
```

### 3. Frontend Setup

#### Install Frontend Dependencies

```bash
# From the project root
npm install

# Or if you prefer to work from the frontend directory
cd frontend && npm install
```

## Running Tests

### Backend Tests

```bash
# Run all backend tests
./run_tests.sh

# Run tests for a specific app
./run_tests.sh customers

# Run with coverage
./run_tests.sh --cov

# Run specific test file
python -m pytest customers/tests.py -v

# Run tests matching a specific name pattern
python -m pytest -k "customer"
```

### Frontend Tests

```bash
# From the project root
cd frontend

# Run all tests
npm test

# Run tests for specific files
npm test -- components/customers

# Run with coverage
npm test -- --coverage

# Run tests in watch mode (for development)
npm test -- --watch
```

### End-to-End Tests (Cypress)

#### Start the Application Servers

```bash
# Start the backend server
python manage.py runserver

# In another terminal, start the frontend server
cd frontend && npm run dev
```

#### Run Cypress Tests

```bash
# Open Cypress GUI
npm run cypress:open

# Run all tests headlessly
npm run cypress:run

# Run specific test file
npx cypress run --spec "cypress/e2e/auth.cy.js"
```

### Contract Tests

#### Run Consumer Tests

```bash
# From the project root
npm run test:pact
```

#### Run Provider Verification

```bash
# From the project root
npm run test:pact:verify
```

## Setting Up Test Data

### Using Factories

The project uses factories to create test data. You can use these factories in your tests:

```python
# Example of using factories in tests
from test_utils.factories import CustomerFactory, ProductFactory, OrderFactory

# Create a customer
customer = CustomerFactory()

# Create a customer with specific attributes
customer = CustomerFactory(
    company_name="Test Company",
    email="test@example.com"
)

# Create multiple customers
customers = CustomerFactory.create_batch(5)

# Create related objects
product = ProductFactory()
order = OrderFactory(customer=customer)
```

### Using Fixtures

Common test fixtures are available in `conftest.py`:

```python
# Example of using fixtures in tests
def test_with_fixtures(test_user, test_customer, test_product):
    # Test using fixtures
    assert test_customer.created_by == test_user
```

### Creating Custom Fixtures

You can create custom fixtures in your test files or in a local `conftest.py`:

```python
# Example of creating a custom fixture
@pytest.fixture
def premium_customer(test_user):
    """Create a premium customer for testing."""
    return CustomerFactory(
        subscription_level="premium",
        created_by=test_user
    )
```

## Troubleshooting

### Common Issues and Solutions

#### Backend Test Issues

1. **Database connection errors**
   ```
   django.db.utils.OperationalError: could not connect to server
   ```
   Solution: Ensure PostgreSQL is running and the database credentials in `test_settings.py` are correct.

2. **Migrations issues**
   ```
   django.db.utils.ProgrammingError: relation does not exist
   ```
   Solution: Run migrations on your test database: `python manage.py migrate --settings=LedgerLink.test_settings`

3. **Import errors**
   ```
   ImportError: No module named 'some_module'
   ```
   Solution: Ensure all dependencies are installed and you're using the correct virtual environment.

#### Frontend Test Issues

1. **Jest configuration errors**
   ```
   Jest encountered an unexpected token
   ```
   Solution: Check that the transformation configuration in Jest is correct for the file type.

2. **Component not rendering**
   ```
   TypeError: Cannot read property 'addEventListener' of null
   ```
   Solution: Ensure that components requiring DOM interaction are properly mocked or use `@testing-library/user-event`.

3. **Act warnings**
   ```
   Warning: An update to Component inside a test was not wrapped in act(...)
   ```
   Solution: Wrap state updates in `act()` and use `waitFor` or `findBy` queries for async operations.

#### Cypress Test Issues

1. **Element not found**
   ```
   Timed out retrying: Expected to find element: '[data-testid=submit-button]', but never found it.
   ```
   Solution: 
   - Check that the element exists in the page
   - Use Cypress GUI to inspect the page
   - Add appropriate wait conditions

2. **Network errors**
   ```
   CypressError: The following error originated from your application code, not from Cypress.
   ```
   Solution: 
   - Check that the backend server is running
   - Use `cy.intercept()` to mock API responses if needed

#### Pact Test Issues

1. **Contract file not found**
   ```
   Error: Cannot find pact file at /path/to/pacts/...
   ```
   Solution: Ensure consumer tests have been run to generate pact files.

2. **Provider verification failure**
   ```
   Verification failed. Missing resource in interaction.
   ```
   Solution: 
   - Check that provider state setup is correct
   - Ensure the API response structure matches the contract

## Getting Help

If you encounter issues not covered in this guide:

1. Check the existing test files for examples
2. Review the [TESTING_GUIDE.md](TESTING_GUIDE.md) and [WRITING_EFFECTIVE_TESTS.md](WRITING_EFFECTIVE_TESTS.md) documents
3. Ask in the #testing Slack channel for help
4. Check the official documentation for:
   - [pytest](https://docs.pytest.org/)
   - [Jest](https://jestjs.io/docs/getting-started)
   - [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
   - [Cypress](https://docs.cypress.io/)
   - [Pact](https://docs.pact.io/)