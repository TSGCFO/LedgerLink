Billing Module
===========

The Billing module handles billing calculations, reports, and invoicing in LedgerLink. The v2 implementation includes advanced API endpoints for generating and managing billing reports.

Models
------

.. automodule:: billing.models
   :members:
   :undoc-members:
   :show-inheritance:

Calculator
---------

.. automodule:: billing.calculator
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: billing.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: billing.views
   :members:
   :undoc-members:
   :show-inheritance:

API
---

.. automodule:: billing.api
   :members:
   :undoc-members:
   :show-inheritance:

V2 API Requirements
----------------

The Billing V2 API includes upgraded endpoints for report generation, listing, and downloading. For details, see :doc:`/api/requirements`.

Tests
-----

The Billing module has comprehensive test coverage (90%+) including tests for the billing calculator and rule integration. Recent updates include additional tests for tier-based pricing calculations.
