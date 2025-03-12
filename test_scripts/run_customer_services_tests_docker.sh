#!/bin/bash
# Script to run customer_services tests with Docker and PostgreSQL

# Source the main Docker test script for environment setup
SCRIPT_DIR="$(dirname "$0")"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Fix Docker credential issue 
if [ ! -f ~/.docker/config.json ]; then
  echo "Setting up Docker configuration to avoid credential issues..."
  mkdir -p ~/.docker
  echo '{"credsStore":""}' > ~/.docker/config.json
fi

echo "=== Running customer_services tests with PostgreSQL ==="
echo "Building and starting test containers..."

# Stop any existing test containers
docker compose -f $ROOT_DIR/docker-compose.test.yml down

# Build and start test containers
docker compose -f $ROOT_DIR/docker-compose.test.yml up --build -d db

# Wait a moment for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run the test container with our command for model tests
echo "Running customer_services model tests..."
docker compose -f $ROOT_DIR/docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test python -m pytest customer_services/tests/test_models.py -v

# Get the exit code
EXIT_CODE=$?

# If the model tests pass, run the other tests
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Model tests passed, running remaining tests"
  
  # Run other test files
  docker compose -f $ROOT_DIR/docker-compose.test.yml run --rm \
    -e SKIP_MATERIALIZED_VIEWS=True \
    test python -m pytest customer_services/tests/test_serializers.py -v
  
  docker compose -f $ROOT_DIR/docker-compose.test.yml run --rm \
    -e SKIP_MATERIALIZED_VIEWS=True \
    test python -m pytest customer_services/tests/test_views.py -v
  
  docker compose -f $ROOT_DIR/docker-compose.test.yml run --rm \
    -e SKIP_MATERIALIZED_VIEWS=True \
    test python -m pytest customer_services/tests/test_integration.py -v
else
  echo "❌ Model tests failed, fix these before continuing"
fi

# Stop the containers
echo "Stopping test containers..."
docker compose -f $ROOT_DIR/docker-compose.test.yml down

# Display results
if [ $EXIT_CODE -eq 0 ]; then
  echo "=== All tests passed! ==="
else
  echo "=== Tests failed with exit code $EXIT_CODE ==="
fi

exit $EXIT_CODE