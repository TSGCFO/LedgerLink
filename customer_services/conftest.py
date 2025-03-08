"""
Pytest configuration for customer_services tests.
"""
import os
import pytest

# Set environment variables for testing
os.environ['SKIP_MATERIALIZED_VIEWS'] = 'True'

# Mark all tests in this directory as django_db tests
pytestmark = pytest.mark.django_db