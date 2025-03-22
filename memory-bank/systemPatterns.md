# System Patterns

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-03-22 14:56:49 - Log of updates made.

## Coding Patterns

* Django REST framework views with consistent response format:
  * `{'success': True/False, 'data': data}` response structure
  * Error handling with appropriate HTTP status codes
  * Consistent error response format
* Frontend component structure:
  * Material-UI based components
  * Form validation with error display
  * Progressive loading indicators
  * Consistent API service integration

## Architectural Patterns

* Service-oriented design:
  * Services defined independently
  * Customer-services mapping for customization
  * Rule-based service application
* Billing calculation pipeline:
  1. Input validation
  2. Service filtering (all vs. specific)
  3. Order retrieval
  4. Rule evaluation
  5. Cost calculation
  6. Report generation
* Parameter handling:
  * Omitted parameters (None) indicating "use all" or "use default"
  * Explicit parameters for specific selections
  * Type conversion and validation for parameters

## Testing Patterns

* Test scripts organized by module/feature
* Comprehensive test coverage approach
* Docker-based testing environment
* Testing with different service selection combinations
* Integration testing between frontend and backend