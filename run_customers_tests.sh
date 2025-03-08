#!/bin/bash

# Run all customers app tests in Docker environment
echo "Running Customer app tests in Docker environment..."

# Run unit tests
echo "Running unit tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest customers/tests/test_models.py customers/tests/test_serializers.py customers/tests/test_urls.py -v

# Run integration tests
echo "Running integration tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest customers/tests/test_views.py customers/tests/integration/ -v

# Run contract tests (PACT)
echo "Running contract tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest customers/test_pact_provider.py -v

# Run performance tests
echo "Running performance tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest customers/tests/performance/ -v

# Run complete test suite with coverage
echo "Running complete test suite with coverage..."
docker compose -f docker-compose.test.yml run --rm \
  test sh -c "coverage run --source='customers' -m pytest customers/ -v && coverage report && coverage html -d coverage_html/customers"

echo "All Customer app tests completed."