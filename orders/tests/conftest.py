"""
Order-specific test configuration.
This conftest.py extends the main root conftest.py.
"""
import os
import random
import pytest
from django.db import connection

# Import main project's fixtures
from conftest import django_db_setup, _django_db_helper

# Import local utils
from orders.tests.utils import verify_field_exists, verify_model_schema
from customers.models import Customer
from orders.models import Order

# Set environment variables
if 'SKIP_MATERIALIZED_VIEWS' not in os.environ:
    os.environ['SKIP_MATERIALIZED_VIEWS'] = 'True'

# Mark all tests in this directory as django_db tests
pytestmark = pytest.mark.django_db

@pytest.fixture(scope='session', autouse=True)
def verify_order_schema(django_db_blocker):
    """Verify the Order model schema before running tests."""
    django_db_blocker.unblock()
    try:
        # Verify Customer model has is_active field
        success, message = verify_field_exists(Customer, 'is_active')
        if not success:
            pytest.fail(f"Schema verification failed: {message}")
        
        # Verify Order model schema
        order_success, order_messages = verify_model_schema(Order)
        if not order_success:
            pytest.fail(f"Order schema verification failed: {order_messages}")
        
        # If we get here, schema verification passed
        print("Schema verification for orders app passed!")
    finally:
        django_db_blocker.restore()

@pytest.fixture
def generate_transaction_id():
    """
    Generate a unique transaction ID for order tests.
    This helps prevent primary key violations when multiple tests create orders.
    """
    def _generate_id():
        # Generate a random 6-digit ID between 100000 and 999999
        return random.randint(100000, 999999)
    
    return _generate_id

@pytest.fixture
def customer():
    """Fixture to provide a customer for order tests."""
    # Create with unique email to avoid conflicts
    unique_id = str(random.randint(10000, 99999))
    return Customer.objects.create(
        company_name=f"Test Company {unique_id}",
        legal_business_name=f"Test Company LLC {unique_id}",
        email=f"test{unique_id}@example.com",
        phone=f"123-456-{unique_id[-4:]}",
        is_active=True
    )

@pytest.fixture
def order(customer, generate_transaction_id):
    """Fixture to provide an order for tests."""
    transaction_id = generate_transaction_id()
    return Order.objects.create(
        transaction_id=transaction_id,
        customer=customer,
        reference_number=f"REF-TEST-{transaction_id}",
        ship_to_name="Order Recipient",
        ship_to_address="456 Order St",
        ship_to_city="Order City",
        ship_to_state="OS",
        ship_to_zip="54321",
        sku_quantity={"TEST-SKU-A": 10, "TEST-SKU-B": 5},
        total_item_qty=15,
        line_items=2,
        status="draft",
        priority="medium"
    )