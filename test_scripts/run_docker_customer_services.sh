#!/bin/bash
# Simple Docker-based test runner for customer_services

# Stop and remove any existing containers
echo "Cleaning up existing containers..."
docker-compose -f docker-compose.test.yml down

# Build test image
echo "Building test image..."
docker build -t ledgerlink-test:latest -f Dockerfile.test .

# Run PostgreSQL container
echo "Starting PostgreSQL container..."
docker run --name pg-test -d -e POSTGRES_DB=ledgerlink_test -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15

# Wait for PostgreSQL to start
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run tests with custom settings
echo "Running customer_services tests..."
docker run --rm --network=host -v $(pwd):/app -w /app \
  -e DJANGO_SETTINGS_MODULE=LedgerLink.settings \
  -e DB_HOST=localhost \
  -e DB_NAME=ledgerlink_test \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e SKIP_MATERIALIZED_VIEWS=True \
  -e IN_DOCKER=true \
  ledgerlink-test:latest \
  python -m pytest customer_services/tests/test_models.py -v

# Get exit code
EXIT_CODE=$?

# Cleanup
echo "Cleaning up containers..."
docker stop pg-test && docker rm pg-test

# Report result
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Tests passed successfully!"
else
  echo "❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE