#!/bin/bash
set -e

echo "=== Running Simplified Billing Tests ==="

# Create a test database
echo "Creating test database..."
createdb -h localhost -U postgres ledgerlink_test

# Set up essential tables
echo "Setting up essential tables..."
psql -h localhost -U postgres ledgerlink_test << EOF
-- Authentication and users
CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Core tables
CREATE TABLE IF NOT EXISTS customers_customer (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    legal_business_name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(50),
    business_type VARCHAR(50),
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS services_service (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    description TEXT,
    charge_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_services_customerservice (
    id SERIAL PRIMARY KEY,
    unit_price NUMERIC(10,2) NOT NULL,
    is_active BOOLEAN NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers_customer(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services_service(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

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

CREATE TABLE IF NOT EXISTS billing_billingreport (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers_customer(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    report_data JSONB,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    updated_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS billing_billingreportdetail (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES billing_billingreport(id) ON DELETE CASCADE,
    order_id BIGINT NOT NULL REFERENCES orders_order(transaction_id) ON DELETE CASCADE,
    service_breakdown JSONB,
    total_amount NUMERIC(10,2) NOT NULL
);
EOF

# Run the tests directly with pytest
echo "Running billing tests..."
DJANGO_SETTINGS_MODULE=LedgerLink.settings.test \
DATABASE_URL=postgres://postgres:postgres@localhost/ledgerlink_test \
SKIP_MATERIALIZED_VIEWS=True \
DISABLE_CUSTOM_MIGRATIONS=True \
python -m pytest billing/tests/ -v

# Clean up
echo "Cleaning up..."
dropdb -h localhost -U postgres ledgerlink_test

echo "=== Billing Tests Completed ==="