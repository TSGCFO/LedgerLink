#!/bin/bash
# Initialize the test database for LedgerLink with a cleaner approach

set -e  # Exit on any error

echo "=== Initializing LedgerLink Test Database (Clean Method) ==="

# Make sure docker is running and start with a clean state
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d db

echo "Waiting for PostgreSQL to initialize..."
sleep 10  # Simple sleep-based wait

# Apply migrations all at once to let Django handle the order
echo "Applying all migrations at once..."
docker compose -f docker-compose.test.yml run --rm test bash -c "
  SKIP_MATERIALIZED_VIEWS=True python manage.py migrate
"

# Create materialized views manually after migrations
echo "Creating materialized views manually..."
docker compose -f docker-compose.test.yml run --rm test bash -c "
cat << 'EOF' | python manage.py dbshell
-- Drop existing views first to avoid conflicts
DROP MATERIALIZED VIEW IF EXISTS orders_sku_view;
DROP MATERIALIZED VIEW IF EXISTS customer_services_customerserviceview;

-- Create orders_sku_view materialized view
CREATE MATERIALIZED VIEW orders_sku_view AS
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
CREATE MATERIALIZED VIEW customer_services_customerserviceview AS
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
CREATE UNIQUE INDEX orders_sku_view_order_sku_idx ON orders_sku_view(order_id, sku);
CREATE INDEX orders_sku_view_sku_idx ON orders_sku_view(sku);
CREATE INDEX orders_sku_view_customer_id_idx ON orders_sku_view(customer_id);
CREATE UNIQUE INDEX customer_services_customerserviceview_id_idx ON customer_services_customerserviceview(id);
EOF
"

echo "Creating initial test data..."
docker compose -f docker-compose.test.yml run --rm test python manage.py shell -c "
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Product
from services.models import Service
from orders.models import Order
import random

# Create test admin
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
    print('Created admin user')
else:
    admin_user = User.objects.get(username='admin')
    print('Using existing admin user')

# Create test customers
if not Customer.objects.filter(company_name='Test Company 1').exists():
    customer = Customer.objects.create(
        company_name='Test Company 1',
        legal_business_name='Test Company 1 LLC',
        email='test1@example.com',
        phone='555-123-0001',
        is_active=True
    )
    print('Created test customer')
else:
    customer = Customer.objects.get(company_name='Test Company 1')
    print('Using existing test customer')

# Create test products
if not Product.objects.filter(sku='SKU-0001').exists():
    product = Product.objects.create(
        product_name='Test Product 1',
        sku='SKU-0001',
        description='Test product description',
        price=99.99,
        weight_lb=1.5
    )
    print('Created test product')
else:
    product = Product.objects.get(sku='SKU-0001')
    print('Using existing test product')

# Create test services
if not Service.objects.filter(service_name='Test Service 1').exists():
    service = Service.objects.create(
        service_name='Test Service 1',
        description='Test service description',
        charge_type='fixed'
    )
    print('Created test service')
else:
    service = Service.objects.get(service_name='Test Service 1')
    print('Using existing test service')

# Create test orders
if not Order.objects.filter(transaction_id=100001).exists():
    Order.objects.create(
        transaction_id=100001,
        customer=customer,
        reference_number='REF-100001',
        ship_to_name='Test Recipient',
        ship_to_address='123 Test St',
        ship_to_city='Test City',
        ship_to_state='TS',
        ship_to_zip='12345',
        sku_quantity={'SKU-0001': 5},
        total_item_qty=5
    )
    print('Created test order')
else:
    print('Using existing test order')

# Create a few more orders with numeric transaction IDs for testing
for i in range(100002, 100005):
    if not Order.objects.filter(transaction_id=i).exists():
        Order.objects.create(
            transaction_id=i,
            customer=customer,
            reference_number=f'REF-{i}',
            ship_to_name='Test Recipient',
            ship_to_address='123 Test St',
            ship_to_city='Test City',
            ship_to_state='TS',
            ship_to_zip='12345',
            sku_quantity={'SKU-0001': random.randint(1, 10)},
            total_item_qty=random.randint(1, 10)
        )
        print(f'Created additional test order {i}')
"

echo "Dumping database for quick restore..."
docker compose -f docker-compose.test.yml exec db pg_dump -U postgres ledgerlink_test > test_db_dump.sql

echo "=== Database initialization complete ==="
echo "You can now run tests without recreating the database each time."
echo "To rebuild the database from scratch, use: ./run_billing_tests_docker.sh --rebuild"