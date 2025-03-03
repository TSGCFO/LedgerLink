# Shipping Module Testing Documentation

This document outlines the testing strategy and implementation for the LedgerLink shipping module, which includes both Canadian (CAD) and US shipping functionality.

## Testing Coverage

The shipping module testing includes several layers:

1. **Model Tests**: Unit tests for data models
2. **API Tests**: Integration tests for API endpoints
3. **Serializer Tests**: Tests for data validation and business logic
4. **End-to-End Tests**: Cypress tests for UI interactions
5. **Bulk Operations Tests**: Tests for importing shipping data

## Test Files

### Django Backend Tests

- `shipping/test_models.py` - Tests for CADShipping and USShipping models
- `shipping/test_apis.py` - Tests for shipping API endpoints, filtering, and special actions
- `shipping/test_serializers.py` - Tests for data validation, calculated fields, and error handling

### Cypress E2E Tests

- `cypress/e2e/shipping.cy.js` - End-to-end tests for shipping UI
- `cypress/support/shipping-commands.js` - Custom Cypress commands for shipping operations
- `cypress/fixtures/cad_shipping_sample.csv` - Sample data for CAD shipping imports
- `cypress/fixtures/us_shipping_sample.csv` - Sample data for US shipping imports

## Running Tests

### Django Tests

Run all shipping tests:

```bash
python manage.py test shipping
```

Run specific test module:

```bash
python manage.py test shipping.test_models
python manage.py test shipping.test_apis
python manage.py test shipping.test_serializers
```

### Cypress Tests

Run all Cypress tests:

```bash
npx cypress run
```

Run only shipping tests:

```bash
npx cypress run --spec "cypress/e2e/shipping.cy.js"
```

## Test Coverage

The shipping tests cover:

### Model Tests

- Creation and validation of shipping records
- Unique constraints (one shipping record per order)
- Relationships with orders and customers
- Field validation and data types

### API Tests

- CRUD operations for shipping records
- Filtering by customer, order, carrier, status
- Search functionality
- Special endpoints (carriers list, status list)
- Response structure and error handling

### Serializer Tests

- Data validation rules
- Calculated fields (total_tax, total_charges, delivery_days)
- Error messages for validation failures
- Handling of null/empty values

### E2E Tests

- Shipping listing page display and filtering
- Creating new shipping records
- Editing existing shipping records
- Deleting shipping records
- Shipping analytics and reporting
- Bulk import operations

## Integration with Bulk Operations

Shipping records can be bulk imported using the bulk operations module. The tests include:

- Importing shipping records from CSV files
- Validation of imported data
- Error handling for invalid data

## Test Data

Test data is generated using:

- Test factories (`CADShippingFactory` and `USShippingFactory` in `test_utils/factories.py`)
- CSV fixtures for bulk import testing
- Custom Cypress commands for E2E test data setup

## Testing Strategy

The testing follows a pyramid approach:

1. Unit tests for models and serializers provide fast, isolated testing of business logic
2. API tests verify the correctness of endpoints and data flow
3. E2E tests ensure the entire system works together correctly

This multi-layered approach provides confidence in both the individual components and the integrated system.