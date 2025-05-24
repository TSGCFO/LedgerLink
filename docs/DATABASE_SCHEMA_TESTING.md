# LedgerLink Database Schema Testing Guide

This guide explains the approach to handling database schema testing in the LedgerLink project, especially regarding migrations and schema verification.

## Database Schema Management

### Understanding the Issues

One of the most common causes of test failures is misalignment between model definitions and database schema. This can happen when:

1. Model fields are added or changed, but migrations aren't created
2. Migrations exist but aren't applied properly in the test environment
3. Test environment uses a different approach to create tables than production

### Our Solution

We've implemented a comprehensive approach to handle these issues:

1. **Migration-Based Schema Creation**: We now ensure that all environments (Docker, TestContainers, and local) apply migrations correctly.

2. **Schema Verification**: We've added utilities to verify schema correctness before tests run.

3. **Clear Error Messages**: When schema issues are detected, specific diagnostics are provided.

4. **Safe Fallbacks**: Tests that don't depend on schema can still run even if schema issues exist.

## Schema Verification Utilities

We've added utilities in `tests/utils/schema_verification.py` to help with schema verification:

### Functions

- `verify_field_exists(model_class, field_name)`: Check if a specific field exists
- `verify_model_schema(model_class, required_fields=None)`: Verify all or specific fields for a model
- `verify_app_schema(app_label, required_models=None)`: Verify all or specific models in an app
- `verify_critical_models()`: Verify schema for the most critical models

### Usage Examples

#### Checking a Specific Field

```python
from tests.utils import verify_field_exists
from customers.models import Customer

# Check if is_active field exists
success, message = verify_field_exists(Customer, 'is_active')
if not success:
    print(f"Schema issue: {message}")
```

#### Verifying an Entire Model

```python
from tests.utils import verify_model_schema
from orders.models import Order

# Check all fields in the Order model
success, messages = verify_model_schema(Order)
for message in messages:
    print(message)
```

#### Checking All Critical Models

```python
from tests.utils import verify_critical_models

# Verify all critical models
success, results = verify_critical_models()
for app, models in results.items():
    print(f"App: {app}")
    for model, data in models.items():
        print(f"  Model: {model} - {'✅' if data['success'] else '❌'}")
        for msg in data.get('messages', []):
            print(f"    {msg}")
```

### Using in Tests

You can use these utilities in your test classes:

```python
import pytest
from tests.utils import verify_field_exists
from customers.models import Customer

@pytest.fixture(scope='session', autouse=True)
def verify_customer_schema():
    """Verify the Customer model schema before running tests."""
    success, message = verify_field_exists(Customer, 'is_active')
    if not success:
        pytest.fail(f"Schema verification failed: {message}")
    return True
```

## Best Practices for Model and Migration Changes

When making changes to models, follow these guidelines to maintain test integrity:

1. **Always create migrations after model changes**:
   ```bash
   python manage.py makemigrations
   ```

2. **Check migration quality**:
   ```bash
   python manage.py showmigrations
   python manage.py sqlmigrate app_name migration_number
   ```

3. **Test migrations before committing**:
   ```bash
   python manage.py migrate
   ```

4. **Add schema verification in tests**:
   ```python
   from tests.utils import verify_field_exists
   
   def test_something():
       # Verify schema before test
       success, message = verify_field_exists(YourModel, 'your_field')
       assert success, message
       
       # Test code...
   ```

## Test Environment Setup

### Docker-Based Testing

Our Docker-based test environment now applies migrations properly:

```bash
# Run all tests in Docker
./run_docker_tests.sh

# Run tests for a specific app
./run_orders_tests.sh
./run_customers_tests.sh
# ... etc
```

The Docker setup includes:
- Automatic migration application
- Schema verification before tests
- Fallback to minimal tests if schema issues exist

### TestContainers-Based Testing

For local development, TestContainers provides isolated PostgreSQL instances:

```bash
# Enable TestContainers
USE_TESTCONTAINERS=True python -m pytest

# Run specific app tests with TestContainers
USE_TESTCONTAINERS=True python -m pytest orders/
```

The TestContainers setup includes:
- Dedicated PostgreSQL container per test session
- Proper migration application
- Schema verification

### Standard Django Testing

For standard Django tests, we've improved migration handling:

```bash
# Run with pytest
python -m pytest

# Run with Django test runner
python manage.py test
```

## Troubleshooting Schema Issues

### Common Issues

1. **"Field X not found in table Y"**:
   - Check if you've created and applied migrations for the field
   - Ensure the test environment is applying migrations

2. **Test passes in Docker but fails locally**:
   - Consider using TestContainers: `USE_TESTCONTAINERS=True python -m pytest`
   - Ensure your local database has all migrations applied

3. **Migration conflicts**:
   - Use `python manage.py makemigrations --merge` to resolve conflicts
   - Consider resetting your test database if needed

### Diagnostic Commands

```bash
# Show all migrations
python manage.py showmigrations

# Show SQL for a migration
python manage.py sqlmigrate app_name migration_number

# Verify schema
python -c "from tests.utils import verify_critical_models; success, results = verify_critical_models(); print(results)"

# Check table schema directly
python -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name=%s', ['customers_customer']); print([row[0] for row in cursor.fetchall()])"
```

## Implementation Details

### Changes Made

1. **Modified conftest.py**: Changed from direct table creation to proper migration application

2. **Added schema verification utilities**: Created `tests/utils/schema_verification.py`

3. **Updated run_orders_tests.sh**: Added schema verification steps

4. **Added app-specific conftest.py**: Created `orders/tests/conftest.py` with schema verification

### Technical Details

#### Migration Executor

We're using Django's migration executor to apply migrations in the test environment:

```python
from django.db.migrations.executor import MigrationExecutor

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
executor.migrate(executor.loader.graph.leaf_nodes())
```

#### Schema Verification

We're using SQL queries to verify schema:

```python
with connection.cursor() as cursor:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", [table_name])
    columns = [row[0] for row in cursor.fetchall()]
```

## Conclusion

The schema verification approach ensures that:

1. Tests fail fast when schema issues exist
2. Clear diagnostic information is provided
3. Migrations are applied consistently
4. Test integrity is maintained

By following the guidelines in this document, you can avoid common schema-related test failures and maintain a robust test suite.
