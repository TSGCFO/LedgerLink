# Decision Log

This file records architectural and implementation decisions using a list format.
2025-03-22 14:56:34 - Log of updates made.

## Decision

* Use separate parameter handling for "All" services vs. specific services in billing calculator
* Implement frontend logic to omit customer_services parameter when "All" is selected
* Create two different code paths for handling service filtering in the backend

## Rationale 

* Frontend needs a user-friendly way to select "All" services or specific ones
* Omitting the parameter is cleaner than sending a complete list of all service IDs
* Backend needs flexibility to handle both selection modes efficiently
* Different business rules may apply to different services

## Implementation Details

* Frontend (BillingReportGenerator.jsx): 
  * When "All" is selected, omit customer_services parameter in API call
  * When specific services are selected, send list of service IDs
* Backend API (views.py):
  * Converts customer_services parameter to customer_service_ids
  * Handles different input formats (list, comma-separated string)
* Calculator (calculator.py):
  * Uses None for customer_service_ids to indicate "all services"
  * Filters service list based on IDs when specific services are selected
  * Currently having issues when specific services are selected