#!/bin/bash
set -e

# Script to run all billing tests after fixing implementation issues
echo "=== Running All LedgerLink Billing Tests ==="

# Fix implementation issues first
echo "Fixing billing calculator implementation..."
python fix_billing_calculator.py

# Function to run tests in a directory
run_tests() {
    local test_dir=$1
    local test_name=$2
    
    echo "Running $test_name tests..."
    SKIP_MATERIALIZED_VIEWS=True python -m pytest $test_dir -v
    
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "=== $test_name tests failed with exit code: $exit_code ==="
        return $exit_code
    fi
    
    echo "$test_name tests passed successfully"
    return 0
}

# Run all test categories
run_tests "billing/tests/test_calculator/" "Calculator"
CALCULATOR_TESTS=$?

run_tests "billing/tests/test_models/" "Model"
MODEL_TESTS=$?

run_tests "billing/tests/test_serializers/" "Serializer"
SERIALIZER_TESTS=$?

run_tests "billing/tests/test_views/" "View"
VIEW_TESTS=$?

run_tests "billing/tests/test_rules/" "Rules" 
RULES_TESTS=$?

run_tests "billing/tests/test_tiers/" "Tier"
TIER_TESTS=$?

run_tests "billing/tests/test_integration/" "Integration"
INTEGRATION_TESTS=$?

run_tests "billing/tests/test_exporters/" "Exporter"
EXPORTER_TESTS=$?

run_tests "billing/tests/test_services/" "Service"
SERVICE_TESTS=$?

run_tests "billing/tests/test_utils/" "Utility"
UTILS_TESTS=$?

# Display results
echo "=== Billing Test Summary ==="
echo "Calculator tests: ${CALCULATOR_TESTS}"
echo "Model tests: ${MODEL_TESTS}"
echo "Serializer tests: ${SERIALIZER_TESTS}"
echo "View tests: ${VIEW_TESTS}"
echo "Rules tests: ${RULES_TESTS}"
echo "Tier tests: ${TIER_TESTS}"
echo "Integration tests: ${INTEGRATION_TESTS}"
echo "Exporter tests: ${EXPORTER_TESTS}"
echo "Service tests: ${SERVICE_TESTS}"
echo "Utility tests: ${UTILS_TESTS}"

# Return combined exit code - success only if all tests passed
if [ $CALCULATOR_TESTS -eq 0 ] && [ $MODEL_TESTS -eq 0 ] && [ $SERIALIZER_TESTS -eq 0 ] && \
   [ $VIEW_TESTS -eq 0 ] && [ $RULES_TESTS -eq 0 ] && [ $TIER_TESTS -eq 0 ] && \
   [ $INTEGRATION_TESTS -eq 0 ] && [ $EXPORTER_TESTS -eq 0 ] && [ $SERVICE_TESTS -eq 0 ] && \
   [ $UTILS_TESTS -eq 0 ]; then
    echo "✅ All Billing tests passed successfully!"
    exit 0
else
    echo "❌ Some Billing tests failed"
    exit 1
fi