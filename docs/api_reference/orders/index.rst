Orders Module
============

The Orders module manages order transactions in LedgerLink. It includes integration with materialized views (OrderSKUView) for efficient SKU analysis.

Models
------

.. automodule:: orders.models
   :members:
   :undoc-members:
   :show-inheritance:

Materialized Views
----------------

The Orders app uses materialized views that require PostgreSQL:

- **orders_sku_view**: Provides consolidated information about SKUs in orders

.. note::
   Materialized views require PostgreSQL and are not compatible with SQLite. See :doc:`/testing/testing_sqlite_issues` for more information.

Serializers
----------

.. automodule:: orders.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: orders.views
   :members:
   :undoc-members:
   :show-inheritance:

API
---

.. automodule:: orders.api
   :members:
   :undoc-members:
   :show-inheritance:

Tests
-----

The Orders app has comprehensive test coverage including specialized tests for materialized views. For more details, see :doc:`/testing/orders_testing`.
