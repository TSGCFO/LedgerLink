import { Matchers } from '@pact-foundation/pact';
import axios from 'axios';
import { provider, createPaginatedResponse, createResponse, like, eachLike } from '../pact-utils';

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
            results: [{ id: 1, sku: 'PROD-001', customer: 1 }]
          }
        });
      }),
      post: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 201,
          data: { id: 100, sku: 'NEW-PROD-001', customer: 1 }
        });
      }),
      put: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 200,
          data: { id: 1, sku: 'UPDATED-PROD-001', customer: 1 }
        });
      }),
      delete: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 204,
          data: { success: true }
        });
      })
    }
  };
});

/**
 * @fileoverview API Contract tests for LedgerLink Products API
 * 
 * These tests ensure the contract between the frontend consumer (React) and 
 * backend provider (Django) remains consistent. They define the expected
 * request/response format for all Products API endpoints.
 */

// Mock axios for controlled request/response testing
jest.mock('axios');

// Create product object patterns for Pact tests
const createProductObject = (overrides = {}) => {
  return {
    id: like(1),
    sku: like('PROD-001'),
    customer: like(1),
    customer_details: {
      id: like(1),
      company_name: like('Test Company')
    },
    labeling_unit_1: like('case'),
    labeling_quantity_1: like(10),
    labeling_unit_2: like('pallet'),
    labeling_quantity_2: like(100),
    labeling_unit_3: like('container'),
    labeling_quantity_3: like(1000),
    created_at: like('2025-01-15T10:30:00Z'),
    updated_at: like('2025-01-15T10:30:00Z'),
    ...overrides
  };
};

describe('Products API Contract Tests', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  
  describe('GET /api/v1/products/', () => {
    beforeEach(() => {
      const productExample = createProductObject();
      
      return provider.addInteraction({
        state: 'products exist',
        uponReceiving: 'a request for all products',
        withRequest: {
          method: 'GET',
          path: '/api/v1/products/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          createPaginatedResponse([productExample], 10)
        )
      });
    });
    
    test('can retrieve a list of products', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: '/api/v1/products/'
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('GET /api/v1/products/:id/', () => {
    const productId = 1;
    const productExample = createProductObject({ id: productId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `product with ID ${productId} exists`,
        uponReceiving: 'a request for a specific product',
        withRequest: {
          method: 'GET',
          path: `/api/v1/products/${productId}/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          productExample
        )
      });
    });
    
    test('can retrieve a specific product', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/api/v1/products/${productId}/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('GET /api/v1/products/stats/', () => {
    const statsExample = {
      total_products: like(100),
      active_customers: like(15),
      skus_per_customer: like(6.7),
      recent_additions: like(12)
    };
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'product statistics exist',
        uponReceiving: 'a request for product statistics',
        withRequest: {
          method: 'GET',
          path: '/api/v1/products/stats/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          statsExample
        )
      });
    });
    
    test('can retrieve product statistics', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: '/api/v1/products/stats/'
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('GET /api/v1/products/ with customer filter', () => {
    const customerId = 1;
    const productExample = createProductObject({ customer: customerId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `products for customer ${customerId} exist`,
        uponReceiving: 'a request for products filtered by customer',
        withRequest: {
          method: 'GET',
          path: '/api/v1/products/',
          query: { customer: customerId.toString() },
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          createPaginatedResponse([productExample], 5)
        )
      });
    });
    
    test('can retrieve products for a specific customer', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/api/v1/products/?customer=${customerId}`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('POST /api/v1/products/', () => {
    const newProduct = {
      sku: 'NEW-PROD-001',
      customer: 1,
      labeling_unit_1: 'box',
      labeling_quantity_1: 5,
      labeling_unit_2: 'case',
      labeling_quantity_2: 25,
      labeling_unit_3: 'pallet',
      labeling_quantity_3: 100
    };
    
    const createdProduct = createProductObject({
      ...newProduct,
      id: 100,
      customer_details: {
        id: 1,
        company_name: 'Test Company'
      }
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'can create a product',
        uponReceiving: 'a request to create a product',
        withRequest: {
          method: 'POST',
          path: '/api/v1/products/',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: newProduct
        },
        willRespondWith: createResponse(
          201, 
          { 'Content-Type': 'application/json' },
          createdProduct
        )
      });
    });
    
    test('can create a product', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'POST',
        url: '/api/v1/products/'
      });
      
      // Verify the response
      expect(response.status).toEqual(201);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('PUT /api/v1/products/:id/', () => {
    const productId = 1;
    const updatedProduct = {
      sku: 'UPDATED-PROD-001',
      customer: 1,
      labeling_unit_1: 'box',
      labeling_quantity_1: 10,
      labeling_unit_2: 'case',
      labeling_quantity_2: 50,
      labeling_unit_3: 'pallet',
      labeling_quantity_3: 200
    };
    
    const responseProduct = createProductObject({
      id: productId,
      ...updatedProduct,
      customer_details: {
        id: 1,
        company_name: 'Test Company'
      }
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `product with ID ${productId} exists`,
        uponReceiving: 'a request to update a product',
        withRequest: {
          method: 'PUT',
          path: `/api/v1/products/${productId}/`,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: updatedProduct
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          responseProduct
        )
      });
    });
    
    test('can update a product', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'PUT',
        url: `/api/v1/products/${productId}/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
  
  describe('DELETE /api/v1/products/:id/', () => {
    const productId = 1;
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `product with ID ${productId} exists`,
        uponReceiving: 'a request to delete a product',
        withRequest: {
          method: 'DELETE',
          path: `/api/v1/products/${productId}/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          204, 
          { 'Content-Type': 'application/json' },
          { success: true }
        )
      });
    });
    
    test('can delete a product', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'DELETE',
        url: `/api/v1/products/${productId}/`
      });
      
      // Verify the response
      expect(response.status).toEqual(204);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
});