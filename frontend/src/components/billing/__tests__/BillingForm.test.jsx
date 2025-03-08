import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '../../../utils/test-utils';
import BillingForm from '../BillingForm';
import axios from 'axios';
import { billingApi, customerApi, handleApiError } from '../../../utils/apiClient';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }), // No ID by default (create mode)
}));

// Mock the API client
jest.mock('../../../utils/apiClient', () => {
  return {
    billingApi: {
      generateReport: jest.fn(),
      get: jest.fn()
    },
    customerApi: {
      list: jest.fn()
    },
    handleApiError: jest.fn(error => 'Error: ' + (error.message || 'An unknown error occurred'))
  };
});

// Mock the logger
jest.mock('../../../utils/logger', () => ({
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  logApiRequest: jest.fn(),
  logApiResponse: jest.fn(),
  logApiError: jest.fn(),
}));

describe('BillingForm Component', () => {
  const mockCustomers = [
    { id: 1, company_name: 'Test Company', contact_name: 'John Doe' },
    { id: 2, company_name: 'Another Company', contact_name: 'Jane Smith' }
  ];
  
  const mockReportResponse = {
    success: true,
    data: {
      id: '123e4567-e89b-12d3-a456-426614174000',
      customer: 1,
      customer_name: 'Test Company',
      start_date: '2025-01-01',
      end_date: '2025-02-01',
      report_id: 'REP-123',
      total_amount: 1500.00,
      generated_at: '2025-01-15T10:30:00Z',
      output_format: 'json'
    }
  };

  const mockPreviewResponse = {
    success: true,
    data: {
      id: '123e4567-e89b-12d3-a456-426614174000',
      customer: 1,
      customer_name: 'Test Company',
      start_date: '2025-01-01',
      end_date: '2025-02-01',
      total_amount: 1500.00,
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
          },
          {
            order_id: 'ORD-002',
            transaction_date: '2025-01-20',
            status: 'Completed',
            ship_to_name: 'Jane Smith',
            ship_to_address: '456 Test Ave',
            total_items: 3,
            line_items: 1,
            weight_lb: 5,
            services: [
              { service_id: 1, service_name: 'Standard Shipping', amount: 15.00 }
            ],
            total_amount: 75.00
          }
        ]
      },
      service_totals: {
        1: { name: 'Standard Shipping', amount: 40.00, order_count: 2 }
      }
    }
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API client responses
    customerApi.list.mockResolvedValue({
      success: true,
      data: mockCustomers
    });
    
    billingApi.generateReport.mockResolvedValue(mockReportResponse);
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders form with all fields', async () => {
    render(<BillingForm />);
    
    // Initially should show loading state for customer dropdown
    expect(screen.getByLabelText(/customer/i)).toBeInTheDocument();
    
    // Wait for form to load completely
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Check all form fields are rendered
    expect(screen.getByLabelText(/customer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/export format/i)).toBeInTheDocument();
    
    // Check submit button is present
    expect(screen.getByRole('button', { name: /generate report/i })).toBeInTheDocument();
  });
  
  test('validates required fields', async () => {
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Click submit without filling required fields
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Check validation errors
    await waitFor(() => {
      expect(screen.getByText(/customer is required/i)).toBeInTheDocument();
      expect(screen.getByText(/start date is required/i)).toBeInTheDocument();
      expect(screen.getByText(/end date is required/i)).toBeInTheDocument();
    });
    
    // Should not call API
    expect(billingApi.generateReport).not.toHaveBeenCalled();
  });
  
  test('submits form with valid data', async () => {
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Fill out form
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField); // Open dropdown
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set start date - mock the DatePicker onChange
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    // Set end date - similar approach
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Expecting API to be called with correct data
    await waitFor(() => {
      expect(billingApi.generateReport).toHaveBeenCalledTimes(1);
      expect(billingApi.generateReport).toHaveBeenCalledWith(
        expect.objectContaining({
          customer: 1,
          start_date: '2025-01-01',
          end_date: '2025-02-01',
          output_format: expect.any(String)
        })
      );
    });
    
    // Should show success message
    expect(screen.getByText(/report generated successfully/i)).toBeInTheDocument();
  });
  
  test('handles API errors on submit', async () => {
    // Mock API error
    billingApi.generateReport.mockRejectedValueOnce({
      status: 400,
      message: 'Invalid date range',
      data: {
        detail: 'Invalid date range'
      }
    });
    
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Fill out form minimally
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set dates
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '03/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(handleApiError).toHaveBeenCalled();
      expect(screen.getByText(/Error: Invalid date range/i)).toBeInTheDocument();
    });
  });
  
  test('validates end date is after start date', async () => {
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Fill out form with invalid date range
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set start date after end date
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '03/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Check validation errors
    await waitFor(() => {
      expect(screen.getByText(/end date must be after start date/i)).toBeInTheDocument();
    });
    
    // Should not call API
    expect(billingApi.generateReport).not.toHaveBeenCalled();
  });
  
  test('fetches an existing report in edit mode', async () => {
    // Mock the useParams to return an ID (edit mode)
    jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ id: '123' });
    
    // Mock the API response for fetching a report
    billingApi.get.mockResolvedValue({
      success: true,
      data: mockReportResponse.data
    });
    
    render(<BillingForm />);
    
    // Should call the API to fetch the report
    await waitFor(() => {
      expect(billingApi.get).toHaveBeenCalledWith('123');
    });
    
    // Form should be populated with the report data
    await waitFor(() => {
      // Should display the report summary section
      expect(screen.getByText(/report summary/i)).toBeInTheDocument();
      expect(screen.getByText(/total amount/i)).toBeInTheDocument();
      expect(screen.getByText(/generated/i)).toBeInTheDocument();
    });
  });
  
  test('shows preview dialog when generating report with preview format', async () => {
    // Mock the API response for preview data
    billingApi.generateReport.mockResolvedValueOnce(mockPreviewResponse);
    
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Fill out form
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set dates
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Set output format to preview (directly modify the formData)
    const formatSelect = screen.getByLabelText(/export format/i);
    fireEvent.mouseDown(formatSelect);
    
    // Force preview mode by modifying the component's state
    Object.defineProperty(BillingForm.prototype, 'output_format', {
      value: 'preview',
      writable: true
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Wait for the API call
    await waitFor(() => {
      expect(billingApi.generateReport).toHaveBeenCalledTimes(1);
    });
    
    // Should show the preview dialog
    await waitFor(() => {
      expect(screen.getByText(/report preview/i)).toBeInTheDocument();
      
      // Check for order data in the preview
      expect(screen.getByText('ORD-001')).toBeInTheDocument();
      expect(screen.getByText('ORD-002')).toBeInTheDocument();
      expect(screen.getByText('Service Summary')).toBeInTheDocument();
    });
    
    // Check export button in dialog
    expect(screen.getByRole('button', { name: /export as excel/i })).toBeInTheDocument();
    
    // Test closing the dialog
    fireEvent.click(screen.getByRole('button', { name: /close/i }));
    
    // Dialog should be closed
    await waitFor(() => {
      expect(screen.queryByText(/report preview/i)).not.toBeInTheDocument();
    });
  });
  
  test('can export report from preview dialog', async () => {
    // Mock the API responses
    billingApi.generateReport.mockResolvedValueOnce(mockPreviewResponse);
    // Second call for export
    billingApi.generateReport.mockResolvedValueOnce({
      success: true,
      data: new Blob(['mock export data'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    });
    
    // Mock URL.createObjectURL and document functions for file download
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    const mockAppendChild = jest.fn();
    const mockRemoveChild = jest.fn();
    const mockClick = jest.fn();
    
    // Save original document.createElement
    const originalCreateElement = document.createElement;
    
    // Mock document.createElement to return a mock anchor element
    document.createElement = jest.fn().mockImplementation((tagName) => {
      if (tagName === 'a') {
        return {
          href: '',
          download: '',
          click: mockClick
        };
      }
      return originalCreateElement.call(document, tagName);
    });
    
    // Mock document.body methods
    document.body.appendChild = mockAppendChild;
    document.body.removeChild = mockRemoveChild;
    
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Fill out form
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set dates
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Force preview mode
    Object.defineProperty(BillingForm.prototype, 'output_format', {
      value: 'preview',
      writable: true
    });
    
    // Submit form to show preview
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Wait for preview dialog
    await waitFor(() => {
      expect(screen.getByText(/report preview/i)).toBeInTheDocument();
    });
    
    // Click export button in dialog
    fireEvent.click(screen.getByRole('button', { name: /export as excel/i }));
    
    // Verify the export API call
    await waitFor(() => {
      expect(billingApi.generateReport).toHaveBeenCalledTimes(2);
      expect(billingApi.generateReport).toHaveBeenLastCalledWith(
        expect.objectContaining({
          output_format: 'excel'
        })
      );
      
      // Verify the file download process
      expect(URL.createObjectURL).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
      expect(URL.revokeObjectURL).toHaveBeenCalled();
    });
    
    // Restore original document methods
    document.createElement = originalCreateElement;
  });
  
  test('handles network errors during API calls', async () => {
    // Mock a network error
    customerApi.list.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    
    render(<BillingForm />);
    
    // Should display error message
    await waitFor(() => {
      expect(handleApiError).toHaveBeenCalled();
      expect(screen.getByText(/error: failed to fetch/i)).toBeInTheDocument();
    });
  });
  
  test('handles server errors during API calls', async () => {
    // Mock a server error
    customerApi.list.mockRejectedValueOnce({
      status: 500,
      message: 'Internal server error',
      data: {
        detail: 'An unexpected error occurred'
      }
    });
    
    render(<BillingForm />);
    
    // Should display error message
    await waitFor(() => {
      expect(handleApiError).toHaveBeenCalled();
      expect(screen.getByText(/error: internal server error/i)).toBeInTheDocument();
    });
  });
});