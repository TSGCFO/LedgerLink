# LedgerLink Testing Documentation

This document serves as a comprehensive guide to the testing approach for the LedgerLink application. It outlines the testing infrastructure, methodologies, and best practices.

## Testing Architecture Overview

LedgerLink implements a multi-layered testing approach:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **API Tests**: Test REST API endpoints
4. **Frontend Component Tests**: Test React UI components
5. **End-to-End Tests**: Test complete user flows
6. **Accessibility Tests**: Ensure WCAG compliance
7. **Performance Tests**: Test system performance under load
8. **Contract Tests**: Ensure backend and frontend API compatibility

## Current Implementation Status

### Completed

- ✅ Backend testing infrastructure with pytest and factory_boy
- ✅ Base test classes for Django and DRF testing
- ✅ Implementation of unit, integration, and API tests for the Customers app
- ✅ Frontend testing with Jest and React Testing Library
- ✅ Component tests for customer management
- ✅ End-to-end testing with Cypress
- ✅ Accessibility testing with jest-axe and cypress-axe
- ✅ Performance testing with k6
- ✅ CI/CD integration with GitHub Actions

### In Progress

- Performance testing with k6
- Visual regression testing
- Comprehensive accessibility testing
- Cross-browser testing

### Completed Recently

- ✅ End-to-end tests with Cypress for all major features
- ✅ Contract testing with Pact for all major APIs (Orders, Billing, Products, Rules, Customers)
- ✅ Backend tests for all core apps
- ✅ Frontend component tests for critical components

## Backend Testing (Django)

### Configuration

- **Framework**: pytest with Django extensions
- **Test Data**: Factory Boy for model generation
- **Base Classes**: Custom TestCase classes with helper methods
- **Database**: PostgreSQL (required for materialized views and other PostgreSQL-specific features)

### Directory Structure

Tests for each Django app follow a consistent structure:

```
app_name/
  tests/
    __init__.py
    factories.py  # Factory Boy factories
    test_models.py
    test_serializers.py
    test_views.py
    test_api.py
```

### Running Backend Tests

```bash
# Run all tests with PostgreSQL (recommended)
DJANGO_SETTINGS_MODULE=LedgerLink.settings.test python manage.py test

# Run tests for a specific app
DJANGO_SETTINGS_MODULE=LedgerLink.settings.test python manage.py test app_name

# Using Docker (recommended for CI/CD)
docker-compose -f docker-compose.test.yml run test

# Run with pytest
DJANGO_SETTINGS_MODULE=LedgerLink.settings.test pytest

# Run with coverage
DJANGO_SETTINGS_MODULE=LedgerLink.settings.test pytest --cov=.
```

> **IMPORTANT**: PostgreSQL is required for proper testing due to the application's use of PostgreSQL-specific features like materialized views. See [Testing with SQLite Issues](TESTING_SQLITE_ISSUES.md) for details.

### Test Markers

The following markers are available:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.db` - Tests requiring database access
- `@pytest.mark.slow` - Slow tests

## Frontend Testing (React)

### Configuration

- **Framework**: Jest with React Testing Library
- **Directory Structure**: Tests adjacent to components in __tests__ directories
- **Accessibility**: jest-axe integration

### Running Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm run test:coverage

# Run accessibility tests only
npm run test:a11y
```

## End-to-End Testing

### Configuration

- **Framework**: Cypress
- **Directory Structure**: Tests organized by feature in cypress/e2e directory
- **Accessibility**: cypress-axe integration

### Running E2E Tests

```bash
# Open Cypress test runner
cd frontend
npm run cypress:open

# Run in headless mode
npm run cypress:run

# Start dev server and run tests
npm run e2e
```

## Performance Testing

### Configuration

- **Framework**: k6
- **Directory Structure**: Tests in tests/performance directory
- **Data**: Test data in JSON format

### Running Performance Tests

```bash
# Run a specific performance test
cd tests/performance
./run_perf_tests.sh
```

## Accessibility Testing

### Configuration

- **Component Level**: jest-axe for React components
- **E2E Level**: cypress-axe for full page testing
- **Standards**: WCAG 2.0 AA compliance

### Running Accessibility Tests

```bash
# Component level
cd frontend
npm run test:a11y

# E2E level
cd frontend
npm run cypress:open
# Then run the a11y.cy.js tests
```

## Contract Testing

### Configuration

- **Framework**: Pact
- **Consumer Tests**: Frontend tests in `/frontend/src/utils/__tests__/*.pact.test.js`
- **Provider Tests**: Backend tests in `<app>/tests/pact_provider.py`

### Running Contract Tests

```bash
# Run consumer tests
cd frontend
npm run test:pact

# Run provider tests
python manage.py test customers.tests.pact_provider
```

## Continuous Integration

GitHub Actions workflows automate testing on pushes and pull requests:

1. **Backend Tests**: Run pytest with coverage
2. **Frontend Tests**: Run Jest tests with coverage
3. **End-to-End Tests**: Run Cypress tests
4. **Contract Tests**: Verify contracts between frontend and backend

Workflow configurations are in the `.github/workflows/` directory.

## Best Practices

1. **Test Organization**:
   - Follow the established patterns and directory structure
   - Name test files and functions clearly

2. **Test Isolation**:
   - Tests should not depend on each other
   - Use factories and fixtures for test data

3. **Coverage**:
   - Aim for 90%+ test coverage for critical components
   - Test edge cases and error conditions

4. **Accessibility**:
   - All new components should have accessibility tests
   - Run automated tests and do manual testing with screen readers

5. **Performance**:
   - Keep tests fast, especially unit tests
   - Use selective test running for development

## Next Steps

1. **Complete Test Coverage**:
   - Implement tests for all backend apps
   - Add tests for all frontend components
   - Create additional E2E test scenarios

2. **Testing Infrastructure**:
   - Set up Docker-based PostgreSQL for local and CI testing
   - Resolve migration dependency issues
   - Add fixtures for materialized views and other complex database structures

3. **Advanced Testing**:
   - Set up Pact broker for contract testing
   - Add security testing with OWASP ZAP
   - Implement visual regression testing

4. **Documentation**:
   - Create component-specific test documentation
   - Add examples of test patterns

5. **Test Performance Optimization**:
   - Implement parallel test execution
   - Add test caching where appropriate
   - Optimize database fixtures

## Further Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Cypress Documentation](https://docs.cypress.io/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Accessibility Testing](https://www.deque.com/axe/)