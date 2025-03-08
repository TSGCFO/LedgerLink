#!/bin/bash
set -e

# Script to run LedgerLink Orders Model tests with PostgreSQL

echo "=== Running LedgerLink Orders Model Tests with PostgreSQL ==="

# Stop any existing test containers
docker compose -f docker-compose.test.yml down

# Build and start test containers
docker compose -f docker-compose.test.yml up --build -d db

# Wait a moment for the database to initialize
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# Create a direct test that verifies Customer and Order models work
echo "Running direct order model test..."
docker compose -f docker-compose.test.yml run --rm \
  -e SKIP_MATERIALIZED_VIEWS=True \
  test \
  /bin/bash -c 'cat > /tmp/direct_order_test.py << EOF
from django.test import TransactionTestCase
from django.db import connection
from customers.models import Customer
from orders.models import Order

class DirectOrderModelTest(TransactionTestCase):
    """Tests Order model directly with minimal dependencies."""
    
    def setUp(self):
        """Set up test data."""
        # Create the customer and order tables if they don\'t exist
        with connection.cursor() as cursor:
            # Check if customer table exists
            cursor.execute("SELECT to_regclass(\'public.customers_customer\')")
            if cursor.fetchone()[0] is None:
                cursor.execute("""
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
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                """)
        
            # Check if order table exists
            cursor.execute("SELECT to_regclass(\'public.orders_order\')")
            if cursor.fetchone()[0] is None:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders_order (
                    transaction_id BIGINT PRIMARY KEY,
                    reference_number VARCHAR(100),
                    ship_to_name VARCHAR(100),
                    ship_to_address VARCHAR(200),
                    ship_to_city VARCHAR(100),
                    ship_to_state VARCHAR(50),
                    ship_to_zip VARCHAR(20),
                    ship_to_country VARCHAR(100),
                    sku_quantity JSONB,
                    total_item_qty INTEGER,
                    line_items INTEGER,
                    weight_lb NUMERIC(10, 2),
                    volume_cuft NUMERIC(10, 2),
                    status VARCHAR(20),
                    priority VARCHAR(20),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    customer_id INTEGER REFERENCES customers_customer(id) ON DELETE CASCADE
                )
                """)
                
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Company LLC",
            email="test@example.com",
            is_active=True
        )
    
    def test_customer_is_active_field(self):
        """Test that the is_active field exists and works properly."""
        # Verify initial value
        self.assertTrue(self.customer.is_active)
        
        # Update and verify
        self.customer.is_active = False
        self.customer.save()
        
        # Refresh from DB
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)
    
    def test_order_creation(self):
        """Test that we can create an order."""
        order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="TEST-REF",
            ship_to_name="Test Recipient",
            ship_to_address="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            sku_quantity={"TEST-SKU": 10},
            total_item_qty=10,
            line_items=1,
            status="draft",
            priority="medium"
        )
        
        # Verify order was created
        self.assertEqual(order.transaction_id, 12345)
        self.assertEqual(order.customer, self.customer)
        
        # Verify we can query it back
        order_from_db = Order.objects.get(transaction_id=12345)
        self.assertEqual(order_from_db.reference_number, "TEST-REF")
        self.assertEqual(order_from_db.status, "draft")
EOF

echo "Running the direct order test..."
python -m unittest /tmp/direct_order_test.py
'

# Get the exit code
TEST_EXIT_CODE=$?

# Stop the containers
echo "Stopping test containers..."
docker compose -f docker-compose.test.yml down

# Display results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "=== Order model tests passed! ==="
    echo "=== Customer.is_active field works correctly! ==="
    exit 0
else
    echo "=== Order model tests failed with exit code: $TEST_EXIT_CODE ==="
    exit 1
fi