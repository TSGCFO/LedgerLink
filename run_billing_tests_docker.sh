#!/bin/bash
set -e

# Script to run LedgerLink Billing app tests directly in Docker without the wait_for_db command
echo "=== Running LedgerLink Billing Tests in Docker ==="

# Stop any existing test containers and ensure clean environment
docker compose -f docker-compose.test.yml down -v

# Start the database and wait for it manually
docker compose -f docker-compose.test.yml up -d db

# Wait for PostgreSQL to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 10  # Simple sleep-based wait

# Run calculator tests from reorganized structure
echo "Running calculator tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "sleep 5 && python manage.py migrate --noinput && python -m pytest billing/tests/test_calculator/ -v"

# Run tier tests from reorganized structure
echo "Running tier tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "python -m pytest billing/tests/test_tiers/ -v"

# Get the exit code
DIRECT_TESTS=$?

if [ $DIRECT_TESTS -ne 0 ]; then
    echo "=== Direct tests failed with exit code: $DIRECT_TESTS ==="
    docker compose -f docker-compose.test.yml down -v
    exit $DIRECT_TESTS
fi

# Run tests from the tests/ directory
echo "Running tests in the tests/ directory..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "python -m pytest billing/tests/ -v"

# Get the exit code
ALL_TESTS=$?

# Stop all containers
echo "Stopping test containers..."
docker compose -f docker-compose.test.yml down -v

# Display final results
echo "=== Billing Test Results ==="
echo "Direct tests: ${DIRECT_TESTS}"
echo "All tests: ${ALL_TESTS}"

# Set final exit code
if [ $DIRECT_TESTS -eq 0 ] && [ $ALL_TESTS -eq 0 ]; then
    echo "✅ All Billing tests passed!"
    exit 0
else
    echo "❌ Some Billing tests failed"
    exit 1
fi