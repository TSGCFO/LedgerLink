# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-03-22 14:55:53 - Log of updates made will be appended as footnotes to the end of this file.

## Project Goal

* LedgerLink appears to be a billing and order management system with Django backend and React frontend
* The system helps track customer orders, services, and generates billing reports
* The primary goal is to accurately calculate billing costs for services provided to customers

## Key Features

* Customer management
* Service configuration and management
* Order tracking and processing
* Billing report generation with customizable service selection
* Multiple export formats (JSON, CSV, PDF)
* Rule-based service application

## Overall Architecture

* Backend: Django with RESTful API endpoints
* Frontend: React-based UI with Material-UI components
* Database: PostgreSQL (inferred from configuration files)
* Modular design with separate apps for different functionality:
  * customers - Customer data management
  * services - Service definition
  * customer_services - Mapping services to customers
  * billing/Billing_V2 - Billing calculation and report generation
  * orders - Order management
  * products - Product catalog
  * rules - Business rule definitions and evaluation