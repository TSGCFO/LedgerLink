#!/bin/bash
set -e

# Script to run LedgerLink Billing app tests with proper integration to the main test framework
# This fixed version addresses the module import issue

# Fix Docker credential issue
if [ ! -f ~/.docker/config.json ]; then
  echo "Setting up Docker configuration to avoid credential issues..."
  mkdir -p ~/.docker
  echo '{"credsStore":""}' > ~/.docker/config.json
fi

echo "=== Running LedgerLink Billing Tests with Fixed Structure ==="

# Function to clean Python cache files
clean_pycache() {
    echo "Cleaning Python cache files..."
    find ./billing -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Clean Python cache files first
clean_pycache

# Run the direct test files first (unit tests without database dependencies)
echo "Running direct unit tests..."
SKIP_MATERIALIZED_VIEWS=True python -m pytest billing/test_billing_calculator.py billing/test_case_based_tiers.py -v

# Get direct test exit code
DIRECT_TEST_CODE=$?

if [ $DIRECT_TEST_CODE -ne 0 ]; then
    echo "=== Direct tests failed with exit code: $DIRECT_TEST_CODE ==="
    exit $DIRECT_TEST_CODE
fi

# Run tests in the test_models directory
echo "Running billing model tests..."
SKIP_MATERIALIZED_VIEWS=True python -m pytest billing/tests/test_models/ -v

# Get model tests exit code
MODEL_TESTS_CODE=$?

if [ $MODEL_TESTS_CODE -ne 0 ]; then
    echo "=== Model tests failed with exit code: $MODEL_TESTS_CODE ==="
    exit $MODEL_TESTS_CODE
fi

# Run tests in the test_serializers directory
echo "Running billing serializer tests..."
SKIP_MATERIALIZED_VIEWS=True python -m pytest billing/tests/test_serializers/ -v

# Get serializer tests exit code
SERIALIZER_TESTS_CODE=$?

if [ $SERIALIZER_TESTS_CODE -ne 0 ]; then
    echo "=== Serializer tests failed with exit code: $SERIALIZER_TESTS_CODE ==="
    exit $SERIALIZER_TESTS_CODE
fi

# Run tests in the test_views directory
echo "Running billing view tests..."
SKIP_MATERIALIZED_VIEWS=True python -m pytest billing/tests/test_views/ -v

# Get view tests exit code
VIEW_TESTS_CODE=$?

if [ $VIEW_TESTS_CODE -ne 0 ]; then
    echo "=== View tests failed with exit code: $VIEW_TESTS_CODE ==="
    exit $VIEW_TESTS_CODE
fi

# Run tests in the test_integration directory
echo "Running billing integration tests..."
SKIP_MATERIALIZED_VIEWS=True python -m pytest billing/tests/test_integration/ -v

# Get integration tests exit code
INTEGRATION_TESTS_CODE=$?

# Display results
if [ $INTEGRATION_TESTS_CODE -eq 0 ]; then
    echo "=== All Billing tests passed! ==="
else
    echo "=== Billing integration tests failed with exit code: $INTEGRATION_TESTS_CODE ==="
fi

echo "=== Billing Test Summary ==="
echo "Direct tests exit code: $DIRECT_TEST_CODE"
echo "Model tests exit code: $MODEL_TESTS_CODE"
echo "Serializer tests exit code: $SERIALIZER_TESTS_CODE"
echo "View tests exit code: $VIEW_TESTS_CODE"
echo "Integration tests exit code: $INTEGRATION_TESTS_CODE"

# Return combined exit code - success only if all tests passed
if [ $DIRECT_TEST_CODE -eq 0 ] && [ $MODEL_TESTS_CODE -eq 0 ] && [ $SERIALIZER_TESTS_CODE -eq 0 ] && [ $VIEW_TESTS_CODE -eq 0 ] && [ $INTEGRATION_TESTS_CODE -eq 0 ]; then
    exit 0
else
    exit 1
fi