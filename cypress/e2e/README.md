# End-to-End Testing for LedgerLink

This directory contains end-to-end tests for the LedgerLink application using Cypress.

## Test Structure

The tests are organized by feature area:

- `auth.cy.js` - Authentication tests (login/logout)
- `customers.cy.js` - Customer management tests
- `a11y.cy.js` - Accessibility compliance tests

## Running Tests

To run the tests, you need to:

1. Make sure the backend server is running:
   ```
   python manage.py runserver
   ```

2. Make sure the frontend development server is running:
   ```
   cd frontend && npm run dev
   ```

3. Run the tests using one of the following commands:

   ```bash
   # Open Cypress GUI
   npm run cypress:open

   # Run all tests headlessly
   npm run cypress:run

   # Run a specific test file
   npx cypress run --spec "cypress/e2e/auth.cy.js"
   ```

## Test Data

The tests use two approaches for test data:

1. **Predefined data**: Some tests rely on existing data in the database
2. **Dynamic data**: Most tests create their own data with timestamps to ensure uniqueness

## Custom Commands

Custom Cypress commands have been created to simplify common operations:

- `cy.login()` - Log in to the application
- `cy.logout()` - Log out from the application
- `cy.createCustomer()` - Create a test customer
- `cy.cleanupTestData()` - Clean up test data after tests
- `cy.checkA11y()` - Run accessibility checks
- `cy.logA11yViolations()` - Log accessibility violations

## Best Practices

1. **Independent tests**: Each test should be independent and not rely on other tests
2. **Reliable selectors**: Use `data-testid` attributes for selectors
3. **Wait properly**: Use `cy.wait()` with intercepted API calls instead of arbitrary timeouts
4. **Clean up**: Tests should clean up any data they create
5. **Realistic scenarios**: Tests should model realistic user flows

## Adding New Tests

When adding new tests:

1. Create a new `.cy.js` file for the feature area
2. Use the existing patterns for test structure
3. Leverage custom commands where appropriate
4. Add API interception to verify server interactions
5. Include tests for validation and error handling

## Troubleshooting

- **Tests failing at login**: Ensure the test user exists in the database
- **Selector errors**: Check that the `data-testid` attributes match between tests and application
- **Timeouts**: Increase timeouts in the Cypress config or add explicit waits
- **API errors**: Check that the API endpoints match what the tests expect