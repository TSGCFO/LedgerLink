#!/bin/bash

# LedgerLink Performance Tests Runner
# This script runs both pytest performance tests and k6 load tests

echo "=== Running LedgerLink Performance Tests ==="

# Set environment variables
export PYTHONPATH=${PYTHONPATH:-$(cd "$(dirname "$0")/../.." && pwd)}
export DATABASE_URL=${DATABASE_URL:-"postgres://postgres:postgres@localhost:5432/ledgerlink_test"}
export API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
export TEST_USERNAME=${TEST_USERNAME:-"admin"}
export TEST_PASSWORD=${TEST_PASSWORD:-"adminpassword"}

# Create results directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "Test Environment:"
echo "- PYTHONPATH: $PYTHONPATH"
echo "- DATABASE_URL: $DATABASE_URL"
echo "- API_BASE_URL: $API_BASE_URL"
echo "- System: $(uname -a)"
echo "- Results directory: $RESULTS_DIR"
echo "----------------------------------------"

# PART 1: Run pytest performance tests
echo "Running pytest performance tests..."
cd "$(dirname "$0")"

# Check if pytest and pytest-benchmark are installed
if ! python -c "import pytest, pytest_benchmark" &> /dev/null; then
    echo "Installing required Python packages..."
    pip install pytest pytest-benchmark pytest-django
fi

# Run pytest with benchmark
python -m pytest ../integration/test_performance.py -v --benchmark-save

# Generate performance report
echo "Generating Python performance report..."
python generate_report.py

# Copy report to results directory
cp -r results/* "$RESULTS_DIR/python_tests/"
echo "Python performance tests completed"
echo "----------------------------------------"

# PART 2: Run k6 load tests
echo "Running k6 load tests..."

# Check if k6 is installed
if command -v k6 &> /dev/null; then
    # Run specific API tests
    run_test() {
        local test_file="$1"
        local test_name=$(basename "$test_file" .js)
        
        echo "Running $test_name..."
        k6 run \
            --out json="$RESULTS_DIR/k6_tests/${test_name}.json" \
            --summary-export="$RESULTS_DIR/k6_tests/${test_name}_summary.json" \
            "$test_file"
        
        echo "$test_name completed"
        echo "----------------------------------------"
    }

    # Create k6 results directory
    mkdir -p "$RESULTS_DIR/k6_tests"

    # Run all the k6 performance tests
    if [ -f "api_load_test.js" ]; then
        run_test "api_load_test.js"
    fi
    if [ -f "order_api_load_test.js" ]; then
        run_test "order_api_load_test.js"
    fi
    if [ -f "customer_api_load_test.js" ]; then
        run_test "customer_api_load_test.js"
    fi
else
    echo "k6 is not installed - skipping k6 load tests"
    echo "To install k6, visit: https://k6.io/docs/getting-started/installation/"
fi

# Create a summary file
cat > "$RESULTS_DIR/README.md" << EOL
# LedgerLink Performance Test Results

Date: $(date)

## Test Environment
- API URL: $API_BASE_URL
- Database: $DATABASE_URL
- Test User: $TEST_USERNAME
- System: $(uname -a)

## Test Categories

### Python Performance Tests
Located in \`python_tests/\` directory:
- Integration test performance measurements
- Database query performance
- API response time tests

### k6 Load Tests
Located in \`k6_tests/\` directory (if k6 is installed):
- api_load_test.js - General API endpoints test
- order_api_load_test.js - Order API endpoints test
- customer_api_load_test.js - Customer API endpoints test

## Visualizing Results

For Python test results:
- Review the Markdown reports in the python_tests directory

For k6 test results:
- k6 web dashboard: https://k6.io/docs/results-visualization/k6-web-dashboard/
- Grafana: https://k6.io/docs/results-visualization/grafana-dashboards/

## Next Steps
To analyze these results, you can:
1. Compare with previous test runs
2. Identify endpoints with high latency
3. Check for errors or timeouts
4. Look for performance regressions
EOL

echo "=== Performance Test Results ==="
echo "All results saved to: $RESULTS_DIR/"
echo ""
echo "To view summary: cat $RESULTS_DIR/README.md"
echo ""
echo "=== End of Performance Tests ==="