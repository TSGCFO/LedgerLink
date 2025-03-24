Customer Services Module
=====================

The Customer Services module links customers with available services. It serves as the foundation for the rules system, determining pricing and billing for customer services.

Models
------

.. automodule:: customer_services.models
   :members:
   :undoc-members:
   :show-inheritance:

Materialized Views
----------------

- **customer_services_customerserviceview**: Provides consolidated information about customer services

Serializers
----------

.. automodule:: customer_services.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: customer_services.views
   :members:
   :undoc-members:
   :show-inheritance:

API
---

.. automodule:: customer_services.api
   :members:
   :undoc-members:
   :show-inheritance:

Factory Testing Pattern
---------------------

The Customer Services module uses a custom factory pattern for testing due to materialized view dependencies and complex schema requirements. For more details, see :doc:`/testing/customer_services_testing`.

Tests
-----

The Customer Services app has comprehensive test coverage including integration with the Rules system. For more details, see :doc:`/testing/customer_services_testing`.
