#!/bin/bash
# Initialize the test database for LedgerLink in the correct order

set -e  # Exit on any error

echo "=== Initializing LedgerLink Test Database ==="

# Make sure docker is running
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d db

echo "Waiting for PostgreSQL to initialize..."
sleep 10  # Simple sleep-based wait

# Run migrations in a controlled order to avoid dependency issues
echo "Applying migrations in controlled order..."

# Base Django apps first
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate auth
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate contenttypes
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate admin
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate sessions

# Core data models next (in dependency order)
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate customers
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate products
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate materials
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate services
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate rules

# Then dependent models
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate orders
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate shipping
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate inserts
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate customer_services
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate bulk_operations

# Finally billing (depends on many others)
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate billing

# Create materialized views (without depending on migrations)
echo "Creating materialized views manually..."
docker compose -f docker-compose.test.yml run --rm test bash -c "
cat << 'EOF' | python manage.py dbshell
-- Create orders_sku_view materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS orders_sku_view AS
SELECT 
    o.transaction_id as order_id,
    o.customer_id,
    o.reference_number,
    o.ship_to_name,
    o.ship_to_city,
    o.ship_to_state,
    o.ship_to_zip,
    o.status,
    o.priority,
    jsonb_object_keys(o.sku_quantity) as sku,
    (o.sku_quantity->>jsonb_object_keys(o.sku_quantity))::integer as quantity,
    p.id as product_id,
    p.product_name,
    p.sku as product_sku,
    p.description as product_description,
    p.price as product_price
FROM 
    orders_order o
LEFT JOIN products_product p ON 
    jsonb_object_keys(o.sku_quantity) = p.sku;

-- Create customer_services_customerserviceview materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS customer_services_customerserviceview AS
SELECT 
    cs.id,
    cs.customer_id,
    cs.service_id,
    cs.created_at,
    cs.updated_at,
    s.service_name,
    s.description as service_description,
    s.charge_type,
    c.company_name,
    c.legal_business_name,
    c.email,
    c.phone,
    c.address,
    c.city,
    c.state,
    c.zip,
    c.country,
    c.business_type,
    c.is_active as customer_is_active
FROM customer_services_customerservice cs
JOIN services_service s ON cs.service_id = s.id
JOIN customers_customer c ON cs.customer_id = c.id;

-- Create indices on materialized views
CREATE UNIQUE INDEX IF NOT EXISTS orders_sku_view_order_sku_idx ON orders_sku_view(order_id, sku);
CREATE INDEX IF NOT EXISTS orders_sku_view_sku_idx ON orders_sku_view(sku);
CREATE INDEX IF NOT EXISTS orders_sku_view_customer_id_idx ON orders_sku_view(customer_id);
CREATE UNIQUE INDEX IF NOT EXISTS customer_services_customerserviceview_id_idx ON customer_services_customerserviceview(id);
EOF
"

echo "Creating initial test data..."
docker compose -f docker-compose.test.yml run --rm test python manage.py shell -c "
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Product
from services.models import Service
from orders.models import Order

# Create test admin
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
    print('Created admin user')

# Create test customers
if not Customer.objects.filter(company_name='Test Company 1').exists():
    Customer.objects.create(
        company_name='Test Company 1',
        legal_business_name='Test Company 1 LLC',
        email='test1@example.com',
        phone='555-123-0001',
        is_active=True
    )
    print('Created test customers')

# Create test products
if not Product.objects.filter(sku='SKU-0001').exists():
    Product.objects.create(
        product_name='Test Product 1',
        sku='SKU-0001',
        description='Test product description',
        price=99.99,
        weight_lb=1.5
    )
    print('Created test products')

# Create test services
if not Service.objects.filter(service_name='Test Service 1').exists():
    Service.objects.create(
        service_name='Test Service 1',
        description='Test service description',
        charge_type='fixed'
    )
    print('Created test services')

# Create test orders
if not Order.objects.filter(transaction_id=100001).exists():
    cust = Customer.objects.first()
    if cust:
        Order.objects.create(
            transaction_id=100001,
            customer=cust,
            reference_number='REF-100001',
            ship_to_name='Test Recipient',
            ship_to_address='123 Test St',
            ship_to_city='Test City',
            ship_to_state='TS',
            ship_to_zip='12345',
            sku_quantity={'SKU-0001': 5},
            total_item_qty=5
        )
        print('Created test orders')
"

echo "Dumping database for quick restore..."
docker compose -f docker-compose.test.yml exec db pg_dump -U postgres ledgerlink_test > test_db_dump.sql

echo "=== Database initialization complete ==="
echo "You can now run tests without recreating the database each time."
echo "To rebuild the database from scratch, use: ./run_billing_tests_docker.sh --rebuild"