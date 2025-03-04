#!/bin/bash
set -e

# Script to run LedgerLink Rules app tests with Docker and PostgreSQL

# Fix Docker credential issue
if [ ! -f ~/.docker/config.json ]; then
  echo "Setting up Docker configuration to avoid credential issues..."
  mkdir -p ~/.docker
  echo '{"credsStore":""}' > ~/.docker/config.json
fi

echo "=== Running LedgerLink Rules Tests with PostgreSQL ==="
echo "Building and starting test containers..."

# Stop any existing test containers
docker compose -f docker-compose.test.yml down

# Build and start test containers
docker compose -f docker-compose.test.yml up --build -d db

# Wait a moment for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run the tests
echo "Running tests for Rules app only..."
docker compose -f docker-compose.test.yml run --rm \
  test \
  -c "sleep 5 && python manage.py migrate && python -m pytest rules/tests/ rules/test_*.py -v"

# Get the exit code
EXIT_CODE=$?

# Stop the containers
echo "Stopping test containers..."
docker compose -f docker-compose.test.yml down

# Display results
if [ $EXIT_CODE -eq 0 ]; then
  echo "=== All Rules tests passed! ==="
else
  echo "=== Rules tests failed with exit code $EXIT_CODE ==="
fi

exit $EXIT_CODE