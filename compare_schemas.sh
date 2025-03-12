#!/bin/bash
# Script to compare database schemas between production and test databases

# Set variables for both databases
PROD_HOST="db.dorunzumqoeiozqiyiux.supabase.co"
PROD_DB="postgres"
PROD_USER="postgres"
PROD_PASSWORD="Hassan8488\$"

TEST_HOST="db"
TEST_DB="ledgerlink_test"
TEST_USER="postgres"
TEST_PASSWORD="postgres"

# Dump production schema
echo "Dumping production schema..."
PGPASSWORD=$PROD_PASSWORD pg_dump -h $PROD_HOST -U $PROD_USER -d $PROD_DB --schema-only > prod_schema.sql

# Dump test schema from Docker
echo "Dumping test schema from Docker..."
docker compose -f docker-compose.test.yml run --rm test bash -c "PGPASSWORD=$TEST_PASSWORD pg_dump -h $TEST_HOST -U $TEST_USER -d $TEST_DB --schema-only > /app/test_schema.sql"

# Compare schemas
echo "Comparing schemas..."
diff -u prod_schema.sql test_schema.sql > schema_diff.txt

# Check if there are differences
if [ -s schema_diff.txt ]; then
    echo "Differences found! Check schema_diff.txt for details."
    
    # Count differences by object type
    echo "Differences by object type:"
    echo "Tables: $(grep -c 'CREATE TABLE' schema_diff.txt)"
    echo "Indexes: $(grep -c 'CREATE INDEX' schema_diff.txt)"
    echo "Views: $(grep -c 'CREATE VIEW' schema_diff.txt)"
    echo "Materialized Views: $(grep -c 'CREATE MATERIALIZED VIEW' schema_diff.txt)"
    echo "Functions: $(grep -c 'CREATE FUNCTION' schema_diff.txt)"
    echo "Triggers: $(grep -c 'CREATE TRIGGER' schema_diff.txt)"
    
    # Show table differences
    echo "Table differences:"
    grep -A 5 'CREATE TABLE' schema_diff.txt | head -20
else
    echo "No differences found. Schemas match exactly!"
fi

# Clean up
echo "Cleaning up temporary files..."
rm prod_schema.sql test_schema.sql
echo "Done!"