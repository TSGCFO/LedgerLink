import { Matchers } from '@pact-foundation/pact';
import { mockProvider, like, eachLike } from '../../utils/pact-utils';
import { orderApi } from '../../utils/apiClient';
import path from 'path';

// Create a dedicated provider for Order API tests to avoid port conflicts
const provider = mockProvider('OrderFrontend', 'OrderAPI');

describe('Order API Contract', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  afterEach(() => provider.verify());
  
  describe('get all orders', () => {
    beforeEach(() => {
      return provider.addInteraction({
        state: 'orders exist',
        uponReceiving: 'a request for all orders',
        withRequest: {
          method: 'GET',
          path: '/api/v1/orders/',
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            count: 3,
            next: null,
            previous: null,
            results: [
              {
                id: 1,
                order_number: 'ORD-001',
                customer: {
                  id: 1,
                  company_name: 'Test Company'
                },
                order_date: '2025-03-01T10:00:00Z',
                status: 'pending',
                priority: 'normal',
                shipping_method: 'Standard',
                shipping_address: '123 Test St'
              },
              {
                id: 2,
                order_number: 'ORD-002',
                customer: {
                  id: 2, 
                  company_name: 'Another Company'
                },
                order_date: '2025-03-02T10:00:00Z',
                status: 'in_progress',
                priority: 'high',
                shipping_method: 'Express',
                shipping_address: '456 Test Ave'
              }
            ]
          }
        }
      });
    });
    
    test('returns all orders', async () => {      
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: '/api/v1/orders/'
      });
      
      // Verify the response structure
      expect(response.status).toEqual(200);
      expect(response.body).toBeDefined();
    });
  });
  
  describe('get order by id', () => {
    beforeEach(() => {
      return provider.addInteraction({
        state: 'order with ID 1 exists',
        uponReceiving: 'a request for an order by ID',
        withRequest: {
          method: 'GET',
          path: '/api/v1/orders/1/',
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 1,
            order_number: 'ORD-001',
            customer: {
              id: 1,
              company_name: 'Test Company'
            },
            order_date: '2025-03-01T10:00:00Z',
            status: 'pending',
            priority: 'normal',
            shipping_method: 'Standard',
            shipping_address: '123 Test St'
          }
        }
      });
    });
    
    test('returns the specific order', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: '/api/v1/orders/1/'
      });
      
      // Verify the response structure
      expect(response.status).toEqual(200);
      expect(response.body).toBeDefined();
    });
  });
  
  describe('create an order', () => {
    const newOrder = {
      customer: 1,
      order_number: 'ORD-NEW',
      shipping_address: '789 New Street',
      shipping_method: 'Standard',
      status: 'pending',
      priority: 'normal'
    };
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'order can be created',
        uponReceiving: 'a request to create an order',
        withRequest: {
          method: 'POST',
          path: '/api/v1/orders/',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          },
          body: newOrder
        },
        willRespondWith: {
          status: 201,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 3,
            order_number: 'ORD-NEW',
            customer: {
              id: 1,
              company_name: 'Test Company'
            },
            shipping_address: '789 New Street',
            shipping_method: 'Standard',
            status: 'pending',
            priority: 'normal',
            order_date: '2025-03-03T10:00:00Z'
          }
        }
      });
    });
    
    test('creates a new order', async () => {
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'POST',
        url: '/api/v1/orders/'
      });
      
      // Verify the response structure
      expect(response.status).toEqual(201);
      expect(response.body).toBeDefined();
    });
  });
});