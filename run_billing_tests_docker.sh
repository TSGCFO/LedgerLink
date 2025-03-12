#!/bin/bash
set -e

# Script to run LedgerLink Billing app tests directly in Docker without the wait_for_db command
echo "=== Running LedgerLink Billing Tests in Docker ==="

# Check if we need to recreate the database from scratch
if [ "$1" == "--rebuild" ]; then
  echo "Rebuilding database from scratch..."
  docker compose -f docker-compose.test.yml down -v
else
  # Stop containers but preserve the volume
  docker compose -f docker-compose.test.yml down
fi

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

# Stop only test containers but keep database running
echo "Stopping test containers but keeping database..."
docker compose -f docker-compose.test.yml stop test

# Display final results
echo "=== Billing Test Results ==="
echo "Direct tests: ${DIRECT_TESTS}"
echo "All tests: ${ALL_TESTS}"

# Optionally stop database too
if [ "$2" == "--stop-all" ]; then
  echo "Stopping all containers but preserving volume..."
  docker compose -f docker-compose.test.yml down
fi

# Set final exit code
if [ $DIRECT_TESTS -eq 0 ] && [ $ALL_TESTS -eq 0 ]; then
    echo "✅ All Billing tests passed!"
    exit 0
else
    echo "❌ Some Billing tests failed"
    exit 1
fi