# Materials App Testing Improvements

## Overview

As part of our efforts to increase test coverage across LedgerLink to 90%+, we've implemented comprehensive test improvements for the materials app. This document outlines the new tests added, the testing approach, and next steps.

## Added Tests

### 1. Integration Tests (`test_integration.py`)

These tests ensure that the various components of the materials app work together correctly:

- `MaterialBoxPriceIntegrationTest`: Tests the integration between Material and BoxPrice models and APIs
  - Tests multiple API calls in succession
  - Tests concurrent updates to both models
  - Tests batch operations creating multiple instances
  - Tests edge case calculations (very small and very large dimensions)
  - Tests error handling for invalid data

- `MaterialAPIPerformanceTest`: Tests performance aspects of Material API
  - Tests pagination
  - Tests large batch creation

- `BoxPriceCalculationTest`: Tests advanced calculations
  - Tests price per cubic unit (volume)
  - Tests surface area calculations
  - Tests price per surface area
  - Tests boxes with extreme aspect ratios
  - Tests precision in calculations

### 2. Security Tests (`test_security.py`)

These tests ensure that the materials APIs are secure and validate permissions correctly:

- `MaterialPermissionTest`: Tests different user permission levels
  - Tests unauthenticated access is blocked
  - Tests read-only users can only view data
  - Tests standard users can create and update but not delete
  - Tests admin users have full access

- `BoxPriceSecurityTest`: Tests security aspects of BoxPrice API
  - Tests authentication is required
  - Tests authenticated users can access protected endpoints
  - Tests protection against SQL injection
  - Tests validation of field constraints (max length, decimal precision)

### 3. Contract Tests (`test_pact_provider.py`)

These tests ensure that the backend API contracts match the frontend expectations:

- `MaterialPactProviderTest`: Tests Material API contracts
  - Sets up provider states: "materials exist", "no materials exist", "specific material exists"
  - Verifies contracts against frontend consumer Pact definitions

- `BoxPricePactProviderTest`: Tests BoxPrice API contracts
  - Sets up provider states: "box prices exist", "no box prices exist", "specific box price exists"
  - Verifies contracts against frontend consumer Pact definitions

### 4. Performance Tests (`test_performance.py`)

These tests verify that the materials APIs perform well under load:

- `MaterialQueryPerformanceTest`: Tests database query performance
  - Tests query count for listing materials
  - Tests query execution time
  - Tests performance of queries by name

- `BoxPriceQueryPerformanceTest`: Tests database query performance
  - Tests bulk create performance
  - Tests complex filtering performance

- `APILoadTest`: Tests API endpoints under load
  - Tests repeated API calls
  - Tests interleaved API calls to different endpoints
  - Tests concurrent read/write operations

## Testing Approach

The tests follow the established patterns from the billing app, which already has 90%+ coverage. The key aspects of the testing approach include:

1. **Comprehensive Testing**: Testing all aspects of models, serializers, and API endpoints
2. **Edge Case Coverage**: Testing boundary conditions and extreme values
3. **Error Handling**: Testing error responses for invalid inputs
4. **Permission Testing**: Testing different user roles and access levels
5. **API Contract Testing**: Ensuring backend and frontend agree on API structure
6. **Performance Testing**: Verifying API performance under load
7. **Integration Testing**: Testing components working together

## Next Steps

1. **Fix Docker Testing Environment**:
   - Address credential issues with Docker
   - Update the Docker configurations to use pre-built psycopg2 wheels compatible with Python 3.11

2. **Implement Similar Tests for Shipping App**:
   - Follow the same patterns to bring shipping app tests to 90%+ coverage

3. **Implement Similar Tests for Inserts App**:
   - Follow the same patterns to bring inserts app tests to 90%+ coverage

4. **Frontend Tests**:
   - Implement corresponding frontend component tests for materials
   - Implement Cypress end-to-end tests for materials flows

## Conclusion

The materials app now has comprehensive backend tests that should bring its coverage to 90%+ once the Docker testing environment issues are resolved. The test patterns established here can be replicated for the shipping and inserts apps to ensure consistent testing across the entire LedgerLink application.