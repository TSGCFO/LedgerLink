#!/bin/bash
# Script to run all customer_services tests

# Start the PostgreSQL DB container
echo "Starting PostgreSQL container..."
docker-compose -f docker-compose.test.yml up --build -d db

# Wait for database to be ready
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run all test scripts
echo "=================================="
echo "Running customer_services tests..."
echo "=================================="

# Run model tests first
echo
echo "== Running Model Tests =="
docker-compose -f docker-compose.test.yml run --rm test python -m unittest customer_services/tests/test_models.py
MODEL_RESULT=$?

# Run integration tests 
echo
echo "== Running Integration Tests =="
docker-compose -f docker-compose.test.yml run --rm test python -m unittest customer_services/tests/test_integration.py
INTEGRATION_RESULT=$?

# Run contract tests
echo
echo "== Running Contract Tests =="
docker-compose -f docker-compose.test.yml run --rm test python -m unittest customer_services/tests/test_pact_provider.py
CONTRACT_RESULT=$?

# Run performance tests
echo
echo "== Running Performance Tests =="
docker-compose -f docker-compose.test.yml run --rm test python -m unittest customer_services/tests/test_performance.py
PERFORMANCE_RESULT=$?

# Stop containers
echo "Stopping containers..."
docker-compose -f docker-compose.test.yml down

# Report results
echo
echo "======= Test Results Summary ======="
echo "Model Tests: $([ $MODEL_RESULT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "Integration Tests: $([ $INTEGRATION_RESULT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "Contract Tests: $([ $CONTRACT_RESULT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "Performance Tests: $([ $PERFORMANCE_RESULT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo

# Overall result
if [ $MODEL_RESULT -eq 0 ] && [ $INTEGRATION_RESULT -eq 0 ] && [ $CONTRACT_RESULT -eq 0 ] && [ $PERFORMANCE_RESULT -eq 0 ]; then
  echo "All Tests: ✅ PASSED"
  exit 0
else
  echo "All Tests: ❌ FAILED"
  exit 1
fi