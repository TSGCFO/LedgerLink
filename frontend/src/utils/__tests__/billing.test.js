import axios from 'axios';
import { billingApi, handleApiError } from '../apiClient';

// Mock axios
jest.mock('axios');

// Mock the logger
jest.mock('../logger', () => ({
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  logApiRequest: jest.fn(),
  logApiResponse: jest.fn(),
  logApiError: jest.fn(),
}));

describe('Billing API Utilities', () => {
  const mockBillingReports = [
    {
      id: '123e4567-e89b-12d3-a456-426614174000',
      customer: 1,
      customer_name: 'Test Company',
      start_date: '2025-01-01',
      end_date: '2025-02-01',
      total_amount: 1500.00,
      generated_at: '2025-01-15T10:30:00Z'
    },
    {
      id: '223e4567-e89b-12d3-a456-426614174001',
      customer: 2,
      customer_name: 'Another Company',
      start_date: '2025-02-01',
      end_date: '2025-03-01',
      total_amount: 2500.00,
      generated_at: '2025-02-15T10:30:00Z'
    }
  ];

  const mockBillingReport = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    customer: 1,
    customer_name: 'Test Company',
    start_date: '2025-01-01',
    end_date: '2025-02-01',
    total_amount: 1500.00,
    generated_at: '2025-01-15T10:30:00Z',
    preview_data: {
      orders: [
        {
          order_id: 'ORD-001',
          transaction_date: '2025-01-15',
          status: 'Completed',
          ship_to_name: 'John Smith',
          ship_to_address: '123 Test St',
          total_items: 5,
          line_items: 2,
          weight_lb: 10,
          services: [
            { service_id: 1, service_name: 'Standard Shipping', amount: 25.00 }
          ],
          total_amount: 150.00
        }
      ]
    },
    service_totals: {
      1: { name: 'Standard Shipping', amount: 25.00, order_count: 1 }
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });

  describe('billingApi.list', () => {
    it('should fetch billing reports with correct parameters', async () => {
      // Mock axios response
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          data: mockBillingReports
        }
      });

      // Call the API with some parameters
      const params = {
        search: 'Test',
        customer: 1,
        start_date: '2025-01-01',
        end_date: '2025-02-01'
      };
      
      const result = await billingApi.list(params);
      
      // Verify axios was called with correct URL and parameters
      expect(axios.get).toHaveBeenCalledWith(
        '/api/v1/billing/api/reports/?search=Test&customer=1&start_date=2025-01-01&end_date=2025-02-01',
        expect.any(Object)
      );
      
      // Check result structure
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockBillingReports);
    });
    
    it('should handle errors correctly', async () => {
      // Mock error response
      const errorResponse = {
        response: {
          status: 500,
          data: {
            detail: 'Internal server error'
          }
        }
      };
      
      axios.get = jest.fn().mockRejectedValue(errorResponse);
      
      // Call the API
      try {
        await billingApi.list();
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.status).toBe(500);
        expect(error.message).toBe('Internal server error');
      }
    });
  });
  
  describe('billingApi.generateReport', () => {
    it('should generate a billing report with correct parameters', async () => {
      // Mock axios response
      axios.post = jest.fn().mockResolvedValue({
        data: {
          success: true,
          data: mockBillingReport
        }
      });
      
      // Data to generate report
      const reportData = {
        customer: 1,
        start_date: '2025-01-01',
        end_date: '2025-02-01',
        output_format: 'preview'
      };
      
      const result = await billingApi.generateReport(reportData);
      
      // Verify axios was called with correct URL and data
      expect(axios.post).toHaveBeenCalledWith(
        '/api/v1/billing/api/generate-report/',
        reportData,
        expect.any(Object)
      );
      
      // Check result structure
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockBillingReport);
    });
    
    it('should handle network errors', async () => {
      // Mock network error
      const networkError = new TypeError('Failed to fetch');
      axios.post = jest.fn().mockRejectedValue(networkError);
      
      // Call the API
      try {
        await billingApi.generateReport({
          customer: 1,
          start_date: '2025-01-01',
          end_date: '2025-02-01'
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toBe('Failed to fetch');
      }
    });
    
    it('should handle server validation errors', async () => {
      // Mock validation error response
      const errorResponse = {
        response: {
          status: 400,
          data: {
            detail: 'Invalid date range',
            errors: {
              start_date: ['Start date must be before end date']
            }
          }
        }
      };
      
      axios.post = jest.fn().mockRejectedValue(errorResponse);
      
      // Call the API
      try {
        await billingApi.generateReport({
          customer: 1,
          start_date: '2025-02-01',
          end_date: '2025-01-01'
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.status).toBe(400);
        expect(error.message).toBe('Invalid date range');
        expect(error.data.errors.start_date[0]).toBe('Start date must be before end date');
      }
    });
  });
  
  describe('billingApi.get', () => {
    it('should fetch a specific billing report by ID', async () => {
      // Mock axios response
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          data: mockBillingReport
        }
      });
      
      const result = await billingApi.get('123e4567-e89b-12d3-a456-426614174000');
      
      // Verify axios was called with correct URL
      expect(axios.get).toHaveBeenCalledWith(
        '/api/v1/billing/api/reports/123e4567-e89b-12d3-a456-426614174000/',
        expect.any(Object)
      );
      
      // Check result structure
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockBillingReport);
    });
    
    it('should handle not found errors', async () => {
      // Mock 404 error
      const errorResponse = {
        response: {
          status: 404,
          data: {
            detail: 'Report not found'
          }
        }
      };
      
      axios.get = jest.fn().mockRejectedValue(errorResponse);
      
      // Call the API
      try {
        await billingApi.get('non-existent-id');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.status).toBe(404);
        expect(error.message).toBe('Report not found');
      }
    });
  });
  
  describe('billingApi.delete', () => {
    it('should delete a billing report by ID', async () => {
      // Mock axios response
      axios.delete = jest.fn().mockResolvedValue({
        data: {
          success: true
        }
      });
      
      const result = await billingApi.delete('123e4567-e89b-12d3-a456-426614174000');
      
      // Verify axios was called with correct URL
      expect(axios.delete).toHaveBeenCalledWith(
        '/api/v1/billing/api/reports/123e4567-e89b-12d3-a456-426614174000/',
        expect.any(Object)
      );
      
      // Check result structure
      expect(result.success).toBe(true);
    });
    
    it('should handle authorization errors', async () => {
      // Mock 403 error
      const errorResponse = {
        response: {
          status: 403,
          data: {
            detail: 'You do not have permission to delete this report'
          }
        }
      };
      
      axios.delete = jest.fn().mockRejectedValue(errorResponse);
      
      // Call the API
      try {
        await billingApi.delete('123e4567-e89b-12d3-a456-426614174000');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.status).toBe(403);
        expect(error.message).toBe('You do not have permission to delete this report');
      }
    });
  });
  
  describe('handleApiError', () => {
    it('should handle network errors', () => {
      const networkError = new TypeError('Failed to fetch');
      const message = handleApiError(networkError);
      expect(message).toContain('Network error');
    });
    
    it('should handle server errors with appropriate message', () => {
      const serverError = {
        status: 500,
        message: 'Internal server error',
        data: {
          detail: 'An unexpected error occurred'
        }
      };
      
      const message = handleApiError(serverError);
      expect(message).toContain('Server error');
    });
    
    it('should handle authentication errors', () => {
      const authError = {
        status: 401,
        message: 'Authentication failed',
        data: {
          detail: 'Invalid or expired token'
        }
      };
      
      const message = handleApiError(authError);
      expect(message).toContain('Please log in');
    });
    
    it('should handle validation errors', () => {
      const validationError = {
        status: 400,
        message: 'Invalid data provided',
        data: {
          detail: 'Invalid request data',
          errors: {
            start_date: ['This field is required'],
            end_date: ['This field is required']
          }
        }
      };
      
      const message = handleApiError(validationError);
      expect(message).toContain('Invalid request');
    });
    
    it('should handle missing resources', () => {
      const notFoundError = {
        status: 404,
        message: 'Resource not found',
        data: {
          detail: 'The requested report was not found'
        }
      };
      
      const message = handleApiError(notFoundError);
      expect(message).toContain('not found');
    });
  });
});