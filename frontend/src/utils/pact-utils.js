import { Pact } from '@pact-foundation/pact';
import path from 'path';

/**
 * @fileoverview Pact utilities for contract testing in LedgerLink
 * 
 * This module provides common utilities for API contract testing with Pact.
 * It includes:
 * - Pact provider configuration
 * - Response formatters for consistent API interactions
 * - Object generators for common entity types
 * - Helper functions for simulating paginated responses
 */

// Pact mock service setup for consumer tests
export const provider = new Pact({
  consumer: 'LedgerLinkFrontend',
  provider: 'LedgerLinkAPI',
  log: path.resolve(process.cwd(), 'logs', 'pact.log'),
  logLevel: 'warn',
  dir: path.resolve(process.cwd(), 'pacts'),
  spec: 2,
  cors: true,
  pactfileWriteMode: 'merge' // Allows multiple test files to contribute to the same pact
});

/**
 * Creates an expected response for a Pact API interaction
 * 
 * @param {number} status - HTTP status code
 * @param {object} headers - Response headers
 * @param {object} body - Response body
 * @returns {object} - Pact response object
 */
export const createResponse = (status, headers = {}, body = {}) => {
  return {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body
  };
};

/**
 * Creates a customer object for Pact tests with default values
 * 
 * @param {object} overrides - Fields to override default values
 * @returns {object} - Customer object
 */
export const createCustomerObject = (overrides = {}) => {
  return {
    id: Pact.like('123e4567-e89b-12d3-a456-426614174000'),
    company_name: Pact.like('Test Company'),
    contact_name: Pact.like('John Doe'),
    email: Pact.like('john@example.com'),
    phone: Pact.like('555-1234'),
    address: Pact.like('123 Main St'),
    city: Pact.like('Testville'),
    state: Pact.like('TS'),
    zip_code: Pact.like('12345'),
    country: Pact.like('US'),
    is_active: Pact.like(true),
    ...overrides
  };
};

/**
 * Creates a list of objects for Pact tests
 * 
 * @param {function} itemGenerator - Function that generates an item
 * @param {number} count - Number of items to generate
 * @returns {Array} - List of generated items
 */
export const createList = (itemGenerator, count = 3) => {
  const list = [];
  for (let i = 0; i < count; i++) {
    list.push(itemGenerator(i));
  }
  return list;
};

/**
 * Creates a paginated response for Pact tests
 * 
 * @param {Array} results - List of items
 * @param {number} count - Total count
 * @param {string|null} next - URL for next page
 * @param {string|null} previous - URL for previous page
 * @returns {object} - Paginated response
 */
export const createPaginatedResponse = (results, count, next = null, previous = null) => {
  return {
    count: Pact.like(count),
    next: next ? Pact.like(next) : null,
    previous: previous ? Pact.like(previous) : null,
    results: Pact.eachLike(results[0], { min: results.length })
  };
};