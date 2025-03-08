# Orders App Testing Guide

## Overview

The Orders app contains comprehensive tests covering:
- Models (Order, OrderSKUView)
- Serializers
- Views (ViewSets)
- Integration with other apps
- Materialized views

## Test Structure

```
orders/
├── tests/
│   ├── __init__.py
│   ├── factories.py
│   ├── mock_ordersku_view.py
│   ├── test_models/
│   │   ├── test_order_model.py
│   │   └── test_ordersku_view.py
│   ├── test_serializers/
│   │   └── test_order_serializer.py
│   └── test_views/
│       └── test_order_viewset.py
├── test_direct.py
├── test_direct_db.py  
├── test_pact_provider.py
├── conftest.py
├── minimal_test.py
└── basic_test.py
```

## Running Tests

### Full Test Suite
```bash
./run_orders_tests.sh
```

This will:
1. Set up the test database with proper schema
2. Create required tables and materialized views
3. Run all orders app tests

### Direct DB Tests Only
```bash
./run_direct_test.sh
```

### Basic Functionality Tests
```bash
./run_basic_test.sh
```

## Special Considerations

### Materialized Views
The OrderSKUView model relies on a materialized view called `orders_sku_view`. Tests that involve this view:

1. Usually use `@pytest.mark.skipif('should_skip_materialized_view_tests()')` to avoid running when the view isn't available
2. Can use the MockOrderSKUView implementation for testing without the actual database view

When the environment variable `SKIP_MATERIALIZED_VIEWS=True` is set, these tests are skipped.

### Database Dependencies
Orders tests require several tables to be present:
- `orders_order` - The main orders table
- `customers_customer` - For customer relationships
- `shipping_cadshipping` and `shipping_usshipping` - For integration tests
- `billing_billingreport` and `billing_billingreportdetail` - For integrated billing features

### Transaction IDs
Order objects use transaction_id as their primary key. In production, these are generated from timestamps, but in tests we use smaller random integers to avoid PostgreSQL INT limit issues.

## Common Test Issues and Solutions

### "Database access not allowed"
This usually happens when a test module doesn't properly set `pytestmark = pytest.mark.django_db`.

### Missing Views
If you're getting errors about `orders_sku_view` not existing:
1. Make sure you're running tests with `./run_orders_tests.sh` which sets up the view
2. Or set `SKIP_MATERIALIZED_VIEWS=True` to skip view-dependent tests

### Cascade Delete Issues
Tests involving deletion of related objects can fail if the database schema isn't properly set up. The run_orders_tests.sh script sets up all necessary tables with correct foreign key constraints.

## Adding New Tests

When adding new tests:

1. **Models**: Add to `tests/test_models/`
2. **Serializers**: Add to `tests/test_serializers/`
3. **Views**: Add to `tests/test_views/`
4. **For view-dependent tests**: Use `@pytest.mark.skipif('should_skip_materialized_view_tests()')` when appropriate

Always run the full test suite after adding new tests to ensure no regressions.

## Test Coverage

Current test coverage: ~90%

The Orders app testing is quite comprehensive, with special attention to:
- Order lifecycle (status transitions)
- SKU quantity handling 
- Materialized view functionality
- Customer relationship cascade behaviors
- Transaction ID generation and validation
- Serializer validation logic