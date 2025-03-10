#!/bin/bash
# Simple database initialization focused on fixing the order-product dependency issue

set -e  # Exit on any error

echo "=== Simple Database Initialization for LedgerLink ==="

# Clean start
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d db

echo "Waiting for PostgreSQL to initialize..."
sleep 10

# Migrate apps in a specific order to avoid dependency issues
echo "Applying migrations in the correct order..."

# Base apps
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate auth
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate admin
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate contenttypes
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate sessions

# Core models - customer and product first
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate customers
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate products

# Then orders (depends on products)
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate orders --fake-initial

# Then the rest
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate materials
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate services
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate shipping
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate rules
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate customer_services
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate inserts
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate bulk_operations

# Finally billing
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate billing

# Create a simple test order with numeric transaction_id
echo "Creating test data with numeric transaction_id..."
docker compose -f docker-compose.test.yml run --rm test python manage.py shell -c "
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Product
from orders.models import Order

# Create admin
User = get_user_model()
admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')

# Create test customer
customer = Customer.objects.create(
    company_name='Test Customer',
    legal_business_name='Test Company LLC',
    email='test@example.com',
    is_active=True
)

# Create test product
product = Product.objects.create(
    product_name='Test Product',
    sku='TEST-SKU-1',
    price=99.99
)

# Create test order with NUMERIC transaction_id (the key fix)
Order.objects.create(
    transaction_id=100001,  # Numeric ID, not string
    customer=customer,
    reference_number='REF-100001',
    sku_quantity={'TEST-SKU-1': 5},
    total_item_qty=5
)

print('Test data created successfully with numeric transaction_id')
"

echo "=== Simple Database Initialization Complete ==="
echo "Database is now ready for billing tests"