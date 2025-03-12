#!/bin/bash

# Run all products app tests in Docker environment
echo "Running Products app tests in Docker environment..."

# Run unit tests
echo "Running unit tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest products/tests/test_models.py products/tests/test_serializers.py products/tests/test_urls.py -v

# Run integration tests
echo "Running integration tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest products/tests/test_views.py products/tests/integration/ -v

# Run contract tests (PACT)
echo "Running contract tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest products/test_pact_provider.py -v

# Run performance tests
echo "Running performance tests..."
docker compose -f docker-compose.test.yml run --rm \
  test python -m pytest products/tests/performance/ -v

# Run complete test suite with coverage
echo "Running complete test suite with coverage..."
docker compose -f docker-compose.test.yml run --rm \
  test sh -c "coverage run --source='products' -m pytest products/ -v && coverage report && coverage html -d coverage_html/products"

echo "All Products app tests completed."