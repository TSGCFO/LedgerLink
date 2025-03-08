import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '../../../utils/test-utils';
import BillingList from '../BillingList';
import axios from 'axios';
import { billingApi, customerApi, handleApiError } from '../../../utils/apiClient';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

// Mock API client
jest.mock('../../../utils/apiClient', () => {
  const originalModule = jest.requireActual('../../../utils/apiClient');
  return {
    ...originalModule,
    billingApi: {
      list: jest.fn(),
      generateReport: jest.fn(),
      delete: jest.fn()
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

describe('BillingList Component', () => {
  const mockCustomers = [
    { id: 1, company_name: 'Test Company', contact_name: 'John Doe' },
    { id: 2, company_name: 'Another Company', contact_name: 'Jane Smith' }
  ];
  
  const mockBillingData = {
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

  // Mock billing reports list
  const mockBillingReports = {
    success: true,
    data: [
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
    ]
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API client responses
    customerApi.list.mockResolvedValue({
      success: true,
      data: mockCustomers
    });
    
    billingApi.generateReport.mockResolvedValue(mockBillingData);
    billingApi.list.mockResolvedValue(mockBillingReports);
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders billing report form with all fields', async () => {
    render(<BillingList />);
    
    // Check the initial form fields are rendered
    expect(screen.getByLabelText(/customer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /calculate/i })).toBeInTheDocument();
    
    // Wait for customer dropdown to load
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
  });
  
  test('validates form inputs before calculation', async () => {
    render(<BillingList />);
    
    // Click calculate without filling required fields
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/please select a customer and date range/i)).toBeInTheDocument();
    });
    
    // API should not be called
    expect(billingApi.generateReport).not.toHaveBeenCalled();
  });
  
  test('shows error when start date is after end date', async () => {
    render(<BillingList />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Select customer
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set dates in wrong order
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '03/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // Should show date validation error
    await waitFor(() => {
      expect(screen.getByText(/start date must be before end date/i)).toBeInTheDocument();
    });
    
    // API should not be called
    expect(billingApi.generateReport).not.toHaveBeenCalled();
  });
  
  test('displays billing data when calculate is clicked with valid inputs', async () => {
    render(<BillingList />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Select customer
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set valid dates
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // API should be called with correct data
    await waitFor(() => {
      expect(billingApi.generateReport).toHaveBeenCalledTimes(1);
      expect(billingApi.generateReport).toHaveBeenCalledWith(
        expect.objectContaining({
          customer: 1,
          start_date: '2025-01-01',
          end_date: '2025-02-01',
          output_format: 'preview'
        })
      );
    });
    
    // Table should be displayed with billing data
    await waitFor(() => {
      // Look for order IDs in the table
      expect(screen.getByText('ORD-001')).toBeInTheDocument();
      expect(screen.getByText('ORD-002')).toBeInTheDocument();
      
      // Check for service totals
      expect(screen.getByText('Standard Shipping')).toBeInTheDocument();
      expect(screen.getByText('$40.00')).toBeInTheDocument();
      
      // Check for overall total
      expect(screen.getByText('$1,500.00')).toBeInTheDocument();
    });
  });
  
  test('handles API errors when calculating billing', async () => {
    // Mock API error
    billingApi.generateReport.mockRejectedValueOnce({
      status: 500,
      message: 'Server error occurred',
      data: {
        detail: 'Server error occurred'
      }
    });
    
    render(<BillingList />);
    
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Select customer
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    
    await waitFor(() => {
      expect(screen.getAllByRole('option')[0]).toBeInTheDocument();
    });
    
    // Select the first option
    const options = screen.getAllByRole('option');
    fireEvent.click(options[0]);
    
    // Set valid dates
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(handleApiError).toHaveBeenCalled();
      expect(screen.getByText(/Error: Server error occurred/i)).toBeInTheDocument();
    });
    
    // No table should be displayed
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });
  
  test('fetches and displays saved billing reports', async () => {
    render(<BillingList />);
    
    // Wait for both API calls (customers and billing reports)
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
      expect(billingApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Check if saved reports are displayed
    expect(screen.getByText(/saved reports/i)).toBeInTheDocument();
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('Another Company')).toBeInTheDocument();
    
    // Should show dates in human-readable format
    expect(screen.getByText('Jan 1, 2025 - Feb 1, 2025')).toBeInTheDocument();
    expect(screen.getByText('Feb 1, 2025 - Mar 1, 2025')).toBeInTheDocument();
    
    // Should show amounts properly formatted
    expect(screen.getByText('$1,500.00')).toBeInTheDocument();
    expect(screen.getByText('$2,500.00')).toBeInTheDocument();
  });
  
  test('allows loading a saved billing report', async () => {
    render(<BillingList />);
    
    // Wait for API calls
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
      expect(billingApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Find and click the "View" button for the first report
    const viewButtons = screen.getAllByRole('button', { name: /view/i });
    fireEvent.click(viewButtons[0]);
    
    // The report data should be loaded
    await waitFor(() => {
      expect(billingApi.generateReport).toHaveBeenCalledTimes(1);
      expect(billingApi.generateReport).toHaveBeenCalledWith(
        expect.objectContaining({
          customer: 1,
          report_id: '123e4567-e89b-12d3-a456-426614174000'
        })
      );
    });
    
    // Table should be displayed with billing data
    await waitFor(() => {
      expect(screen.getByText('ORD-001')).toBeInTheDocument();
      expect(screen.getByText('ORD-002')).toBeInTheDocument();
    });
  });
  
  test('can delete a saved billing report', async () => {
    // Mock successful delete
    billingApi.delete.mockResolvedValue({ success: true });
    
    render(<BillingList />);
    
    // Wait for API calls
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
      expect(billingApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Get all delete buttons
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    
    // Click the delete button for the first report
    fireEvent.click(deleteButtons[0]);
    
    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/are you sure you want to delete this report/i)).toBeInTheDocument();
    });
    
    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);
    
    // Delete API should be called
    await waitFor(() => {
      expect(billingApi.delete).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000');
      expect(billingApi.list).toHaveBeenCalledTimes(2); // Called again to refresh
    });
    
    // Success message should be shown
    expect(screen.getByText(/report deleted successfully/i)).toBeInTheDocument();
  });
  
  test('can cancel deletion of a billing report', async () => {
    render(<BillingList />);
    
    // Wait for API calls
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
      expect(billingApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Get all delete buttons
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    
    // Click the delete button for the first report
    fireEvent.click(deleteButtons[0]);
    
    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/are you sure you want to delete this report/i)).toBeInTheDocument();
    });
    
    // Cancel deletion
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    // Delete API should not be called
    expect(billingApi.delete).not.toHaveBeenCalled();
    
    // Dialog should be closed
    await waitFor(() => {
      expect(screen.queryByText(/are you sure you want to delete this report/i)).not.toBeInTheDocument();
    });
  });
  
  test('handles API errors when loading saved reports', async () => {
    // Mock API error for billing list
    billingApi.list.mockRejectedValueOnce({
      status: 500,
      message: 'Failed to load saved reports',
      data: {
        detail: 'Server error occurred'
      }
    });
    
    render(<BillingList />);
    
    // Error should be displayed
    await waitFor(() => {
      expect(handleApiError).toHaveBeenCalled();
      expect(screen.getByText(/Error: Failed to load saved reports/i)).toBeInTheDocument();
    });
    
    // Saved reports section should show error state
    expect(screen.getByText(/could not load saved reports/i)).toBeInTheDocument();
  });
  
  test('handles API errors when deleting a report', async () => {
    // Mock successful list
    billingApi.list.mockResolvedValue(mockBillingReports);
    
    // Mock error on delete
    billingApi.delete.mockRejectedValueOnce({
      status: 500,
      message: 'Failed to delete report',
      data: {
        detail: 'Server error occurred'
      }
    });
    
    render(<BillingList />);
    
    // Wait for API calls
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
      expect(billingApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Get all delete buttons
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    
    // Click the delete button for the first report
    fireEvent.click(deleteButtons[0]);
    
    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/are you sure you want to delete this report/i)).toBeInTheDocument();
    });
    
    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);
    
    // Delete API should be called and error handled
    await waitFor(() => {
      expect(billingApi.delete).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000');
      expect(handleApiError).toHaveBeenCalled();
      expect(screen.getByText(/Error: Failed to delete report/i)).toBeInTheDocument();
    });
  });
  
  test('allows filtering saved reports', async () => {
    render(<BillingList />);
    
    // Wait for API calls
    await waitFor(() => {
      expect(customerApi.list).toHaveBeenCalledTimes(1);
      expect(billingApi.list).toHaveBeenCalledTimes(1);
    });
    
    // Find the search input
    const searchInput = screen.getByPlaceholderText(/search reports/i);
    
    // Enter search query
    fireEvent.change(searchInput, { target: { value: 'Test Company' } });
    
    // API should be called with search parameter
    await waitFor(() => {
      expect(billingApi.list).toHaveBeenCalledTimes(2);
      expect(billingApi.list).toHaveBeenLastCalledWith(
        expect.objectContaining({
          search: 'Test Company'
        })
      );
    });
  });
});