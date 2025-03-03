import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import BillingList from '../BillingList';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('BillingList Component', () => {
  const mockCustomers = [
    { id: 1, company_name: 'Test Company', contact_name: 'John Doe' },
    { id: 2, company_name: 'Another Company', contact_name: 'Jane Smith' }
  ];
  
  const mockBillingData = {
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
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API calls
    axios.get.mockImplementation((url) => {
      if (url.includes('/customers')) {
        return Promise.resolve({ data: { results: mockCustomers } });
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    axios.post.mockResolvedValue({
      data: mockBillingData,
      success: true
    });
    
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
      expect(screen.getByText('Test Company')).toBeInTheDocument();
      expect(screen.getByText('Another Company')).toBeInTheDocument();
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
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('shows error when start date is after end date', async () => {
    render(<BillingList />);
    
    // Select customer
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Set dates in wrong order
    const startDateInput = screen.getByLabelText(/start date/i);
    fireEvent.change(startDateInput, { target: { value: '03/01/2025' } });
    
    const endDateInput = screen.getByLabelText(/end date/i);
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // Should show date validation error
    await waitFor(() => {
      expect(screen.getByText(/start date must be before end date/i)).toBeInTheDocument();
    });
    
    // API should not be called
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('displays billing data when calculate is clicked with valid inputs', async () => {
    render(<BillingList />);
    
    // Select customer
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Set valid dates
    const startDateInput = screen.getByLabelText(/start date/i);
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = screen.getByLabelText(/end date/i);
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // API should be called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/billing/api/generate-report/'),
        expect.objectContaining({
          customer: 1,
          output_format: 'preview'
        }),
        expect.any(Object)
      );
    });
    
    // Table should be displayed with billing data
    await waitFor(() => {
      expect(screen.getByText('ORD-001')).toBeInTheDocument();
      expect(screen.getByText('ORD-002')).toBeInTheDocument();
      // Check for totals
      expect(screen.getByText('$150.00')).toBeInTheDocument();
      expect(screen.getByText('$75.00')).toBeInTheDocument();
    });
  });
  
  test('handles API errors when calculating billing', async () => {
    // Mock API error
    axios.post.mockRejectedValueOnce({
      response: {
        status: 500,
        data: {
          detail: 'Server error occurred'
        }
      }
    });
    
    render(<BillingList />);
    
    // Select customer
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Set valid dates
    const startDateInput = screen.getByLabelText(/start date/i);
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = screen.getByLabelText(/end date/i);
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(screen.getByText(/server error occurred/i)).toBeInTheDocument();
    });
    
    // No table should be displayed
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });
});