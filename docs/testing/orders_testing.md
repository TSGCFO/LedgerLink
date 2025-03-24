# Orders Module Testing Documentation

This document outlines the testing approach and coverage for the Orders module in the LedgerLink application.

## Test Structure

The tests for the Orders module follow the testing pyramid approach:

1. **Unit Tests**: Testing individual components (models, serializers, methods)
2. **Integration Tests**: Testing components working together
3. **API Tests**: Testing API endpoints and authentication

## Test Coverage

### Model Tests

#### Order Model
- ✅ Test object creation with valid data
- ✅ Test string representation
- ✅ Test status and priority choices
- ✅ Test default status and priority values
- ✅ Test SKU detail methods:
  - ✅ `get_sku_details()` - Retrieve detailed SKU information
  - ✅ `get_total_cases()` - Calculate total cases
  - ✅ `get_total_picks()` - Calculate total picks
  - ✅ `has_only_excluded_skus()` - Check for excluded SKUs
  - ✅ `get_case_summary()` - Get case and pick breakdown

### Serializer Tests

#### OrderSerializer
- ✅ Test serializer with valid data
- ✅ Test validation of required fields
- ✅ Test SKU quantity validation:
  - ✅ Valid SKU dictionary format
  - ✅ Invalid format (not a dictionary)
  - ✅ Invalid quantities (negative, zero)
- ✅ Test shipping address validation
- ✅ Test automatic calculation of `total_item_qty` and `line_items`
- ✅ Test status transition validation:
  - ✅ Valid transitions between consecutive statuses
  - ✅ Invalid transitions skipping statuses
  - ✅ Cannot change status of cancelled orders
- ✅ Test transaction_id generation

### API Tests

#### OrderViewSet
- ✅ Test authentication requirements
- ✅ Test listing all orders
- ✅ Test filtering by:
  - ✅ Customer
  - ✅ Status
  - ✅ Priority
- ✅ Test search functionality
- ✅ Test creating new orders
- ✅ Test retrieving a specific order
- ✅ Test updating orders with valid and invalid status transitions
- ✅ Test delete restrictions:
  - ✅ Can delete draft orders
  - ✅ Cannot delete orders with other statuses
- ✅ Test custom actions:
  - ✅ `cancel` action for cancelling orders
  - ✅ `status_counts` action for counting orders by status
  - ✅ `choices` action for getting available status/priority choices

## Covered Functionality

The tests cover all key functionality of the Orders module:
- Basic CRUD operations with validation
- Status transitions and restrictions
- Order deletion restrictions
- Custom methods for SKU and case/pick calculations
- Advanced filtering and search capabilities
- JSON field handling (SKU quantities)
- Custom API actions for special operations

## Running the Tests

To run the Orders module tests:

```bash
# Run all Orders tests
python manage.py test orders

# Run specific test class
python manage.py test orders.tests.OrderModelTests

# Run specific test method
python manage.py test orders.tests.OrderModelTests.test_create_order
```

## Test Design Principles

1. **Isolation**: Each test is isolated and doesn't depend on the state from previous tests
2. **Completeness**: Tests cover both positive cases (expected behavior) and negative cases (error handling)
3. **Clarity**: Test names and docstrings clearly describe what is being tested
4. **Performance**: Tests are optimized to run quickly

## Testing Approach for OrderSKUView

Since `OrderSKUView` is a database view (not managed by Django models), we've taken a special approach:

1. Created a `MockOrderSKUView` class to simulate the behavior of the view
2. Used monkeypatching to override the database access
3. Verified all methods that depend on the view without requiring database setup

This approach allows us to thoroughly test the functionality without complex database setup while ensuring the code behaves correctly with various SKU combinations.

## Future Improvements

Potential areas for test enhancement:

1. Add more extensive tests for pagination of order results
2. Implement performance tests for large order datasets
3. Test complex filtering scenarios combining multiple filters
4. Add tests for date range filtering
5. Test the `refresh_sku_view` management command
6. Create factory-based test data generation with Factory Boy