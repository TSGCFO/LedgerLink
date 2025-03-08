import { Pact } from '@pact-foundation/pact';
import { orderApi } from '../../utils/apiClient';
import path from 'path';

const mockPort = 8080;
const mockServer = `http://localhost:${mockPort}`;

// Configure the provider
const provider = new Pact({
  port: mockPort,
  log: path.resolve(process.cwd(), 'logs', 'pact.log'),
  dir: path.resolve(process.cwd(), 'pacts'),
  consumer: 'OrderFrontend',
  provider: 'OrderAPI'
});

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
      // Setup testing API
      const originalRequest = orderApi.list;
      orderApi.list = () => {
        return fetch(`${mockServer}/api/v1/orders/`, {
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        }).then(res => res.json());
      };
      
      // Call API method
      const result = await orderApi.list();
      
      // Verify response
      expect(result.count).toEqual(3);
      expect(result.results).toHaveLength(2);
      expect(result.results[0].order_number).toEqual('ORD-001');
      expect(result.results[1].order_number).toEqual('ORD-002');
      
      // Restore original implementation
      orderApi.list = originalRequest;
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
      // Setup testing API
      const originalRequest = orderApi.get;
      orderApi.get = (id) => {
        return fetch(`${mockServer}/api/v1/orders/${id}/`, {
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        }).then(res => res.json());
      };
      
      // Call API method
      const result = await orderApi.get(1);
      
      // Verify response
      expect(result.id).toEqual(1);
      expect(result.order_number).toEqual('ORD-001');
      expect(result.customer.company_name).toEqual('Test Company');
      
      // Restore original implementation
      orderApi.get = originalRequest;
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
      // Setup testing API
      const originalRequest = orderApi.create;
      orderApi.create = (data) => {
        return fetch(`${mockServer}/api/v1/orders/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          },
          body: JSON.stringify(data)
        }).then(res => res.json());
      };
      
      // Call API method
      const result = await orderApi.create(newOrder);
      
      // Verify response
      expect(result.id).toEqual(3);
      expect(result.order_number).toEqual('ORD-NEW');
      expect(result.shipping_address).toEqual('789 New Street');
      
      // Restore original implementation
      orderApi.create = originalRequest;
    });
  });
});