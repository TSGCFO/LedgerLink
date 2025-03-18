# orders/tests/__init__.py
# Tests for the orders app

# Import key components to make them available at the package level
from .mock_ordersku_view import should_skip_materialized_view_tests

# Make factories available directly from the package
from .factories import (
    OrderFactory, SubmittedOrderFactory, ShippedOrderFactory,
    DeliveredOrderFactory, CancelledOrderFactory
)