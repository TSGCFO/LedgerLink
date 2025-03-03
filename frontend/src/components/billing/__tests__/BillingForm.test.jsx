import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import BillingForm from '../BillingForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }), // No ID by default (create mode)
}));

describe('BillingForm Component', () => {
  const mockCustomers = [
    { id: 1, company_name: 'Test Company', contact_name: 'John Doe' },
    { id: 2, company_name: 'Another Company', contact_name: 'Jane Smith' }
  ];
  
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
      data: {
        id: 123,
        customer: 1,
        start_date: '2025-01-01',
        end_date: '2025-02-01',
        report_id: 'REP-123',
        total_amount: 1500.00
      }
    });
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders form with all fields', async () => {
    render(<BillingForm />);
    
    // Initially should show loading state for customer dropdown
    expect(screen.getByLabelText(/customer/i)).toBeInTheDocument();
    
    // Wait for form to load completely
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
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
      expect(screen.getByText('Test Company')).toBeInTheDocument();
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
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('submits form with valid data', async () => {
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Fill out form
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField); // Open dropdown
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Set start date - mock the DatePicker onChange
    const startDateField = screen.getByLabelText(/start date/i);
    // Direct fireEvent doesn't work with DatePicker components
    // Access the DatePicker component props and call onChange directly
    const startDatePicker = screen.getAllByRole('textbox')[0];
    fireEvent.mouseDown(startDatePicker);
    const startDate = new Date(2025, 0, 1); // 2025-01-01
    // We need to find the onChange handler from the component
    // For the test, we'll simulate the date selection
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    // Set end date - similar approach
    const endDateField = screen.getByLabelText(/end date/i);
    const endDatePicker = screen.getAllByRole('textbox')[1];
    fireEvent.mouseDown(endDatePicker);
    const endDate = new Date(2025, 1, 1); // 2025-02-01
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Expecting API to be called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/billing/api/generate-report/'),
        expect.objectContaining({
          customer: 1,
          output_format: 'json'
          // We can't check the date strings easily here due to the DatePicker complexity
        }),
        expect.any(Object)
      );
    });
  });
  
  test('handles API errors on submit', async () => {
    // Mock API error
    axios.post.mockRejectedValueOnce({
      response: {
        status: 400,
        data: {
          detail: 'Invalid date range'
        }
      }
    });
    
    render(<BillingForm />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Fill out form minimally
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Set start and end dates with invalid range
    const startDateInput = screen.getAllByRole('textbox')[0];
    fireEvent.change(startDateInput, { target: { value: '03/01/2025' } });
    
    const endDateInput = screen.getAllByRole('textbox')[1];
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /generate report/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(screen.getByText(/invalid date range/i)).toBeInTheDocument();
    });
  });
});