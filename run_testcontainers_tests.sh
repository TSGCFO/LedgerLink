#!/bin/bash
set -e

echo "Running tests using TestContainers..."
echo "This script will use TestContainers to create and manage PostgreSQL containers for testing."

# Set environment variable to ensure we use TestContainers
export USE_TESTCONTAINERS=True
# Disable pytest-django's django_db_setup fixture
export PYTEST_SKIP_DJANGO_DB_SETUP=True

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the tests with pytest and skip using the main conftest.py
echo "Running the tests..."
python -m pytest materials/tests/test_testcontainers.py -v --no-header --no-summary

# If you want to run a specific test:
# python -m pytest materials/tests/test_testcontainers.py::TestTestContainersSetup::test_postgresql_connection -v

# If you want to run all tests:
# python -m pytest

echo "Tests completed."