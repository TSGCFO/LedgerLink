# LedgerLink Testing Documentation

## Database Testing Challenges and Solutions

LedgerLink uses PostgreSQL-specific features like materialized views which create special considerations for testing:

1. **Testing Database Connectivity**
   - SQLite cannot be used for all tests since it doesn't support materialized views
   - PostgreSQL is required for complete integration testing

2. **Key Testing Issues**
   - "Database access not allowed" errors with pytest-django
   - Materialized view creation failures in test environment
   - TestContainers vs Docker test environment conflicts
   - Schema/migration dependencies that complicate testing

3. **Solutions Implemented**
   - Added `SKIP_MATERIALIZED_VIEWS=True` environment variable to bypass view creation
   - Created Docker-based test scripts for reliable database access
   - Added direct database tests that work independently of Django migrations
   - Created minimal test suite that verifies core functionality
   - Implemented proper test integration with project fixtures

## Test Integration Guidelines

We've solved the issue of tests running in isolation but failing when integrated with the project's test framework.

### Key Integration Solution Components:

1. **App-specific conftest.py Extensions**
   - Extend main project's fixtures rather than override them
   - Use both the main project's `django_db_setup` and your app-specific fixtures
   - Add schema verification to ensure critical fields (like `is_active`) exist
   - Respect environment variables set in the main project

2. **Test Class Pattern**
   - Use both `@pytest.mark.django_db` and Django's `TestCase`
   - Include explicit fixture usage with autouse fixtures
   - Test critical fields to verify schema is correct

3. **Database Access Control**
   - Use `django_db_blocker` correctly to unblock/restore database access
   - Import the `_django_db_helper` fixture from the main conftest.py
   - Use proper pytest markers for database access

## Testing Approaches

### Docker-Based Testing (Recommended)

```bash
# Run all tests in Docker 
./run_docker_tests.sh

# Run app-specific tests
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test python -m pytest app_name/tests/ -v

# Run direct DB tests (reliable)
./run_direct_test.sh

# Run Factory Boy tests (recommended)
./run_factory_test.sh
```

### TestContainers-Based Testing

```bash
# Run with TestContainers
USE_TESTCONTAINERS=True SKIP_MATERIALIZED_VIEWS=True python -m pytest
```

### Standard Django Tests

```bash
# Run Django tests
python manage.py test app_name
```

## Writing New Database Tests

When writing new tests that require database access:

1. **For pytest-based tests**:
   - Use `@pytest.mark.django_db` decorator
   - Set `pytestmark = pytest.mark.django_db(transaction=True)` at module level
   - Use proper fixtures for setup (see examples in `billing/tests/`)

2. **For TestCase-based tests**:
   - Extend `django.test.TestCase`
   - Use `setUp` for test data creation
   - Use `assertXXX` methods for assertions

3. **For direct database tests** (most reliable):
   - Use pure psycopg2 with unittest.TestCase
   - Set up schema manually
   - Create necessary test data in setUp
   - Example in `test_scripts/direct_db_test.py`

4. **For Factory Boy tests** (recommended):
   - Combines Django ORM with direct DB schema setup
   - Uses factories to create test data with proper relationships
   - Handles test isolation and clean setup/teardown
   - Example in `test_scripts/factory_test.py`

5. **Testing models with FK to materialized views**:
   - Skip these tests when `SKIP_MATERIALIZED_VIEWS=True`
   - Only run in Docker testing environment

## Test Structure Best Practices

Each app should have the following test files:

- `test_models.py` - Test model functionality
- `test_serializers.py` - Test serialization/deserialization
- `test_views.py` - Test API endpoints
- `test_integration.py` - Test interaction with other components
- `test_performance.py` - Test performance characteristics

## Current Status

- We've created a working direct database test for customer_services
- The established pattern of using Docker for database tests works reliably
- The `SKIP_MATERIALIZED_VIEWS=True` approach helps isolate materialized view issues
- TestContainers works in some environments but has configuration challenges
- Direct pytest-django approach has connection issues in some configurations
- Direct database tests with psycopg2 are the most reliable approach

Always run the tests in Docker for the most reliable results, especially when testing database functionality. For the most reliable tests, use the direct database testing approach with `run_direct_test.sh`.