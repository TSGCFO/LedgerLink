#!/bin/bash
set -e

# Script to run LedgerLink Billing app tests with coverage

echo "=== Running LedgerLink Billing Tests with Coverage ==="

# Check if in Docker environment
if [ -f /.dockerenv ] || [ -n "$IN_DOCKER" ]; then
  # In Docker - use the Docker command
  echo "Running in Docker environment..."
  
  # Make sure containers are running
  docker compose -f docker-compose.test.yml up -d db
  
  # Run tests with coverage
  docker compose -f docker-compose.test.yml run --rm \
    test \
    -c "sleep 5 && python manage.py migrate && python -m pytest --cov=billing --cov-report=term --cov-report=html billing/tests/ billing/test_*.py -v"
  
  # Get the exit code
  EXIT_CODE=$?
  
  # Display results
  if [ $EXIT_CODE -eq 0 ]; then
    echo "=== All Billing tests passed! ==="
    echo "Coverage report generated in htmlcov/ directory"
  else
    echo "=== Billing tests failed with exit code $EXIT_CODE ==="
  fi
  
else
  # Not in Docker - use TestContainers or local database
  echo "Running in local environment..."
  
  # Check if USE_TESTCONTAINERS is set
  if [ "$USE_TESTCONTAINERS" = "True" ]; then
    echo "Using TestContainers for database..."
    USE_TESTCONTAINERS=True python -m pytest --cov=billing --cov-report=term --cov-report=html billing/tests/ billing/test_*.py -v
  else
    echo "Using local database..."
    python -m pytest --cov=billing --cov-report=term --cov-report=html billing/tests/ billing/test_*.py -v
  fi
  
  # Get the exit code
  EXIT_CODE=$?
  
  # Display results
  if [ $EXIT_CODE -eq 0 ]; then
    echo "=== All Billing tests passed! ==="
    echo "Coverage report generated in htmlcov/ directory"
  else
    echo "=== Billing tests failed with exit code $EXIT_CODE ==="
  fi
fi

exit $EXIT_CODE