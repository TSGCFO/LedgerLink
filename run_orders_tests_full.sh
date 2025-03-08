#!/bin/bash
set -e

# Script to run LedgerLink Orders app comprehensive tests with Docker and PostgreSQL

echo "=== Running LedgerLink Orders Comprehensive Tests with PostgreSQL ==="

# Stop any existing test containers
docker compose -f docker-compose.test.yml down

# Build and start test containers
docker compose -f docker-compose.test.yml up --build -d db

# Wait a moment for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run minimal tests that don't depend on database schema
echo "Running minimal schema verification tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test \
  /bin/bash -c 'echo "Running minimal tests that do not depend on materialized views" && \
                python -c "from orders.minimal_test import *; import unittest; unittest.main(argv=[\"first-arg-is-ignored\", \"MinimalTest\"])"'

# Get minimal test exit code
MIN_EXIT_CODE=$?

# Create a simple script to directly check if the is_active field exists in the database
echo "Checking database schema for is_active field..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test \
  /bin/bash -c 'python -c "
import psycopg2
from django.conf import settings

# Connect to the database directly
conn = psycopg2.connect(
    host=settings.DATABASES[\"default\"][\"HOST\"],
    dbname=settings.DATABASES[\"default\"][\"NAME\"],
    user=settings.DATABASES[\"default\"][\"USER\"],
    password=settings.DATABASES[\"default\"][\"PASSWORD\"],
    port=settings.DATABASES[\"default\"][\"PORT\"]
)

cursor = conn.cursor()

# Check if the customers_customer table exists
cursor.execute(\"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)\", (\"customers_customer\",))
table_exists = cursor.fetchone()[0]

if not table_exists:
    print(\"\\nERROR: customers_customer table does not exist\")
    exit(1)

# Check for the is_active column
cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name=%s\", (\"customers_customer\",))
columns = [row[0] for row in cursor.fetchall()]

print(f\"\\nColumns in customers_customer table: {columns}\")

if \"is_active\" in columns:
    print(\"\\nSUCCESS: is_active field exists in customers_customer table\")
    exit(0)
else:
    print(\"\\nERROR: is_active field does not exist in customers_customer table\")
    exit(1)
"'

# Get schema check exit code
SCHEMA_CHECK=$?

# If basic checks pass, run the comprehensive tests
if [ $MIN_EXIT_CODE -eq 0 ] && [ $SCHEMA_CHECK -eq 0 ]; then
    echo "=== Running comprehensive tests ==="
    docker compose -f docker-compose.test.yml run --rm \
      -e SKIP_MATERIALIZED_VIEWS=True \
      test python -m pytest orders/tests/functional/ -v
    
    # Get full test exit code
    FULL_TEST_CODE=$?
    
    if [ $FULL_TEST_CODE -eq 0 ]; then
        echo "=== All comprehensive tests passed! ==="
    else
        echo "=== Some comprehensive tests failed with exit code: $FULL_TEST_CODE ==="
    fi
fi

# Stop the containers
echo "Stopping test containers..."
docker compose -f docker-compose.test.yml down

# Display results
if [ $MIN_EXIT_CODE -eq 0 ]; then
    echo "=== Minimal tests passed! ==="
    
    if [ $SCHEMA_CHECK -eq 0 ]; then
        echo "=== Schema check passed: is_active field exists! ==="
        echo "=== Tests are working with the correct database schema ==="
        exit 0
    else
        echo "=== Schema check failed: is_active field missing ==="
        echo "=== This will cause comprehensive tests to fail ==="
        exit 1
    fi
else
    echo "=== Minimal tests failed with exit code: $MIN_EXIT_CODE ==="
    exit 1
fi