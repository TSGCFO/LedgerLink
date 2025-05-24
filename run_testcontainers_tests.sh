#!/bin/bash
set -e

echo "Running tests using TestContainers..."
echo "This script will use TestContainers to create and manage PostgreSQL containers for testing."
# Setup a virtual environment if needed:
# python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

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
echo "Running Materials TestContainers tests..."
python -m pytest materials/tests/test_testcontainers.py -v --no-header --no-summary

echo "Running Orders TestContainers tests..."
python -m pytest orders/tests/test_testcontainers.py -v --no-header --no-summary

echo "Running Orders materialized view tests with TestContainers..."
SKIP_MATERIALIZED_VIEWS=False python -m pytest orders/tests/test_materialized_views.py -v --no-header --no-summary

# If you want to run a specific test:
# python -m pytest orders/tests/test_testcontainers.py::TestContainersOrdersTest::test_postgresql_connection -v

# If you want to run all tests:
# python -m pytest

echo "Tests completed."