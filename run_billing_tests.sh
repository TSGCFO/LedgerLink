#!/bin/bash
set -e

# Script to run LedgerLink Billing app tests with proper integration to the main test framework

echo "=== Running LedgerLink Billing Tests with Full Integration ==="

# Clean Python cache files
echo "Cleaning Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Stop any existing test containers
docker compose -f docker-compose.test.yml down -v

# Start the database container
docker compose -f docker-compose.test.yml up --build -d db

# Wait for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 10

# Set up database schema
echo "Setting up database schema..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  -e DJANGO_SETTINGS_MODULE=LedgerLink.settings \
  -e DISABLE_CUSTOM_MIGRATIONS=True \
  test bash -c "\
    # Wait for database to be ready
    echo 'Waiting for database...' && \
    while ! psql postgresql://postgres:postgres@db:5432/ledgerlink_test -c 'SELECT 1;' 2>/dev/null; do \
      echo 'Database not ready - waiting 2 seconds...' && \
      sleep 2; \
    done && \
    echo 'Database is ready!' && \
    
    # Run migrations for all apps in the correct order
    echo 'Running migrations for all apps in correct order...' && \
    python manage.py migrate auth && \
    python manage.py migrate contenttypes && \
    python manage.py migrate admin && \
    python manage.py migrate sessions && \
    
    # Core apps (no materialized views)
    python manage.py migrate customers && \
    python manage.py migrate services && \
    python manage.py migrate products && \
    python manage.py migrate materials && \
    
    # Rules app (no materialized views)
    python manage.py migrate rules && \
    
    # Apps with materialized views - use fake migrations
    echo "Applying migrations with --fake for apps with materialized views" && \
    python manage.py migrate customer_services --fake && \
    python manage.py migrate shipping --fake && \
    python manage.py migrate inserts --fake && \
    python manage.py migrate orders --fake && \
    python manage.py migrate billing --fake && \
    python manage.py migrate bulk_operations --fake && \
    
    # Create the tables without materialized views
    echo "Creating tables manually via SQL" && \
    psql postgresql://postgres:postgres@db:5432/ledgerlink_test -c "
    -- Customer Services tables
    CREATE TABLE IF NOT EXISTS customer_services_customerservice (
        id SERIAL PRIMARY KEY,
        unit_price NUMERIC(10,2) NOT NULL,
        is_active BOOLEAN NOT NULL,
        customer_id INTEGER NOT NULL REFERENCES customers_customer(id) ON DELETE CASCADE,
        service_id INTEGER NOT NULL REFERENCES services_service(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Orders tables  
    CREATE TABLE IF NOT EXISTS orders_order (
        transaction_id BIGINT PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers_customer(id) ON DELETE CASCADE,
        close_date TIMESTAMP WITH TIME ZONE,
        reference_number VARCHAR(100) NOT NULL,
        ship_to_name VARCHAR(100),
        ship_to_company VARCHAR(100),
        ship_to_address VARCHAR(200),
        ship_to_address2 VARCHAR(200),
        ship_to_city VARCHAR(100),
        ship_to_state VARCHAR(50),
        ship_to_zip VARCHAR(20),
        ship_to_country VARCHAR(50),
        weight_lb NUMERIC(10,2),
        line_items INTEGER,
        sku_quantity JSONB,
        total_item_qty INTEGER,
        volume_cuft NUMERIC(10,2),
        packages INTEGER,
        notes TEXT,
        carrier VARCHAR(50),
        status VARCHAR(20) NOT NULL,
        priority VARCHAR(20) NOT NULL
    );
    
    -- Billing tables
    CREATE TABLE IF NOT EXISTS billing_billingreport (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers_customer(id) ON DELETE CASCADE,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        total_amount NUMERIC(10,2) NOT NULL,
        report_data JSONB,
        generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
        updated_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS billing_billingreportdetail (
        id SERIAL PRIMARY KEY,
        report_id INTEGER NOT NULL REFERENCES billing_billingreport(id) ON DELETE CASCADE,
        order_id BIGINT NOT NULL REFERENCES orders_order(transaction_id) ON DELETE CASCADE,
        service_breakdown JSONB,
        total_amount NUMERIC(10,2) NOT NULL
    );
    " && \
    
    echo 'Database setup complete' \
  "

# Run full test suite
echo "Running billing tests..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  -e DJANGO_SETTINGS_MODULE=LedgerLink.settings \
  -e DISABLE_CUSTOM_MIGRATIONS=True \
  test bash -c "\
    # Run billing app tests one directory at a time
    for test_dir in billing/tests/test_models/ billing/tests/test_serializers/ billing/tests/test_views/ \
                    billing/tests/test_calculator/ billing/tests/test_tiers/ billing/tests/test_services/ \
                    billing/tests/test_utils/ billing/tests/test_integration/; do \
      if [ -d \"\$test_dir\" ]; then \
        echo '=====================================' && \
        echo \"Running tests in: \$test_dir\" && \
        echo '=====================================' && \
        python -m pytest \$test_dir -v || true; \
      else \
        echo \"Warning: Directory \$test_dir not found, skipping\"; \
      fi; \
    done && \
    echo 'All tests completed!' \
  "

# Clean up
echo "Stopping test containers..."
docker compose -f docker-compose.test.yml down -v

echo "=== Billing Tests Completed ==="
echo "Check the test output for successes and failures"