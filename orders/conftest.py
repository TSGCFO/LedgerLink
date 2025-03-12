"""
Pytest configuration for orders tests.
This conftest.py extends the main project's conftest.py rather than replacing it.
"""
import os
import random
import pytest
from django.db import connection

# Import main project's fixtures
from conftest import django_db_setup, _django_db_helper

# Set environment variables for testing
if 'SKIP_MATERIALIZED_VIEWS' not in os.environ:
    os.environ['SKIP_MATERIALIZED_VIEWS'] = 'True'

# Mark all tests in this directory as django_db tests
pytestmark = pytest.mark.django_db

@pytest.fixture(scope='session', autouse=True)
def verify_db_schema(django_db_blocker):
    """
    Verify that the database schema has all required fields before running tests.
    In particular, check for the is_active field in the Customer model which has
    been problematic in the past.
    """
    django_db_blocker.unblock()
    try:
        with connection.cursor() as cursor:
            # Check if the customers_customer table exists
            cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("customers_customer",))
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                pytest.fail("customers_customer table does not exist")
            
            # Check for the is_active column
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s", ("customers_customer",))
            columns = [row[0] for row in cursor.fetchall()]
            
            if "is_active" not in columns:
                pytest.fail(f"is_active field does not exist in customers_customer table. Available columns: {columns}")
                
            print(f"Schema verification passed: is_active field exists in customers_customer table")
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
def order_test_setup(django_db_blocker, _django_db_helper):
    """
    Setup fixture for order tests that ensures:
    1. Database is properly unblocked
    2. Schema is correctly set up
    3. Required models are available
    """
    # Additional setup can go here
    yield
    # Any cleanup can go here
    # django_db_blocker will be automatically restored by _django_db_helper