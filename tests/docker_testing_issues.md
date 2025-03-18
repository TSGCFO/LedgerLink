# Docker Testing Environment Issues

## Overview

While implementing comprehensive tests for the LedgerLink application, we encountered issues with the Docker testing environment. This document outlines the issues and proposed solutions for future reference.

## Issues Encountered

1. **Database Connection Issues**: 
   - When trying to run tests directly with Django, we encountered database connection issues:
   - `database "test_postgres" already exists` when creating the test database
   - `relation "products_product" does not exist` suggesting migration issues

2. **psycopg2 Compatibility Issues**:
   - The version of psycopg2 (2.8.4) specified in requirements.txt is not compatible with Python 3.12
   - When attempting to use Python 3.11, we encountered compilation errors with psycopg2
   - Specifically, the `Py_TYPE()` macro cannot be used on the left side of assignments in newer Python versions

3. **Docker Credential Issues**:
   - When trying to use Docker to run tests, we encountered credential issues:
   - `error getting credentials - err: exec: "docker-credential-desktop.exe": executable file not found in $PATH`
   - This suggests Windows Docker Desktop credential helpers are being referenced in a Linux environment

## Attempted Solutions

1. **For psycopg2 Issues**:
   - Changed from Python 3.12 to Python 3.11 in Dockerfile.test
   - Changed from psycopg2-binary to psycopg2 in requirements.txt
   - Attempted to patch the psycopg2 source code to replace `Py_TYPE(x) = y` with `Py_SET_TYPE(x, y)`
   - Attempted to use a pre-built wheel for psycopg2 (version 2.8.6) that is compatible with Python 3.11

2. **For Docker Credential Issues**:
   - Tried clearing Docker credential settings with `echo '{"credsStore":""}' > $HOME/.docker/config.json`
   - Tried running Docker with different options to bypass credential helpers

## Recommended Solutions

1. **Update psycopg2 Version**:
   - The most straightforward solution is to update to psycopg2-binary 2.9.x in requirements.txt
   - This version is compatible with Python 3.11 and 3.12
   - Example: `psycopg2-binary==2.9.9`

2. **Fix Docker Configuration**:
   - Use a CI/CD environment without Docker Desktop credential helpers
   - Or configure Docker to use appropriate credential helpers for the environment

3. **Alternative Testing Environment**:
   - Consider using GitHub Actions or another CI/CD solution for testing
   - These environments often have pre-configured Docker and database settings

4. **SQLite for Testing**:
   - As suggested in the testing documentation, configure Django to use SQLite for tests
   - This avoids PostgreSQL connection and migration issues during testing
   - Example configuration in settings.py:

```python
import sys

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
```

## Implemented Solution: TestContainers

After evaluating various options, we have implemented TestContainers as the solution for our testing environment issues. TestContainers addresses the problems we encountered in the following ways:

1. **Resolves Database Connection Issues**:
   - TestContainers creates a fresh PostgreSQL container for each test session
   - No conflicts with existing databases or connections
   - Automatic port assignment prevents conflicts

2. **Fixes psycopg2 Compatibility Issues**:
   - TestContainers handles database connection setup internally
   - Compatible with any Python version (3.11, 3.12+)
   - No need for manual psycopg2 configuration

3. **Eliminates Docker Credential Issues**:
   - TestContainers uses the local Docker daemon without credential helpers
   - Simplified container management with programmatic API
   - No dependency on Docker Compose or Docker Desktop features

## Implementation Details

1. **Implementation Location**:
   - Primary implementation in `/LedgerLink/conftest.py`
   - Verification tests in `/materials/tests/test_testcontainers.py`
   - Documentation in `/tests/testcontainers.md`

2. **How to Use**:
   - Run `./run_testcontainers_tests.sh` to execute tests with TestContainers
   - Or set `USE_TESTCONTAINERS=True` environment variable with pytest

3. **Backward Compatibility**:
   - Existing Docker setup (Dockerfile.test, docker-compose.test.yml) still available
   - Tests can run with SQLite, traditional Docker, or TestContainers

## Next Steps

1. Update remaining test configurations:
   - Update psycopg2 to version 2.9.x in requirements.txt for compatibility
   - Add TestContainers to CI/CD pipeline configurations

2. Enhance TestContainers setup:
   - Add support for additional container types (Redis, etc.) if needed
   - Create specialized fixtures for different test scenarios

3. Complete documentation:
   - Document TestContainers setup in CLAUDE.md for future reference (completed)
   - Update testing guides to recommend TestContainers approach