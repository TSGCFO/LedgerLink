Shipping Module
============

The Shipping module handles shipping information for orders. It includes models for both Canadian (CAD) and US shipping workflows.

Models
------

.. automodule:: shipping.models
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: shipping.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: shipping.views
   :members:
   :undoc-members:
   :show-inheritance:

API
---

.. automodule:: shipping.api
   :members:
   :undoc-members:
   :show-inheritance:

Key Features
----------

- CADShipping model with Canadian-specific fields
- USShipping model with US-specific fields and status tracking
- Delivery date calculation
- Address validation
- Tax calculation for Canadian shipping
- Status management for US shipping

Tests
-----

The Shipping module has comprehensive test coverage (87%) including tests for model relationships, calculated fields, validation logic, and API endpoints. For more details, see :doc:`/testing/shipping_testing`.
