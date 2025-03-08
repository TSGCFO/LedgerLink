#!/bin/bash
# Base test setup script for LedgerLink
# This script sets up common environment variables and configurations for all test runs

# Set environment variables for test configuration
export SKIP_MATERIALIZED_VIEWS=True
export DJANGO_SETTINGS_MODULE=LedgerLink.settings
export PYTHONPATH=$PYTHONPATH:/LedgerLink

# Run database setup script to ensure database is properly configured
if [ -f "$(dirname "$0")/db_setup.py" ]; then
  python "$(dirname "$0")/db_setup.py"
else
  echo "⚠️ Database setup script not found, skipping"
fi

# If we're using TestContainers, set that flag
if [ "${USE_TESTCONTAINERS}" = "True" ]; then
  echo "🔍 Using TestContainers for database isolation"
else
  echo "🔍 Using standard database configuration"
fi

# Common flags for pytest
PYTEST_FLAGS="-v"

# Function to run tests with proper environment
run_app_tests() {
  local app_name=$1
  local test_file=$2
  
  if [ -z "$test_file" ]; then
    echo "🧪 Running all tests for $app_name"
    python -m pytest $app_name/ $PYTEST_FLAGS
  else
    echo "🧪 Running specific test file: $test_file"
    python -m pytest $test_file $PYTEST_FLAGS
  fi
}

# Print test configuration
echo "==== LedgerLink Test Configuration ===="
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "SKIP_MATERIALIZED_VIEWS: $SKIP_MATERIALIZED_VIEWS"
echo "USE_TESTCONTAINERS: $USE_TESTCONTAINERS"
echo "====================================="