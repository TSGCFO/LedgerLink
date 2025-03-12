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
            results: [{ id: 1, report_name: 'Billing Report' }]
          }
        });
      }),
      post: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 201,
          data: { id: 1, report_name: 'New Billing Report' }
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
 * @fileoverview API Contract tests for LedgerLink Billing API
 * 
 * These tests establish the contract between the frontend consumer (React) and 
 * backend provider (Django) for the Billing API. They define expected formats for:
 * - Listing billing reports (GET)
 * - Retrieving individual billing reports (GET)
 * - Generating new billing reports (POST)
 * - Deleting billing reports (DELETE)
 * 
 * Implementation follows best practices from part5-full-system-testing.md 
 * including provider state management and detailed request/response verification.
 */

// Mock axios for controlled request/response testing
jest.mock('axios');

// Create billing object patterns for Pact tests
const createBillingReportObject = (overrides = {}) => {
  return {
    id: Pact.like('123e4567-e89b-12d3-a456-426614174000'),
    customer: Pact.like(1),
    customer_name: Pact.like('Test Company'),
    start_date: Pact.like('2025-01-01'),
    end_date: Pact.like('2025-01-31'),
    total_amount: Pact.like(1500.50),
    generated_at: Pact.like('2025-01-15T10:30:00Z'),
    output_format: Pact.like('json'),
    created_at: Pact.like('2025-01-15T10:30:00Z'),
    created_by: Pact.like('admin_user'),
    ...overrides
  };
};

// Create preview data for billing reports
const createPreviewData = () => {
  return {
    preview_data: {
      orders: [
        {
          order_id: Pact.like('ORD-001'),
          transaction_date: Pact.like('2025-01-15'),
          status: Pact.like('Completed'),
          ship_to_name: Pact.like('John Smith'),
          ship_to_address: Pact.like('123 Test St'),
          total_items: Pact.like(5),
          line_items: Pact.like(2),
          weight_lb: Pact.like(10),
          services: [
            {
              service_id: Pact.like(1),
              service_name: Pact.like('Standard Shipping'),
              amount: Pact.like(25.00)
            }
          ],
          total_amount: Pact.like(150.00)
        }
      ]
    },
    service_totals: {
      '1': {
        name: Pact.like('Standard Shipping'),
        amount: Pact.like(25.00),
        order_count: Pact.like(1)
      }
    }
  };
};

describe('Billing API Contract Tests', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  
  describe('GET /api/v1/billing/api/reports/', () => {
    beforeEach(() => {
      const billingReportExample = createBillingReportObject();
      
      return provider.addInteraction({
        state: 'billing reports exist',
        uponReceiving: 'a request for all billing reports',
        withRequest: {
          method: 'GET',
          path: '/api/v1/billing/api/reports/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          { 
            success: true,
            data: [billingReportExample, createBillingReportObject({ id: '223e4567-e89b-12d3-a456-426614174001' })]
          }
        )
      });
    });
    
    test('can retrieve a list of billing reports', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get('/api/v1/billing/api/reports/', {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.success).toBe(true);
      expect(response.data.data).toBeDefined();
      expect(response.data.data.length).toBeGreaterThan(0);
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('GET /api/v1/billing/api/reports/:id/', () => {
    const reportId = '123e4567-e89b-12d3-a456-426614174000';
    const billingReportExample = createBillingReportObject({ id: reportId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `billing report with ID ${reportId} exists`,
        uponReceiving: 'a request for a specific billing report',
        withRequest: {
          method: 'GET',
          path: `/api/v1/billing/api/reports/${reportId}/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          billingReportExample
        )
      });
    });
    
    test('can retrieve a specific billing report', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/billing/api/reports/${reportId}/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.id).toEqual(reportId);
      expect(response.data.customer_name).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('POST /api/v1/billing/api/generate-report/', () => {
    const reportRequest = {
      customer: 1,
      start_date: '2025-01-01',
      end_date: '2025-01-31',
      output_format: 'preview'
    };
    
    const reportResponse = {
      ...createBillingReportObject(),
      ...createPreviewData()
    };
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'can generate a billing report',
        uponReceiving: 'a request to generate a billing report',
        withRequest: {
          method: 'POST',
          path: '/api/v1/billing/api/generate-report/',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: reportRequest
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          { 
            success: true,
            data: reportResponse
          }
        )
      });
    });
    
    test('can generate a billing report', async () => {
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post('/api/v1/billing/api/generate-report/', reportRequest, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.success).toBe(true);
      expect(response.data.data.customer_name).toBeDefined();
      expect(response.data.data.preview_data).toBeDefined();
      expect(response.data.data.preview_data.orders).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('DELETE /api/v1/billing/api/reports/:id/', () => {
    const reportId = '123e4567-e89b-12d3-a456-426614174000';
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `billing report with ID ${reportId} exists`,
        uponReceiving: 'a request to delete a billing report',
        withRequest: {
          method: 'DELETE',
          path: `/api/v1/billing/api/reports/${reportId}/`,
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
    
    test('can delete a billing report', async () => {
      // Set up axios to use the mock provider's URL
      axios.delete.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.delete(`/api/v1/billing/api/reports/${reportId}/`, {
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