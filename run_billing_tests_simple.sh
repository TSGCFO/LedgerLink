#!/bin/bash
set -e

echo "=== Running Billing Tests ==="

# Ensure dependencies are installed in a virtual environment
# python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Use the Docker environment but run tests locally
source venv/bin/activate

# Set environment variables for test execution
export SKIP_MATERIALIZED_VIEWS=True
export DJANGO_SETTINGS_MODULE=LedgerLink.settings

# Run direct tests first
echo "Running direct unit tests..."
python -m pytest billing/test_billing_calculator.py billing/test_utils.py -v

# Get the exit code
DIRECT_TESTS=$?

echo "Direct tests exit code: $DIRECT_TESTS"

exit $DIRECT_TESTS