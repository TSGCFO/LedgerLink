Rules Module
==========

The Rules module implements business logic for determining service pricing and conditions. It supports basic rules, advanced rules, and case-based tier configurations.

Models
------

.. automodule:: rules.models
   :members:
   :undoc-members:
   :show-inheritance:

Rule Evaluator
------------

.. automodule:: rules.evaluator
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: rules.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: rules.views
   :members:
   :undoc-members:
   :show-inheritance:

API
---

.. automodule:: rules.api
   :members:
   :undoc-members:
   :show-inheritance:

Rule Operators
------------

The Rules system supports numerous operators for condition evaluation. Recent updates have fixed issues with the "not equals" (`ne`) and "not contains" (`ncontains`) operators. For more details, see the CHANGELOG.

Case-Based Tiers
--------------

Advanced rules support case-based tiers with min/max ranges and values in tier_config. The implementation allows for complex pricing scenarios based on quantity tiers.

Tests
-----

The Rules module has comprehensive test coverage (92%+) including extensive testing for all operators and edge cases. Recent fixes have been thoroughly tested to ensure proper rule evaluation.
