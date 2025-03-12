#!/bin/bash
# Script to run Django tests with materialized views skipped

# Export environment variables
export DJANGO_SETTINGS_MODULE=LedgerLink.settings
export SKIP_MATERIALIZED_VIEWS=True
export PYTHONPATH=/LedgerLink:$PYTHONPATH

# Run the tests for the requested app
APP_NAME=${1:-customer_services}

echo "Running Django tests for $APP_NAME"
python manage.py test $APP_NAME -v 2

# Get exit code
EXIT_CODE=$?

# Report result
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Tests passed successfully!"
else
  echo "❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE