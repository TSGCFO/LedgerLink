Bulk Operations Module
===================

The Bulk Operations module facilitates data import functionality, allowing users to upload CSV or Excel files for bulk data import.

Components
---------

.. automodule:: bulk_operations.components
   :members:
   :undoc-members:
   :show-inheritance:

Services
-------

.. automodule:: bulk_operations.services
   :members:
   :undoc-members:
   :show-inheritance:

API
---

.. automodule:: bulk_operations.api
   :members:
   :undoc-members:
   :show-inheritance:

Frontend Components
----------------

The module includes several frontend React components:

- **BulkOperations.jsx**: Main container component
- **TemplateSelector.jsx**: Template selection interface
- **FileUploader.jsx**: File upload with validation
- **ValidationProgress.jsx**: Progress display during validation
- **ResultsSummary.jsx**: Results display after import
- **ErrorDisplay.jsx**: Error boundary component

Tests
-----

The Bulk Operations module has comprehensive test coverage (92%) including extensive testing for the backend services, API endpoints, and frontend components. Tests include both unit tests and end-to-end testing. For more details, see :doc:`/testing/bulk_operations_testing`.
