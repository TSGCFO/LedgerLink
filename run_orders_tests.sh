#!/bin/bash
set -e

# Script to run LedgerLink Orders app tests with proper integration to the main test framework

echo "=== Running LedgerLink Orders Tests with Full Integration ==="

# Function to clean Python cache files
clean_pycache() {
    echo "Cleaning Python cache files..."
    docker compose -f docker-compose.test.yml run --rm \
      test \
      find /app/orders -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Stop any existing test containers
docker compose -f docker-compose.test.yml down

# Build and start test containers
docker compose -f docker-compose.test.yml up --build -d db

# Wait for the database to initialize (increased for reliability)
echo "Waiting for PostgreSQL to initialize..."
sleep 8

# Clean Python cache files
clean_pycache

# First run schema verification and prepare database properly
echo "Verifying database schema and setting up required tables..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=False \
  test \
  python -c "
import pytest
import os
from django.db import connection
from django.conf import settings

# Connect to the database
with connection.cursor() as cursor:
    # Check for the is_active column
    cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name=%s\", (\"customers_customer\",))
    columns = [row[0] for row in cursor.fetchall()]
    
    print(f\"\\nColumns in customers_customer table: {columns}\")
    
    if \"is_active\" in columns:
        print(\"\\nSUCCESS: is_active field exists in customers_customer table\")
        
        # Now create required tables and columns for testing if they don't exist
        print(\"Setting up required database objects for testing...\")
        
        # Check if billing_billingreport table exists and has generated_at column
        cursor.execute(\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'billing_billingreport' AND column_name = 'generated_at'
            );
        \"\"\")
        generated_at_exists = cursor.fetchone()[0]
        
        if not generated_at_exists:
            print(\"Adding generated_at column to billing_billingreport table...\")
            cursor.execute(\"\"\"
                ALTER TABLE billing_billingreport 
                ADD COLUMN IF NOT EXISTS generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            \"\"\")
            print(\"Added generated_at column\")
            
        # Check if billing_billingreportdetail table exists
        cursor.execute(\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'billing_billingreportdetail'
            );
        \"\"\")
        detail_table_exists = cursor.fetchone()[0]
        
        if not detail_table_exists:
            print(\"Creating billing_billingreportdetail table...\")
            cursor.execute(\"\"\"
                CREATE TABLE billing_billingreportdetail (
                    id SERIAL PRIMARY KEY,
                    service_breakdown JSONB NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    order_id INT NOT NULL,
                    report_id INT NOT NULL,
                    CONSTRAINT fk_order FOREIGN KEY(order_id) REFERENCES orders_order(transaction_id) ON DELETE CASCADE,
                    CONSTRAINT fk_report FOREIGN KEY(report_id) REFERENCES billing_billingreport(id) ON DELETE CASCADE
                );
                
                CREATE INDEX idx_billingreportdetail_report_order ON billing_billingreportdetail(report_id, order_id);
                CREATE INDEX idx_billingreportdetail_total_amount ON billing_billingreportdetail(total_amount);
            \"\"\")
            print(\"Created billing_billingreportdetail table\")
            
        # Create shipping_cadshipping table if it doesn't exist
        cursor.execute(\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'shipping_cadshipping'
            );
        \"\"\")
        cadshipping_exists = cursor.fetchone()[0]
        
        if not cadshipping_exists:
            print(\"Creating shipping_cadshipping table...\")
            cursor.execute(\"\"\"
                CREATE TABLE shipping_cadshipping (
                    id SERIAL PRIMARY KEY,
                    transaction_id INT REFERENCES orders_order(transaction_id) ON DELETE CASCADE,
                    service_type VARCHAR(50),
                    tracking_number VARCHAR(100),
                    cost DECIMAL(10, 2)
                );
                
                CREATE INDEX idx_cadshipping_transaction_id ON shipping_cadshipping(transaction_id);
            \"\"\")
            print(\"Created shipping_cadshipping table\")
            
        # Create shipping_usshipping table if it doesn't exist
        cursor.execute(\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'shipping_usshipping'
            );
        \"\"\")
        usshipping_exists = cursor.fetchone()[0]
        
        if not usshipping_exists:
            print(\"Creating shipping_usshipping table...\")
            cursor.execute(\"\"\"
                CREATE TABLE shipping_usshipping (
                    id SERIAL PRIMARY KEY,
                    transaction_id INT REFERENCES orders_order(transaction_id) ON DELETE CASCADE,
                    service_type VARCHAR(50),
                    tracking_number VARCHAR(100),
                    cost DECIMAL(10, 2)
                );
                
                CREATE INDEX idx_usshipping_transaction_id ON shipping_usshipping(transaction_id);
            \"\"\")
            print(\"Created shipping_usshipping table\")
        
        # Create materialized view for orders_sku_view
        print(\"Creating orders_sku_view materialized view...\")
        cursor.execute(\"\"\"
            DROP MATERIALIZED VIEW IF EXISTS orders_sku_view CASCADE;
            CREATE MATERIALIZED VIEW orders_sku_view AS
            SELECT 
                o.transaction_id,
                o.customer_id,
                o.close_date,
                o.reference_number,
                o.ship_to_name,
                o.ship_to_company,
                o.ship_to_address,
                o.ship_to_address2,
                o.ship_to_city,
                o.ship_to_state,
                o.ship_to_zip,
                o.ship_to_country,
                o.weight_lb,
                o.line_items,
                o.total_item_qty,
                o.volume_cuft,
                o.packages,
                o.notes,
                o.carrier,
                o.status,
                o.priority,
                (jsonb_each_text(o.sku_quantity::jsonb)).key AS sku_name,
                (jsonb_each_text(o.sku_quantity::jsonb)).value::integer AS sku_count,
                COALESCE((o.sku_quantity->>\'cases\')::integer, 0) AS cases,
                COALESCE((o.sku_quantity->>\'picks\')::integer, 0) AS picks,
                COALESCE((o.sku_quantity->>\'case_size\')::integer, NULL) AS case_size,
                COALESCE((o.sku_quantity->>\'case_unit\')::text, NULL) AS case_unit
            FROM 
                orders_order o
            WHERE 
                o.sku_quantity IS NOT NULL;
                
            CREATE UNIQUE INDEX IF NOT EXISTS orders_sku_view_transaction_id_idx 
            ON orders_sku_view (transaction_id, sku_name);
            CREATE INDEX IF NOT EXISTS orders_sku_view_sku_name_idx 
            ON orders_sku_view (sku_name);
            CREATE INDEX IF NOT EXISTS orders_sku_view_customer_id_idx 
            ON orders_sku_view (customer_id);
            
            REFRESH MATERIALIZED VIEW orders_sku_view;
        \"\"\")
        print(\"Created and refreshed orders_sku_view materialized view\")
        
        # Check if customer_id is found in customers_customer table
        cursor.execute(\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'customers_customer' AND column_name = 'id'
            );
        \"\"\")
        customer_id_exists = cursor.fetchone()[0]
        
        if customer_id_exists:
            print(\"Found customer_id in database for customer field\")
            
        print(\"Schema verification for orders app passed!\")
        exit(0)
    else:
        print(\"\\nERROR: is_active field does not exist in customers_customer table\")
        exit(1)
"

# Get schema check exit code
SCHEMA_CHECK=$?

if [ $SCHEMA_CHECK -eq 0 ]; then
    echo "=== Schema check passed: is_active field exists! ==="
    
    # Run the direct test file first
    echo "Running direct test file..."
    docker compose -f docker-compose.test.yml run --rm \
      -e SKIP_MATERIALIZED_VIEWS=True \
      -e PYTEST_ADDOPTS="--no-header -v" \
      test \
      python -m pytest orders/test_direct.py -v
    
    # Get direct test exit code
    DIRECT_TEST_CODE=$?
    
    # Display direct test results
    if [ $DIRECT_TEST_CODE -eq 0 ]; then
        echo "=== Direct tests passed with proper integration! ==="
        
        # Run tests in the tests/ directory
        echo "Running orders/tests/ tests..."
        docker compose -f docker-compose.test.yml run --rm \
          -e SKIP_MATERIALIZED_VIEWS=True \
          -e PYTEST_ADDOPTS="--no-header -v" \
          test \
          python -m pytest orders/tests/test_models/ orders/tests/test_serializers/ orders/tests/test_views/ -v
        
        # Get sub-directory test exit code
        SUBDIR_TEST_CODE=$?
        
        # Display sub-directory test results
        if [ $SUBDIR_TEST_CODE -eq 0 ]; then
            echo "=== Subdirectory tests passed! ==="
            FINAL_CODE=0
        else
            echo "=== Subdirectory tests failed with exit code: $SUBDIR_TEST_CODE ==="
            FINAL_CODE=$SUBDIR_TEST_CODE
        fi
    else
        echo "=== Direct tests failed with exit code: $DIRECT_TEST_CODE ==="
        FINAL_CODE=$DIRECT_TEST_CODE
    fi
    
    # Stop the containers
    echo "Stopping test containers..."
    docker compose -f docker-compose.test.yml down
    
    # Return test exit code
    exit $FINAL_CODE
else
    echo "=== Schema check failed: is_active field missing ==="
    echo "=== Database setup is incorrect, tests will fail ==="
    # Stop the containers
    docker compose -f docker-compose.test.yml down
    exit 1
fi