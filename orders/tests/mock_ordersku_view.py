# orders/tests/mock_ordersku_view.py
import os
import pytest

class MockOrderSKUView:
    """
    Mock implementation of OrderSKUView for testing.
    This allows tests to run without requiring the actual materialized view to exist.
    """
    def __init__(self, transaction_id, sku_name, cases, picks, case_size=None, case_unit=None):
        self.transaction_id = transaction_id
        self.sku_name = sku_name
        self.cases = cases
        self.picks = picks
        self.case_size = case_size
        self.case_unit = case_unit

    def values(self, *args):
        return [{
            'sku_name': self.sku_name,
            'cases': self.cases,
            'picks': self.picks,
            'case_size': self.case_size,
            'case_unit': self.case_unit
        }]

def should_skip_materialized_view_tests():
    """
    Tests that require materialized views should be skipped if:
    1. The SKIP_MATERIALIZED_VIEWS environment variable is set to 'True'
    2. We're not using PostgreSQL
    3. We're not in a Docker environment and TestContainers is not being used
    """
    # Check environment variable
    if os.environ.get('SKIP_MATERIALIZED_VIEWS') == 'True':
        return True
        
    # If in Docker, materialized views should work
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true'
    if in_docker:
        return False
        
    # If using TestContainers with PostgreSQL, materialized views should work
    use_testcontainers = os.environ.get('USE_TESTCONTAINERS', 'False').lower() == 'true'
    if use_testcontainers:
        return False
        
    # Default to skipping materialized view tests for safety
    return True