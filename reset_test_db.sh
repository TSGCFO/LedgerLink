#!/bin/bash
# Reset the test database to a known state without rebuilding the schema

set -e  # Exit on any error

echo "=== Resetting LedgerLink Test Database ==="

# Check if the dump file exists
if [ ! -f test_db_dump.sql ]; then
  echo "Database dump file not found. Run init_test_db.sh first."
  exit 1
fi

# Make sure database is running
docker compose -f docker-compose.test.yml up -d db

echo "Waiting for PostgreSQL to be ready..."
sleep 5  # Simple sleep-based wait

# Reset the database using the dump
echo "Restoring database from dump..."
docker compose -f docker-compose.test.yml exec db bash -c "
  # Drop connections and recreate database
  psql -U postgres -c \"
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = 'ledgerlink_test'
    AND pid <> pg_backend_pid();
    DROP DATABASE IF EXISTS ledgerlink_test;
    CREATE DATABASE ledgerlink_test;
  \"
"

# Restore the dump
cat test_db_dump.sql | docker compose -f docker-compose.test.yml exec -T db psql -U postgres ledgerlink_test

echo "=== Database reset complete ==="
echo "The database has been restored to its initial state."