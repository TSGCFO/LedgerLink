import { Matchers } from '@pact-foundation/pact';
import path from 'path';

/**
 * @fileoverview Pact utilities for contract testing in LedgerLink
 * 
 * This module provides common utilities for API contract testing with Pact.
 * It includes:
 * - Response formatters for consistent API interactions
 * - Object generators for common entity types
 * - Helper functions for simulating paginated responses
 */

// Export Matchers directly for easier use
export const { like, term, eachLike, somethingLike } = Matchers;

// Create a mock provider helper that doesn't require a server
export const mockProvider = (consumer, provider) => {
  const interactions = [];
  
  return {
    consumer,
    provider,
    addInteraction: (interaction) => {
      interactions.push(interaction);
      return Promise.resolve();
    },
    writePact: () => {
      console.log(`Writing pact file for ${consumer} -> ${provider}`);
      return Promise.resolve();
    },
    verify: () => Promise.resolve(),
    setup: () => Promise.resolve(),
    finalize: () => Promise.resolve(),
    removeInteractions: () => {
      interactions.length = 0;
      return Promise.resolve();
    },
    mockRequest: (req) => {
      // Find matching interaction
      const interaction = interactions.find(int => {
        const withReq = int.withRequest;
        
        // Match method
        if (withReq.method !== req.method) return false;
        
        // Split URL and query parameters
        let urlPath = req.url;
        let queryParams = {};
        
        if (req.url.includes('?')) {
          const [path, query] = req.url.split('?');
          urlPath = path;
          
          // Parse query parameters
          query.split('&').forEach(param => {
            const [key, value] = param.split('=');
            queryParams[key] = value;
          });
        }
        
        // Match path
        const pathMatch = new RegExp(`^${withReq.path.replace(/\{[^}]+\}/g, '[^/]+')}$`);
        if (!pathMatch.test(urlPath)) return false;
        
        // Match query params if defined in the interaction
        if (withReq.query) {
          for (const [key, value] of Object.entries(withReq.query)) {
            if (queryParams[key] !== value) return false;
          }
        }
        
        return true;
      });
      
      if (interaction) {
        return Promise.resolve(interaction.willRespondWith);
      }
      
      return Promise.reject(new Error(`No matching interaction found for ${req.method} ${req.url}`));
    },
    getInteractions: () => interactions
  };
};

// Create a backward-compatible provider for existing tests
export const provider = mockProvider('LedgerLinkFrontend', 'LedgerLinkAPI');

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
    id: like('123e4567-e89b-12d3-a456-426614174000'),
    company_name: like('Test Company'),
    contact_name: like('John Doe'),
    email: like('john@example.com'),
    phone: like('555-1234'),
    address: like('123 Main St'),
    city: like('Testville'),
    state: like('TS'),
    zip_code: like('12345'),
    country: like('US'),
    is_active: like(true),
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
    count: like(count),
    next: next ? like(next) : null,
    previous: previous ? like(previous) : null,
    results: eachLike(results[0], { min: results.length })
  };
};