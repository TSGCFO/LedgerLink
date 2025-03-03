#!/bin/bash
# Run Django tests with coverage and generate reports

# Check if specific apps or test paths were provided
if [ $# -gt 0 ]; then
    TEST_PATHS="$@"
else
    # Default to all Django apps if no specific paths provided
    TEST_PATHS="api customers orders products billing services rules inserts customer_services shipping materials bulk_operations"
fi

# Run tests with coverage
echo "Running tests with coverage for: $TEST_PATHS"
coverage run -m pytest $TEST_PATHS "$@"

# Generate coverage reports
echo "Generating coverage report..."
coverage report -m

# Generate HTML coverage report
echo "Generating HTML coverage report..."
coverage html

echo "Tests complete! Coverage report is available in htmlcov/index.html"