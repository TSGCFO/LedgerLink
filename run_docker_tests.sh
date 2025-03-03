#!/bin/bash

# Script to run LedgerLink tests with Docker and PostgreSQL

echo "=== Running LedgerLink tests with PostgreSQL ==="
echo "Building and starting test containers..."

# Stop any existing test containers
docker-compose -f docker-compose.test.yml down

# Build and start test containers
docker-compose -f docker-compose.test.yml up --build -d db

# Wait a moment for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run the tests
echo "Running tests..."
docker-compose -f docker-compose.test.yml run --rm test

# Get the exit code
EXIT_CODE=$?

# Stop the containers
echo "Stopping test containers..."
docker-compose -f docker-compose.test.yml down

# Display results
if [ $EXIT_CODE -eq 0 ]; then
  echo "=== All tests passed! ==="
else
  echo "=== Tests failed with exit code $EXIT_CODE ==="
fi

exit $EXIT_CODE