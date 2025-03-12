#!/bin/bash
# Script to run a minimal test for customer_services using Docker

# Build the Docker test environment if not already built
docker-compose -f docker-compose.test.yml build

# Run the test container with the basic test file
echo "Running basic customer_services test..."
docker-compose -f docker-compose.test.yml run --rm \
  --entrypoint /bin/sh \
  test -c "python manage.py test customer_services.minimal_test -v 2"

# Check if the tests passed
if [ $? -eq 0 ]; then
  echo "✅ Tests passed successfully!"
else
  echo "❌ Tests failed!"
fi