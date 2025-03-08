#!/bin/bash
# Test runner script for customer_services app

# Add database testing flag to ensure proper environment
export PYTHONPATH=/LedgerLink:$PYTHONPATH
export USE_MATERIALIZED_VIEWS=False

# Source the base test setup script
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/base/test_setup.sh" ]; then
  source "$SCRIPT_DIR/base/test_setup.sh"
else
  echo "⚠️ Base test setup script not found at $SCRIPT_DIR/base/test_setup.sh"
  export SKIP_MATERIALIZED_VIEWS=True
  export DJANGO_SETTINGS_MODULE=LedgerLink.settings
fi

# Run customer_services tests
echo "🔍 Running customer_services tests"

# Run model tests first since they've been problematic
run_app_tests "customer_services" "customer_services/tests/test_models.py"

# If model tests pass, run the rest of the tests
if [ $? -eq 0 ]; then
  echo "✅ Model tests passed, running remaining tests"
  
  # Run other test files one by one to isolate any issues
  run_app_tests "customer_services" "customer_services/tests/test_serializers.py"
  run_app_tests "customer_services" "customer_services/tests/test_views.py"
  run_app_tests "customer_services" "customer_services/tests/test_integration.py"
  run_app_tests "customer_services" "customer_services/tests/test_performance.py"
else
  echo "❌ Model tests failed, fix these before continuing"
  exit 1
fi

# Print summary
echo "==== Customer Services Test Summary ===="
echo "All tests completed. Check output for results."
echo "====================================="