import { Pact } from '@pact-foundation/pact';
import axios from 'axios';
import { provider, createPaginatedResponse, createResponse } from '../pact-utils';
import apiClient from '../apiClient';

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
    id: Pact.like(1),
    sku: Pact.like('PROD-001'),
    customer: Pact.like(1),
    customer_details: {
      id: Pact.like(1),
      company_name: Pact.like('Test Company')
    },
    labeling_unit_1: Pact.like('case'),
    labeling_quantity_1: Pact.like(10),
    labeling_unit_2: Pact.like('pallet'),
    labeling_quantity_2: Pact.like(100),
    labeling_unit_3: Pact.like('container'),
    labeling_quantity_3: Pact.like(1000),
    created_at: Pact.like('2025-01-15T10:30:00Z'),
    updated_at: Pact.like('2025-01-15T10:30:00Z'),
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
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get('/api/v1/products/', {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.count).toBeDefined();
      expect(response.data.results).toBeDefined();
      expect(response.data.results.length).toBeGreaterThan(0);
      
      // Verify against the contract
      return provider.verify();
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
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/products/${productId}/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.id).toEqual(productId);
      expect(response.data.sku).toBeDefined();
      expect(response.data.customer_details).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('GET /api/v1/products/stats/', () => {
    const statsExample = {
      total_products: Pact.like(100),
      active_customers: Pact.like(15),
      skus_per_customer: Pact.like(6.7),
      recent_additions: Pact.like(12)
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
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get('/api/v1/products/stats/', {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.total_products).toBeDefined();
      expect(response.data.active_customers).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
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
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/products/?customer=${customerId}`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.count).toBeDefined();
      expect(response.data.results).toBeDefined();
      expect(response.data.results.length).toBeGreaterThan(0);
      expect(response.data.results[0].customer).toEqual(customerId);
      
      // Verify against the contract
      return provider.verify();
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
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post('/api/v1/products/', newProduct, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(201);
      expect(response.data.id).toBeDefined();
      expect(response.data.sku).toEqual(newProduct.sku);
      expect(response.data.customer).toEqual(newProduct.customer);
      expect(response.data.customer_details).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
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
      // Set up axios to use the mock provider's URL
      axios.put.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.put(`/api/v1/products/${productId}/`, updatedProduct, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.id).toEqual(productId);
      expect(response.data.sku).toEqual(updatedProduct.sku);
      expect(response.data.labeling_quantity_1).toEqual(updatedProduct.labeling_quantity_1);
      
      // Verify against the contract
      return provider.verify();
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
      // Set up axios to use the mock provider's URL
      axios.delete.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.delete(`/api/v1/products/${productId}/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(204);
      expect(response.data.success).toBe(true);
      
      // Verify against the contract
      return provider.verify();
    });
  });
});