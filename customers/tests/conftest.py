import pytest
from django.contrib.auth import get_user_model
from pytest_factoryboy import register
from rest_framework.test import APIClient

from customers.tests.factories import CustomerFactory

# Register factories
register(CustomerFactory)

User = get_user_model()

@pytest.fixture
def api_client():
    """Return an authenticated API client."""
    return APIClient()

@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword'
    )

@pytest.fixture
def regular_user():
    """Create and return a regular user."""
    return User.objects.create_user(
        username='user',
        email='user@example.com',
        password='userpassword'
    )

@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Return an API client authenticated as admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client