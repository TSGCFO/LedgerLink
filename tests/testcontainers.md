# Using TestContainers for LedgerLink Testing

## Overview

TestContainers is a testing library that allows you to create and manage Docker containers programmatically within your tests. This document explains how we've integrated TestContainers with LedgerLink to provide reliable, isolated database environments for testing.

## Benefits Over Traditional Docker Setup

1. **Isolated Testing Environment**: Each test session gets its own containerized database
2. **No Configuration Conflicts**: Avoids port conflicts and credential issues that plague shared Docker setups
3. **Automated Lifecycle Management**: Containers are automatically created, started, and cleaned up
4. **Works with Any Python Version**: Eliminates compatibility issues between Python and database drivers
5. **Compatible with CI/CD**: Same code works locally and in CI environments

## How It Works

1. When tests start, TestContainers automatically:
   - Pulls the PostgreSQL Docker image if needed
   - Creates a container with a clean database
   - Starts the container
   - Exposes port and connection information

2. Our Django test setup:
   - Configures Django to use the TestContainers database
   - Creates tables and schema objects
   - Runs tests against the containerized database

3. When tests complete:
   - Containers are automatically stopped and removed
   - Resources are cleaned up

## How To Use

### Running Tests with TestContainers

```bash
# Run tests using TestContainers
./run_testcontainers_tests.sh

# Or directly with pytest
USE_TESTCONTAINERS=True python -m pytest
```

### Verifying TestContainers Setup

We've created a specific test file to verify that TestContainers is working correctly:

```bash
# Run only the TestContainers verification tests
USE_TESTCONTAINERS=True python -m pytest materials/tests/test_testcontainers.py -v
```

### Disabling TestContainers

If you want to use a different database setup (like SQLite or a local PostgreSQL instance), you can disable TestContainers:

```bash
USE_TESTCONTAINERS=False python -m pytest
```

## Implementation Details

The TestContainers integration is primarily implemented in `/LedgerLink/conftest.py`, which:

1. Provides a `postgres_container` fixture that creates and manages the PostgreSQL container
2. Modifies the Django database settings to use the container's connection information
3. Ensures the database is properly set up with tables and materialized views

## Troubleshooting

### Common Issues

1. **Docker Not Running**: Ensure Docker is installed and running on your machine
2. **Port Conflicts**: TestContainers automatically finds available ports, but if you have many containers running, you might see conflicts
3. **Slow First Run**: The first time you run tests, Docker may need to download the PostgreSQL image

### Debugging

To see more detailed output from TestContainers:

```bash
TESTCONTAINERS_DEBUG=True USE_TESTCONTAINERS=True python -m pytest
```

## Best Practices

1. **Clean Test Data**: Each test should create its own test data and clean up afterward
2. **Keep Containers Lightweight**: Prefer using the default PostgreSQL image without additional customization
3. **Use Transactions**: Wrap tests in transactions to improve performance and isolation

## Next Steps

- Integrate more container types (Redis, Elasticsearch, etc.) for testing other components
- Add TestContainers support to CI/CD pipeline
- Create more specific database fixtures for different test scenarios