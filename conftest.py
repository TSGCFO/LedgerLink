"""
Pytest configuration file with common fixtures.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from test_utils.factories import (
    UserFactory, CustomerFactory, ProductFactory, OrderFactory, BasicRuleFactory
)

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def auth_api_client():
    """Return an authenticated API client."""
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def admin_api_client():
    """Return an API client authenticated as admin."""
    admin = UserFactory(is_staff=True, is_superuser=True)
    client = APIClient()
    client.force_authenticate(user=admin)
    return client, admin


@pytest.fixture
def test_user():
    """Create and return a test user."""
    return UserFactory()


@pytest.fixture
def test_customer(test_user):
    """Create and return a test customer."""
    return CustomerFactory(created_by=test_user)


@pytest.fixture
def test_product(test_user):
    """Create and return a test product."""
    return ProductFactory(created_by=test_user)


@pytest.fixture
def test_order(test_customer, test_user):
    """Create and return a test order."""
    return OrderFactory(customer=test_customer, created_by=test_user)


@pytest.fixture
def test_basic_rule(test_user):
    """Create and return a test basic rule."""
    return BasicRuleFactory(created_by=test_user)


@pytest.fixture
def sample_db_data(test_user):
    """
    Create a sample dataset with customers, products, and orders.
    
    Returns:
        Dictionary containing all created objects
    """
    # Create 3 customers
    customers = [CustomerFactory(created_by=test_user) for _ in range(3)]
    
    # Create 5 products
    products = [ProductFactory(created_by=test_user) for _ in range(5)]
    
    # Create 2 orders for each customer
    orders = []
    for customer in customers:
        orders.extend([OrderFactory(customer=customer, created_by=test_user) for _ in range(2)])
    
    # Create 3 rules
    rules = [BasicRuleFactory(created_by=test_user) for _ in range(3)]
    
    return {
        'user': test_user,
        'customers': customers,
        'products': products,
        'orders': orders,
        'rules': rules
    }