# End-to-End Tests for LedgerLink

This directory contains end-to-end tests for the LedgerLink application using Cypress. These tests simulate real user interactions with the application to verify that all features work correctly from the user's perspective.

## Test Files

- **auth.cy.js**: Tests authentication functionality (login, logout, protected routes)
- **customers.cy.js**: Tests customer management features (listing, creating, editing, deleting)
- **orders.cy.js**: Tests order management features (listing, creating, viewing, updating status)
- **products.cy.js**: Tests product management features (listing, creating, editing, deleting)
- **billing.cy.js**: Tests billing report generation and viewing
- **rules.cy.js**: Tests rule management features (creating rule groups, basic rules, advanced rules)
- **services.cy.js**: Tests service management features (listing, creating, editing, deleting)
- **customer_services.cy.js**: Tests customer-specific service configurations (linking customers to services)
- **a11y.cy.js**: Accessibility tests for all major pages

## Running the Tests

### Prerequisite

Before running the tests, ensure that:

1. Both the backend (Django) and frontend (React) servers are running:
   - Backend: `python manage.py runserver` (port 8000)
   - Frontend: `cd frontend && npm run dev` (port 5175)

2. The test database is properly set up with required fixtures:
   - `python manage.py migrate`
   - `python manage.py loaddata test_fixtures`

### Commands

```bash
# Open Cypress Test Runner (interactive mode)
npm run cypress:open

# Run all tests headlessly
npm run cypress:run

# Run specific test file
npm run cypress:run -- --spec "cypress/e2e/customers.cy.js"

# Run specific test file with browser specified
npm run cypress:run -- --browser chrome --spec "cypress/e2e/auth.cy.js"
```

## Test Organization

Each test file follows a consistent pattern:

1. **Setup**: Log in before tests and set up API interceptors
2. **Page Verification**: Verify page elements are displayed correctly
3. **Navigation**: Test navigation between pages
4. **CRUD Operations**: Test create, read, update, delete operations
5. **Form Validation**: Test validation of form inputs
6. **Error Handling**: Test error messages and edge cases

## Custom Commands

Custom Cypress commands are available in `cypress/support/commands.js`:

- `cy.login()`: Logs in with default test credentials
- `cy.logout()`: Logs out the current user
- `cy.createCustomer()`: Creates a test customer for testing
- `cy.cleanupTestData()`: Cleans up test data after tests
- `cy.checkA11y()`: Runs accessibility checks on the current page

## API Mocking

Tests use Cypress's intercept feature to:

1. Monitor API calls for verification
2. Mock API responses for consistent testing
3. Test error states by returning mock error responses

Example:
```javascript
cy.intercept('GET', '/api/v1/customers/*').as('getCustomers');
cy.visit('/customers');
cy.wait('@getCustomers');
```

## Accessibility Testing

The `a11y.cy.js` file contains tests that verify the application meets WCAG 2.0 AA accessibility standards. These tests use `cypress-axe` to identify accessibility issues.

## Best Practices

1. **Independence**: Each test should be independent and not rely on the state from previous tests
2. **Reset State**: Use `beforeEach` to reset state between tests
3. **API Intercepts**: Set up intercepts before actions that trigger API calls
4. **Selectors**: Use data-testid attributes for selecting elements
5. **Assertions**: Make specific assertions about the expected state
6. **Timeouts**: Use `cy.wait()` for API calls rather than arbitrary timeouts
7. **Screenshots**: Cypress automatically captures screenshots on test failures

## Adding New Tests

When adding new tests:

1. Create a new file following the naming convention `[feature].cy.js`
2. Import necessary commands and set up common beforeEach hooks
3. Organize tests logically using describe and it blocks
4. Add comments explaining the purpose of each test section
5. Follow existing patterns for consistency

## Testing Strategy

- **Critical Paths**: Focus on testing the most critical user paths
- **Edge Cases**: Include tests for important edge cases and error conditions
- **Real-world Scenarios**: Design tests around realistic user scenarios
- **API Consistency**: Verify API contracts match expectations
- **Performance**: Avoid unnecessary test steps that slow down the test suite