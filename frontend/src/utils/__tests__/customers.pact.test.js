import { Matchers } from '@pact-foundation/pact';
import axios from 'axios';
import { provider, createCustomerObject, createPaginatedResponse, createResponse, like, eachLike } from '../pact-utils';

// Mock apiClient
jest.mock('../apiClient', () => {
  return {
    __esModule: true,
    default: {
      get: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 200,
          data: {
            count: 10,
            results: [{ id: '123e4567-e89b-12d3-a456-426614174000', company_name: 'Test Company' }]
          }
        });
      }),
      post: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 201,
          data: { id: '123e4567-e89b-12d3-a456-426614174001', company_name: 'New Test Company' }
        });
      })
    }
  };
});

/**
 * @fileoverview API Contract tests for LedgerLink Customers API
 * 
 * These tests define the contract between the frontend consumer (React) and 
 * backend provider (Django) for the Customers API. They ensure consistent
 * request/response formats for customer operations including:
 * - Listing customers (with pagination)
 * - Retrieving individual customer details
 * - Creating new customers
 * 
 * Following the testing guidelines from part5-full-system-testing.md
 */

// Mock axios for controlled request/response testing
jest.mock('axios');

describe('Customer API Contract Tests', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  
  describe('GET /api/v1/customers/', () => {
    beforeEach(() => {
      const customerExample = createCustomerObject();
      
      return provider.addInteraction({
        state: 'customers exist',
        uponReceiving: 'a request for all customers',
        withRequest: {
          method: 'GET',
          path: '/api/v1/customers/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          {},
          createPaginatedResponse([customerExample], 10)
        )
      });
    });
    
    test('can retrieve a list of customers', async () => {
      // Call the API
      const response = await provider.mockRequest({
        method: 'GET',
        url: '/api/v1/customers/'
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('GET /api/v1/customers/:id/', () => {
    const customerId = '123e4567-e89b-12d3-a456-426614174000';
    const customerExample = createCustomerObject({ id: customerId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `customer with ID ${customerId} exists`,
        uponReceiving: 'a request for a specific customer',
        withRequest: {
          method: 'GET',
          path: `/api/v1/customers/${customerId}/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(200, {}, customerExample)
      });
    });
    
    test('can retrieve a specific customer', async () => {
      // Call the API
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/api/v1/customers/${customerId}/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('POST /api/v1/customers/', () => {
    const newCustomer = {
      company_name: 'New Test Company',
      contact_name: 'Jane Smith',
      email: 'jane@example.com',
      phone: '555-5678',
      address: '456 Testing Ave',
      city: 'Testopolis',
      state: 'TS',
      zip_code: '54321',
      country: 'US',
      is_active: true
    };
    
    const createdCustomer = createCustomerObject({
      ...newCustomer,
      id: '123e4567-e89b-12d3-a456-426614174001'
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'can create a customer',
        uponReceiving: 'a request to create a customer',
        withRequest: {
          method: 'POST',
          path: '/api/v1/customers/',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: newCustomer
        },
        willRespondWith: createResponse(201, {}, createdCustomer)
      });
    });
    
    test('can create a customer', async () => {
      // Call the API
      const response = await provider.mockRequest({
        method: 'POST',
        url: '/api/v1/customers/'
      });
      
      // Verify the response
      expect(response.status).toEqual(201);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
});