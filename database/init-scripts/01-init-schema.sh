#!/bin/bash
set -e

# This script initializes the PostgreSQL database with the LedgerLink schema
# It runs automatically when the container starts for the first time

echo "Initializing LedgerLink test database schema..."

# Apply the schema from dump file if it exists
if [ -f /schema/ledgerlink_schema.sql ]; then
  echo "Applying schema from dump file..."
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /schema/ledgerlink_schema.sql
  echo "Schema applied successfully"
  
  # Apply test data if it exists
  if [ -f /schema/ledgerlink_testdata.sql ]; then
    echo "Loading test data..."
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /schema/ledgerlink_testdata.sql
    echo "Test data loaded successfully"
  fi
else
  echo "No schema dump found - database will be empty"
  echo "You can create a schema dump by running the init_test_db.sh script"
fi

echo "Database initialization complete"