#!/bin/bash
# Script to run customer_services tests with coverage report

# Start the PostgreSQL DB container
echo "Starting PostgreSQL container..."
docker-compose -f docker-compose.test.yml up --build -d db

# Wait for database to be ready
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Run tests with coverage
echo "=================================="
echo "Running customer_services tests with coverage..."
echo "=================================="

# Install coverage in the container if not already present
docker-compose -f docker-compose.test.yml run --rm \
  test bash -c "pip install coverage pytest-cov && \
                coverage run -m unittest discover -s customer_services/tests && \
                coverage report -m --include='customer_services/*' && \
                coverage html -d coverage_html --include='customer_services/*'"

# Get the exit code
COVERAGE_RESULT=$?

# Stop containers
echo "Stopping containers..."
docker-compose -f docker-compose.test.yml down

# Report results
if [ $COVERAGE_RESULT -eq 0 ]; then
  echo
  echo "✅ Coverage report generated successfully!"
  echo "Check the coverage_html directory for detailed reports."
  echo
  exit 0
else
  echo
  echo "❌ Coverage report generation failed."
  echo
  exit 1
fi