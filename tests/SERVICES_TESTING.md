# Services Testing Guide

This document outlines the testing approach for the Services module in LedgerLink.

## Overview

The Services module is a fundamental component that defines the available services that can be assigned to customers. It serves as a foundation for the Customer Services module and the rules system.

## Test Coverage

The Services module has comprehensive test coverage across multiple levels:

### 1. Model and Serializer Tests

Located in `services/tests.py`, these tests verify:

- Service model functionality
- Field validations and constraints
- Serializer functionality and validation
- Unique name validation (including case-insensitive checks)
- Charge type choices

### 2. API Endpoint Tests

These tests ensure the API endpoints function correctly:

- List endpoint with filtering and searching
- Detail endpoint for specific service
- Create endpoint with validation
- Update endpoint functionality
- Delete endpoint functionality with dependency checking
- Custom endpoints for retrieving charge types

### 3. Integration Tests

Located in `services/test_integration.py`, these tests verify:

- Integration with the Customer Services system
- Deletion prevention with related CustomerService records
- Relationships with Customers module
- Rule group creation using services

### 4. Contract Tests

Located in `services/test_pact_provider.py`, these tests ensure:

- API contracts are maintained between frontend and backend
- Response formats match frontend expectations
- All expected endpoints are available and functioning
- Provider states are properly set up for Pact verification

### 5. End-to-End Tests

Located in `frontend/cypress/e2e/services.cy.js`, these tests verify:

- User interface for service management
- Full user flows from UI to database and back
- Form validations in the frontend
- Filtering and searching functionality
- Error handling in the UI

## Running the Tests

### Backend Tests

```bash
# Run all services tests
python manage.py test services

# Run specific test file
python manage.py test services.test_integration
```

### End-to-End Tests

```bash
# Run the services E2E tests
cd frontend
npm run cypress:run -- --spec "cypress/e2e/services.cy.js"
```

### Contract Tests

```bash
# Run the services contract tests
python manage.py test services.test_pact_provider
```

## Test Coverage Matrix

| Functionality                           | Unit Tests | Integration Tests | API Tests | E2E Tests | Contract Tests |
|----------------------------------------|:----------:|:-----------------:|:---------:|:---------:|:--------------:|
| Basic CRUD operations                   |     ✅     |        ✅         |    ✅     |    ✅     |       ✅       |
| Filtering and searching                 |     -      |        -          |    ✅     |    ✅     |       ✅       |
| Charge type management                  |     ✅     |        -          |    ✅     |    ✅     |       ✅       |
| Name uniqueness validation              |     ✅     |        -          |    ✅     |    ✅     |       -        |
| Integration with Customer Services      |     -      |        ✅         |    -      |    ✅     |       -        |
| Deletion prevention with dependencies   |     -      |        ✅         |    ✅     |    -      |       -        |
| UI form validation                      |     -      |        -          |    -      |    ✅     |       -        |

## Test Data Strategy

1. **Unit Tests**: Uses isolated test data created specifically for each test case
2. **Integration Tests**: Creates related records across multiple models to test interactions
3. **API Tests**: Uses test client with authentication and request/response validation
4. **E2E Tests**: Uses either mock data or creates real data through the UI
5. **Contract Tests**: Uses predefined provider states to ensure consistent testing

## Best Practices

1. **Isolation**: Keep tests isolated to avoid test interference
2. **Completeness**: Test both happy paths and error cases
3. **Performance**: Optimize test setup with `setUpTestData` for class-level fixtures
4. **Readability**: Keep tests focused and well-documented
5. **Maintenance**: Update tests when model changes occur

## Common Test Scenarios

1. Creating a new service with various charge types
2. Attempting to create a service with a duplicate name
3. Updating an existing service
4. Attempting to delete a service that has customer service assignments
5. Testing filtering and searching functionality
6. Verifying charge type options are available