# Testing Strategy for LedgerLink with SQLite vs PostgreSQL

## Overview of the Issue

The LedgerLink application is designed to work with PostgreSQL and uses several PostgreSQL-specific features:

1. **Materialized Views**: The application extensively uses PostgreSQL materialized views, particularly in the orders app with migrations like `0002_create_materialized_sku_view.py`.

2. **PostgreSQL-specific SQL**: Many migrations contain PostgreSQL-specific SQL commands like:
   - `CREATE MATERIALIZED VIEW`
   - `REFRESH MATERIALIZED VIEW`
   - `CREATE OR REPLACE FUNCTION`
   - PostgreSQL-specific indices and triggers

3. **Migration Dependencies**: There are complex migration dependencies across the apps, particularly with the orders, products, and billing apps.

## Challenges with SQLite for Testing

Using SQLite for tests creates several challenges:

1. **Incompatible SQL**: SQLite doesn't support materialized views, many of the functions, and other PostgreSQL-specific features.

2. **Migration Graph Issues**: Since the migration dependencies can't be satisfied in SQLite, it breaks the migration graph integrity.

3. **Feature Incompatibility**: Certain features that work in PostgreSQL (like case-sensitive searches, JSON indexing, etc.) behave differently in SQLite.

## Recommended Testing Approaches

### Option 1: Use PostgreSQL for Testing (Recommended)

The most reliable approach is to use PostgreSQL for testing. This ensures test conditions match production:

```python
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ledgerlink_test',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

You would need a PostgreSQL instance available during CI/CD and local testing.

### Option 2: Selective Migration Testing with SQLite

If PostgreSQL is not available, consider:

1. **Mock Migrations**: Create a simplified version of the migrations without PostgreSQL-specific features.

2. **Custom Test Runners**: Use a custom test runner that skips problematic migrations.

3. **Database Fixture Based Testing**: Pre-create database schemas and load them as fixtures.

### Option 3: Bypass Migrations Entirely with Django's Test Runner

As a last resort, you can bypass migrations:

```python
# settings/test.py
TEST_RUNNER = 'your_app.test.runners.NoMigrationTestRunner'

class NoMigrationTestRunner(django.test.runner.DiscoverRunner):
    def setup_databases(self, **kwargs):
        # Create all tables directly with schema_editor
        pass
```

## Current Test Implementation

Our current test implementation follows Option 2, where we:

1. **Mock Migrations**: Created simplified versions of problematic migrations
2. **Disable Certain Migrations**: Used MIGRATION_MODULES to disable specific migrations
3. **Custom Fixtures**: Set up necessary test data in fixtures

## Future Improvements

For more robust testing, consider:

1. **Docker-based PostgreSQL**: Set up a Docker container with PostgreSQL for local and CI testing
2. **Cleaner Migration Structure**: Refactor migrations to separate PostgreSQL-specific operations
3. **Improved Test Isolation**: Create test-specific models that don't rely on PostgreSQL features

## Recommendations for the Product App Tests

For the Products app tests, we need to:

1. Use a full test database that includes all related models
2. Either use PostgreSQL directly or create mock objects for dependencies
3. Consider focusing on unit tests that don't require extensive database setup

## PostgreSQL vs. SQLite Feature Matrix

| Feature | PostgreSQL | SQLite | Impact on Testing |
|---------|------------|--------|-------------------|
| Materialized Views | Yes | No | Critical - breaks migrations |
| JSON Operations | Advanced | Basic | Moderate - some tests will fail |
| Case Sensitivity | Configurable | Varies | Minor - search tests need adjustment |
| Foreign Key Constraints | Yes | Optional | Moderate - integrity tests might fail |
| Concurrent Access | Yes | Limited | Minor for testing |
| Full-Text Search | Yes | No | Significant for search features |