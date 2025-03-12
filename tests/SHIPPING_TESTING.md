# Shipping Module Testing Documentation

This document outlines the testing approach and coverage for the Shipping module in the LedgerLink application.

## Test Structure

The tests for the Shipping module follow the testing pyramid approach:

1. **Unit Tests**: Testing individual components (models, serializers)
2. **Integration Tests**: Testing components working together
3. **API Tests**: Testing API endpoints and authentication

## Test Coverage

### Model Tests

#### CADShipping Model
- ✅ Test object creation with valid data
- ✅ Test string representation
- ✅ Test cascade delete from Order
- ✅ Test relationships with Order and Customer

#### USShipping Model
- ✅ Test object creation with valid data
- ✅ Test string representation
- ✅ Test cascade delete from Order
- ✅ Test delivery date calculation
- ✅ Test status fields and defaults

### Serializer Tests

#### CADShippingSerializer
- ✅ Test serialization with expected fields
- ✅ Test total tax calculation
- ✅ Test total charges calculation
- ✅ Test validation of required shipping address fields

#### USShippingSerializer
- ✅ Test serialization with expected fields
- ✅ Test total charges calculation
- ✅ Test delivery days calculation
- ✅ Test validation of shipping address fields
- ✅ Test date validation (delivery/attempt date must be after ship date)

### API Tests

#### CADShipping API
- ✅ Test authentication requirements
- ✅ Test listing all shipping records
- ✅ Test filtering by customer
- ✅ Test filtering by carrier
- ✅ Test search functionality
- ✅ Test creating a new shipping record
- ✅ Test retrieving a specific shipping record
- ✅ Test updating a shipping record
- ✅ Test deleting a shipping record
- ✅ Test carriers custom action

#### USShipping API
- ✅ Test authentication requirements
- ✅ Test listing all shipping records
- ✅ Test filtering by customer
- ✅ Test filtering by status fields
- ✅ Test search functionality
- ✅ Test creating a new shipping record
- ✅ Test retrieving a specific shipping record
- ✅ Test updating a shipping record
- ✅ Test deleting a shipping record
- ✅ Test statuses custom action
- ✅ Test service_names custom action

## Covered Functionality

The tests cover all key functionality of the Shipping module:
- Model relationships and field validation
- Transaction-based shipping model with OneToOneField relationship
- Calculated fields (total_tax, total_charges, delivery_days)
- Date-based validations
- Address field validations
- API filtering, searching, and CRUD operations
- Custom actions for carriers, statuses, and service names

## Running the Tests

To run the Shipping module tests:

```bash
# Run all Shipping tests
python manage.py test shipping

# Run specific test class
python manage.py test shipping.tests.CADShippingModelTests

# Run specific test method
python manage.py test shipping.tests.CADShippingModelTests.test_create_cad_shipping
```

## Test Design Principles

1. **Isolation**: Each test is isolated and doesn't depend on the state from previous tests
2. **Completeness**: Tests cover both positive cases (expected behavior) and negative cases (error handling)
3. **Clarity**: Test names and docstrings clearly describe what is being tested
4. **Performance**: Tests are optimized to run quickly

## Test Data

The tests use minimal test data created directly in the tests, following the testing pyramid principles:
- Customer and Order objects created for context
- CADShipping and USShipping records with specific test data
- Date-based test data for delivery timing testing
- Various test data for filtering and search testing

## Future Improvements

Potential areas for test enhancement:

1. Add factories for shipping records using Factory Boy
2. Add more thorough integration tests with billing functionality
3. Add tests for edge cases in calculation methods
4. Expand filtering tests for date ranges
5. Test serialization of nested relationship data
6. Add performance tests for bulk shipping records