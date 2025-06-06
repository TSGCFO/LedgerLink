#!/bin/bash

# Script to run the reorganized billing tests

set -e

echo "======================================"
echo "Running reorganized billing tests"
echo "======================================"

# If running locally (outside Docker)
if [ -z "$IN_DOCKER" ]; then
  echo "Running in local environment..."
  
  # Activate virtual environment if it exists
  if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
  elif [ -d "venv311" ] && [ -f "venv311/bin/activate" ]; then
    source venv311/bin/activate
  else
    echo "No virtual environment found, using system Python"
  fi
  
  # Set environment variables
  export DJANGO_SETTINGS_MODULE=LedgerLink.settings
  export PYTHONPATH=$(pwd)
  export SKIP_MATERIALIZED_VIEWS=True
  
  # Run tests using pytest
  python -m pytest billing/tests/ -v
else
  # Running in Docker environment
  echo "Running in Docker environment..."
  
  # Set environment variables
  export DJANGO_SETTINGS_MODULE=LedgerLink.settings
  export PYTHONPATH=/app
  export SKIP_MATERIALIZED_VIEWS=True
  
  # Wait for database to be ready
  python manage.py wait_for_db
  
  # Run migrations
  python manage.py migrate
  
  # Run tests using pytest
  python -m pytest billing/tests/ -v
fi

echo "======================================"
echo "Billing tests completed"
echo "======================================"