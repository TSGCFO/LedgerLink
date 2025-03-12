# Customer Services Testing Guide

This document outlines the testing approach for the Customer Services module in LedgerLink.

## Overview

The Customer Services module is a critical component that links customers with available services. It serves as the foundation for the rules system, which determines pricing and billing for customer services.

## Test Coverage

The Customer Services module has comprehensive test coverage across multiple levels:

### 1. Model and Serializer Tests

Located in `customer_services/tests.py`, these tests verify:

- Customer service model functionality
- Field validations and constraints
- Serializer functionality and validation
- Model methods like `get_skus()` and `get_sku_list()`
- Unique constraint enforcement (`customer` + `service` must be unique)

### 2. API Endpoint Tests

These tests ensure the API endpoints function correctly:

- List endpoint with filtering and searching
- Detail endpoint for specific customer service
- Create endpoint with validation
- Update endpoint functionality
- Delete endpoint functionality
- Custom endpoints for managing SKUs (`add_skus` and `remove_skus`)

### 3. Integration Tests

Located in `customer_services/test_integration.py`, these tests verify:

- Integration with the Rules system (rule groups and rules)
- Cascade delete functionality with related models
- Relationships with Customers and Services modules
- Constraint validation across related models

### 4. Contract Tests

Located in `customer_services/test_pact_provider.py`, these tests ensure:

- API contracts are maintained between frontend and backend
- Response formats match frontend expectations
- All expected endpoints are available and functioning
- Provider states are properly set up for Pact verification

### 5. End-to-End Tests

Located in `frontend/cypress/e2e/customer_services.cy.js`, these tests verify:

- User interface for customer service management
- Full user flows from UI to database and back
- Form validations in the frontend
- Filtering and searching functionality
- SKU assignment operations
- Error handling in the UI

## Running the Tests

### Backend Tests

```bash
# Run all customer services tests
python manage.py test customer_services

# Run specific test file
python manage.py test customer_services.test_integration
```

### End-to-End Tests

```bash
# Run the customer services E2E tests
cd frontend
npm run cypress:run -- --spec "cypress/e2e/customer_services.cy.js"
```

### Contract Tests

```bash
# Run the customer services contract tests
python manage.py test customer_services.test_pact_provider
```

## Test Coverage Matrix

| Functionality                           | Unit Tests | Integration Tests | API Tests | E2E Tests | Contract Tests |
|----------------------------------------|:----------:|:-----------------:|:---------:|:---------:|:--------------:|
| Basic CRUD operations                   |     ✅     |        ✅         |    ✅     |    ✅     |       ✅       |
| Filtering and searching                 |     -      |        -          |    ✅     |    ✅     |       ✅       |
| Custom SKU operations                   |     ✅     |        -          |    ✅     |    ✅     |       -        |
| Validation rules                        |     ✅     |        ✅         |    ✅     |    ✅     |       -        |
| Integration with Rules system           |     -      |        ✅         |    -      |    ✅     |       -        |
| Cascade delete behavior                 |     -      |        ✅         |    -      |    -      |       -        |
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

1. Creating a customer service assignment
2. Updating pricing for a customer service
3. Deleting a customer service and verifying cascade delete behavior
4. Assigning SKUs to a customer service
5. Creating rules based on a customer service
6. Verifying unique constraint enforcement
7. Testing filtering and searching functionality