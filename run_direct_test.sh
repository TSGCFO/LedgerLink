#!/bin/bash
# Script to run our direct test script for customer_services using Docker

# Start the DB only
echo "Starting PostgreSQL container..."
docker-compose -f docker-compose.test.yml up --build -d db

# Wait for DB to be ready
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run our test script directly
echo "Running direct customer_services test..."
docker-compose -f docker-compose.test.yml run --rm \
  --entrypoint /bin/sh \
  test -c "python test_scripts/direct_db_test.py -v"

# Get exit code
EXIT_CODE=$?

# Stop containers
echo "Stopping containers..."
docker-compose -f docker-compose.test.yml down

# Display result
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Tests passed successfully!"
else
  echo "❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE