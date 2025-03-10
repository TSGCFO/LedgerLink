#!/bin/bash
set -e

# Script to run minimal billing app tests using direct database setup

echo "=== Running Minimal Billing Tests ==="

# Clean any existing containers
docker compose -f docker-compose.test.yml down -v

# Start the database
docker compose -f docker-compose.test.yml up -d db

# Wait for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Set up database and run tests
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  -e DJANGO_SETTINGS_MODULE=tests.settings \
  test bash -c "\
    # Wait for database to be ready
    echo 'Waiting for database...' && \
    while ! psql postgresql://postgres:postgres@db:5432/ledgerlink_test -c 'SELECT 1;' 2>/dev/null; do \
      echo 'Database not ready - waiting 2 seconds...' && \
      sleep 2; \
    done && \
    
    # Create required tables directly
    echo 'Setting up minimal database schema...' && \
    psql postgresql://postgres:postgres@db:5432/ledgerlink_test << 'EOQ'
    
    -- Create auth_user table
    DROP TABLE IF EXISTS auth_user CASCADE;
    CREATE TABLE auth_user (
        id SERIAL PRIMARY KEY,
        username VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(128) NOT NULL,
        email VARCHAR(254) NOT NULL,
        first_name VARCHAR(150) NOT NULL DEFAULT '',
        last_name VARCHAR(150) NOT NULL DEFAULT '',
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        is_staff BOOLEAN NOT NULL DEFAULT FALSE,
        is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
        date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        last_login TIMESTAMP WITH TIME ZONE NULL
    );
    
    -- Create customers_customer table
    DROP TABLE IF EXISTS customers_customer CASCADE;
    CREATE TABLE customers_customer (
        id SERIAL PRIMARY KEY,
        company_name VARCHAR(255) NOT NULL,
        legal_business_name VARCHAR(255) NULL,
        contact_email VARCHAR(255) NULL,
        phone_number VARCHAR(20) NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE
    );
    
    -- Create orders_order table
    DROP TABLE IF EXISTS orders_order CASCADE;
    CREATE TABLE orders_order (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers_customer(id) ON DELETE CASCADE,
        reference_number VARCHAR(100) NULL,
        ship_to_name VARCHAR(255) NULL,
        ship_to_address VARCHAR(255) NULL,
        ship_to_city VARCHAR(255) NULL,
        ship_to_state VARCHAR(50) NULL,
        ship_to_zip VARCHAR(50) NULL,
        sku_quantity JSONB NULL,
        total_item_qty INTEGER NULL,
        status VARCHAR(50) NULL DEFAULT 'new',
        priority VARCHAR(50) NULL DEFAULT 'medium'
    );
    
    -- Create billing_billingreport table
    DROP TABLE IF EXISTS billing_billingreport CASCADE;
    CREATE TABLE billing_billingreport (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers_customer(id) ON DELETE CASCADE,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        report_data JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL NULL,
        updated_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL NULL,
        generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create billing_billingreportdetail table
    DROP TABLE IF EXISTS billing_billingreportdetail CASCADE;
    CREATE TABLE billing_billingreportdetail (
        id SERIAL PRIMARY KEY,
        report_id INTEGER REFERENCES billing_billingreport(id) ON DELETE CASCADE,
        order_id INTEGER NULL,
        service_breakdown JSONB NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL
    );
EOQ && \
    
    # Run minimal and direct tests
    echo '=== Running minimal test ===' && \
    python -m pytest billing/minimal_test.py -v && \
    echo '=== Running direct test ===' && \
    python -m pytest billing/test_direct.py -v \
  "

# Get the exit code
TESTS_RESULT=$?

# Clean up
docker compose -f docker-compose.test.yml down -v

# Report results
if [ $TESTS_RESULT -eq 0 ]; then
    echo "✅ Minimal billing tests passed!"
    exit 0
else
    echo "❌ Minimal billing tests failed with exit code: $TESTS_RESULT"
    exit 1
fi