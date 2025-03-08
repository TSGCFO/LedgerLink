#!/bin/bash
set -e

# Script to run LedgerLink Billing app tests with proper integration to the main test framework

# Fix Docker credential issue
if [ ! -f ~/.docker/config.json ]; then
  echo "Setting up Docker configuration to avoid credential issues..."
  mkdir -p ~/.docker
  echo '{"credsStore":""}' > ~/.docker/config.json
fi

echo "=== Running LedgerLink Billing Tests with Full Integration ==="

# Function to clean Python cache files
clean_pycache() {
    echo "Cleaning Python cache files..."
    find billing -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Clean Python cache files locally first
clean_pycache

# Stop any existing test containers and ensure clean environment
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up --build -d db

# Wait for the database to initialize (increased for reliability)
echo "Waiting for PostgreSQL to initialize..."
sleep 10

# First run schema verification and prepare database
echo "Verifying database schema and setting up required tables..."
docker compose -f docker-compose.test.yml run --rm \
  test bash -c "\
    python manage.py wait_for_db && \
    python manage.py migrate && \
    python -c \"from django.db import connection; print('Schema verification: Database setup complete!')\" \
  "

# Run direct tests in Docker
echo "Running direct unit tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "\
    python -m pytest billing/test_billing_calculator.py \
    billing/test_case_based_tiers.py \
    billing/test_services.py \
    billing/test_utils.py -v \
  "

# Get the exit code
DIRECT_TESTS=$?

if [ $DIRECT_TESTS -ne 0 ]; then
    echo "=== Direct tests failed with exit code: $DIRECT_TESTS ==="
    docker compose -f docker-compose.test.yml down
    exit $DIRECT_TESTS
fi

# Run model tests
echo "Running model tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "\
    python -m pytest billing/tests/test_models/ -v \
  "

# Get the exit code
MODEL_TESTS=$?

if [ $MODEL_TESTS -ne 0 ]; then
    echo "=== Model tests failed with exit code: $MODEL_TESTS ==="
    docker compose -f docker-compose.test.yml down
    exit $MODEL_TESTS
fi

# Run serializer tests
echo "Running serializer tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "\
    python -m pytest billing/tests/test_serializers/ -v \
  "

# Get the exit code
SERIALIZER_TESTS=$?

if [ $SERIALIZER_TESTS -ne 0 ]; then
    echo "=== Serializer tests failed with exit code: $SERIALIZER_TESTS ==="
    docker compose -f docker-compose.test.yml down
    exit $SERIALIZER_TESTS
fi

# Run view tests
echo "Running view tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "\
    python -m pytest billing/tests/test_views/ -v \
  "

# Get the exit code
VIEW_TESTS=$?

if [ $VIEW_TESTS -ne 0 ]; then
    echo "=== View tests failed with exit code: $VIEW_TESTS ==="
    docker compose -f docker-compose.test.yml down
    exit $VIEW_TESTS
fi

# Run integration tests
echo "Running integration tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test bash -c "\
    python -m pytest billing/tests/test_integration/ -v \
  "

# Get the exit code
INTEGRATION_TESTS=$?

# Stop all containers
echo "Stopping test containers..."
docker compose -f docker-compose.test.yml down -v

# Display final results
echo "=== Billing Test Results ==="
echo "Direct tests: ${DIRECT_TESTS}"
echo "Model tests: ${MODEL_TESTS}"
echo "Serializer tests: ${SERIALIZER_TESTS}"
echo "View tests: ${VIEW_TESTS}"
echo "Integration tests: ${INTEGRATION_TESTS}"

# Set final exit code
if [ $DIRECT_TESTS -eq 0 ] && [ $MODEL_TESTS -eq 0 ] && [ $SERIALIZER_TESTS -eq 0 ] && [ $VIEW_TESTS -eq 0 ] && [ $INTEGRATION_TESTS -eq 0 ]; then
    echo "✅ All Billing tests passed!"
    exit 0
else
    echo "❌ Some Billing tests failed"
    exit 1
fi