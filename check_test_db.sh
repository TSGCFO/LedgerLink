#!/bin/bash
# Script to check the structure of the test database in Docker

echo "=================================="
echo "LedgerLink Test Database Analysis"
echo "=================================="

# Get schema dump
echo "Extracting schema from test database..."
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "PGPASSWORD=postgres pg_dump -h db -U postgres -s ledgerlink_test > /app/test_schema.sql"

# Count objects
echo -e "\n=== Database Object Counts ==="
echo "Tables: $(docker compose -f docker-compose.test.yml run --rm test bash -c "echo '\dt' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test -t | wc -l")"
echo "Views: $(docker compose -f docker-compose.test.yml run --rm test bash -c "echo '\dv' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test -t | wc -l")"
echo "Materialized Views: $(docker compose -f docker-compose.test.yml run --rm test bash -c "echo '\dm' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test -t | wc -l")"
echo "Indices: $(docker compose -f docker-compose.test.yml run --rm test bash -c "echo '\di' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test -t | wc -l")"
echo "Functions: $(docker compose -f docker-compose.test.yml run --rm test bash -c "echo '\df' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test -t | wc -l")"
echo "Triggers: $(docker compose -f docker-compose.test.yml run --rm test bash -c "echo '\dft' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test -t | wc -l")"

# List tables
echo -e "\n=== Tables ==="
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\dt' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

# List views
echo -e "\n=== Views ==="
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\dv' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

# List materialized views
echo -e "\n=== Materialized Views ==="
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\dm' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

# Check the structure of specific tables/views that are critical for testing
echo -e "\n=== Critical Table/View Structures ==="
echo -e "\n--- orders_order Table ---"
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\d orders_order' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

echo -e "\n--- billing_billingreport Table ---"
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\d billing_billingreport' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

echo -e "\n--- orders_sku_view Materialized View ---"
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\d orders_sku_view' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

echo -e "\n--- customer_services_customerserviceview Materialized View ---"
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo '\d customer_services_customerserviceview' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

# Check for numeric transaction_id in orders
echo -e "\n=== Transaction ID Field Type Check ==="
docker compose -f docker-compose.test.yml run --rm test bash -c \
  "echo 'SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '\''orders_order'\'' AND column_name = '\''transaction_id'\'';' | PGPASSWORD=postgres psql -h db -U postgres -d ledgerlink_test"

echo -e "\n=== Database Analysis Complete ==="