# Inserts Module Testing Documentation

This document outlines the testing approach and coverage for the Inserts module in the LedgerLink application.

## Test Structure

The tests for the Inserts module follow the testing pyramid approach:

1. **Unit Tests**: Testing individual components (models, serializers)
2. **Integration Tests**: Testing components working together
3. **API Tests**: Testing API endpoints and authentication

## Test Coverage

### Model Tests

#### Insert Model
- ✅ Test object creation with valid data
- ✅ Test string representation
- ✅ Test auto timestamps (created_at, updated_at)
- ✅ Test cascading delete from Customer

### Serializer Tests

#### InsertSerializer
- ✅ Test serialization with valid data
- ✅ Test validation of required fields
- ✅ Test validation of insert quantity (positive values only)
- ✅ Test SKU uniqueness per customer
- ✅ Test SKU uppercase conversion

### API Tests

#### Insert API
- ✅ Test authentication requirements
- ✅ Test listing all inserts (GET)
- ✅ Test creating a new insert (POST)
- ✅ Test retrieving a specific insert (GET detail)
- ✅ Test updating an insert (PUT)
- ✅ Test deleting an insert (DELETE)
- ✅ Test filtering by customer
- ✅ Test search functionality
- ✅ Test quantity filtering
- ✅ Test update_quantity custom action
  - ✅ Adding to quantity
  - ✅ Subtracting from quantity
  - ✅ Error handling for invalid operations
  - ✅ Error handling for insufficient quantity
- ✅ Test stats custom action

## Covered Functionality

The tests cover all key functionality of the Inserts module:
- Basic CRUD operations
- Data validation rules
- Search and filtering
- Custom API actions
- Authentication and permissions
- Integration with Customer model
- Error handling
- Response format

## Running the Tests

To run the Inserts module tests:

```bash
# Run all Inserts tests
python manage.py test inserts

# Run specific test class
python manage.py test inserts.tests.InsertModelTests

# Run specific test method
python manage.py test inserts.tests.InsertModelTests.test_create_insert
```

## Test Design Principles

1. **Isolation**: Each test is isolated and doesn't depend on the state from previous tests
2. **Completeness**: Tests cover both positive cases (expected behavior) and negative cases (error handling)
3. **Clarity**: Test names and docstrings clearly describe what is being tested
4. **Performance**: Tests are optimized to run quickly

## Test Data

The tests use minimal test data created directly in the tests, following the testing pyramid principles:
- Customer objects created for context
- Insert objects created with test data
- Various edge cases tested (empty fields, invalid quantities, etc.)

## Future Improvements

Potential areas for test enhancement:

1. Add factory-based test data generation
2. Add performance tests for bulk insert operations
3. Add more extensive contract tests for API endpoints
4. Test integration with Orders module (if applicable)
5. Add test coverage for edge cases in search functionality