# LedgerLink Testing Guide

This guide provides instructions for setting up and running tests in the LedgerLink application.

## Test Environment Setup

### 1. Database Configuration

For testing, you should configure your environment to use SQLite instead of PostgreSQL to avoid database connection issues. This is set up in the `settings.py` file:

```python
# In settings.py
import sys

# Use SQLite for tests to avoid issues with external database during testing
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # Use in-memory database for faster tests
        }
    }
```

### 2. Required Packages

Ensure you have all the required packages installed:

```bash
pip install -r requirements.txt
```

For frontend testing, also install the Node.js dependencies:

```bash
cd frontend
npm install
```

## Running Tests

### Django Backend Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test rules

# Run a specific test class
python manage.py test rules.tests.RuleEvaluatorTests

# Run a specific test method
python manage.py test rules.tests.RuleEvaluatorTests.test_ne_operator

# Run with verbosity for more details
python manage.py test --verbosity=2

# Keep the test database between runs (speeds up multiple test runs)
python manage.py test --keepdb
```

For a Docker-based environment, use the convenience scripts:

```bash
./run_docker_tests.sh              # Run the full test suite
./run_orders_tests.sh              # Example: run tests for the orders app
```

### Standalone Test Scripts

For testing specific functionality without requiring a full Django test environment, use the standalone test scripts in the `test_scripts` directory:

```bash
# Test the 'ne' operator functionality
python test_scripts/test_ne_operator.py

# Test case-based tier rules
python test_scripts/test_rule_engine.py
```

### Frontend Tests

```bash
# Run all frontend tests
cd frontend
npm test

# Run tests with coverage report
npm test -- --coverage

# Run a specific test file
npm test -- src/components/rules/__tests__/ValidationConsistency.test.js
```

## Test Database Troubleshooting

If you encounter issues with the test database:

1. **Database already exists error**:
   ```bash
   python manage.py test --keepdb
   ```

2. **Permission issues with test database**:
   ```bash
   # Drop the test database manually
   psql -c "DROP DATABASE test_postgres"
   
   # Then run tests
   python manage.py test
   ```

3. **Non-interactive test execution**:
   ```bash
   python manage.py test --noinput
   ```

## Types of Tests

LedgerLink includes several types of tests:

### 1. Unit Tests

- Test individual functions or classes in isolation
- Located in `tests.py` files in each app
- Example: `rules/tests.py`

### 2. Integration Tests

- Test the interaction between components
- Located in files like `test_integration.py`
- Example: `rules/test_integration.py`

### 3. Standalone Test Scripts

- Test specific functionality without Django test infrastructure
- Located in the `test_scripts` directory
- Example: `test_scripts/test_ne_operator.py`

### 4. Frontend Tests

- Test React components and utilities
- Located in `__tests__` directories in the frontend structure
- Example: `frontend/src/components/rules/__tests__/ValidationConsistency.test.js`

## Testing Specific Features

### 1. Rule Evaluation

For testing rule evaluation, there are several options:

1. **Unit tests**: Use `rules/test_condition_evaluator.py` to test the `evaluate_condition` function directly
2. **Integration tests**: Use `rules/test_rule_evaluation.py` to test rule evaluation with models
3. **Frontend tests**: Use the Rule Tester UI to test rule evaluation in the browser

### 2. Operator Testing

For testing specific operators (like 'ne'):

1. Use `test_scripts/test_ne_operator.py` for standalone testing
2. Use `rules/test_condition_evaluator.py` for unit testing
3. Use `rules/test_rule_tester.py` for API endpoint testing

### 3. Manual Testing via Rule Tester UI

To manually test rule evaluation:

1. Start the development server: `python manage.py runserver`
2. Navigate to the Rules Management page
3. Click on the "Rule Tester" tab
4. Enter test conditions and order data
5. Click "Test Rule" to see the evaluation result

## Writing New Tests

When adding new features or fixing bugs, create appropriate tests:

1. **Unit tests** for individual functions or methods
2. **Integration tests** for interactions between components
3. **Frontend tests** for React components and UI behavior
4. **Standalone scripts** for complex functionality that's hard to test in Django's framework

Follow these guidelines for test naming:

- `test_<feature>_<scenario>` for test methods
- `Test<Feature>` for test classes

## Test Coverage

To generate a test coverage report:

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate an HTML report
coverage html

# View the report
open htmlcov/index.html
```

For frontend coverage:

```bash
cd frontend
npm test -- --coverage
```

## API Contract Testing

We use Pact for contract testing between our frontend (consumer) and backend (provider). This ensures that API contracts are maintained.

### Consumer Tests (Frontend)

Consumer tests define the expectations that the frontend has for the backend API:

```bash
# Run all consumer tests
cd frontend
npm run test:pact

# Run a specific contract test
npm test -- src/utils/__tests__/products.pact.test.js
```

Consumer tests are located in:
- `frontend/src/utils/__tests__/*.pact.test.js`

### Provider Tests (Backend)

These tests verify the backend implements the API according to the consumer's expectations:

```bash
# Run provider tests for an app
python manage.py test customers.tests.pact_provider
```

### Contract Testing Workflow

1. Frontend developers write consumer tests defining API expectations
2. Tests generate Pact files in `frontend/pacts/`
3. Backend developers run provider tests against these Pact files
4. CI pipeline verifies both sides of the contract

### Best Practices

1. **Always update contracts first**: When changing an API, update the contract test before changing the implementation
2. **Version your contracts**: Use semantic versioning for your Pact contracts
3. **Use provider states**: Define clear provider states for different testing scenarios
4. **Test all response fields**: Ensure your contracts test all relevant fields in responses
5. **Include error cases**: Test both successful and error responses

## Continuous Integration

The test suite runs automatically in the CI pipeline for:

1. Pull requests to the main branch
2. Commits to the main branch

The CI pipeline includes:

1. Linting (ESLint, Black)
2. Type checking (TypeScript, mypy)
3. Unit and integration tests
4. Frontend tests

## Troubleshooting

### Common Test Issues

1. **Database connection errors**: Use the SQLite configuration or `--keepdb` flag
2. **Import errors**: Check that the package is installed and the import path is correct
3. **Test data setup issues**: Ensure your test class properly sets up test data in `setUp`
4. **Frontend test failures**: Check that the component props match what the test expects

### Getting Help

If you encounter issues with the test suite:

1. Check the logs for detailed error messages
2. Review this testing guide for common solutions
3. Check the Django testing documentation for general Django testing issues
4. Contact the development team for project-specific issues
