import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import OrderForm from '../OrderForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }), // No ID by default (create mode)
}));

describe('OrderForm Component', () => {
  const mockCustomers = [
    { id: 1, company_name: 'Test Company', contact_name: 'John Doe' },
    { id: 2, company_name: 'Another Company', contact_name: 'Jane Smith' }
  ];
  
  const mockChoices = {
    status_choices: [
      { value: 'pending', label: 'Pending' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'completed', label: 'Completed' },
      { value: 'cancelled', label: 'Cancelled' }
    ],
    priority_choices: [
      { value: 'low', label: 'Low' },
      { value: 'normal', label: 'Normal' },
      { value: 'high', label: 'High' },
      { value: 'urgent', label: 'Urgent' }
    ]
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API calls
    axios.get.mockImplementation((url) => {
      if (url.includes('/customers')) {
        return Promise.resolve({ data: { results: mockCustomers } });
      } else if (url.includes('/orders/choices')) {
        return Promise.resolve({ data: mockChoices });
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    axios.post.mockResolvedValue({
      data: {
        id: 123,
        order_number: 'TEST-123',
        customer: 1,
        status: 'pending'
      }
    });
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders form with all fields', async () => {
    render(<OrderForm />);
    
    // Initially should show loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Check all form fields are rendered
    expect(screen.getByLabelText(/customer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/order number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/shipping address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/shipping method/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/notes/i)).toBeInTheDocument();
    
    // Check submit button is present
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });
  
  test('validates required fields', async () => {
    render(<OrderForm />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Click submit without filling required fields
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    
    // Check validation errors
    await waitFor(() => {
      expect(screen.getByText(/customer is required/i)).toBeInTheDocument();
      expect(screen.getByText(/order number is required/i)).toBeInTheDocument();
      expect(screen.getByText(/shipping address is required/i)).toBeInTheDocument();
    });
    
    // Should not call API
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('submits form with valid data', async () => {
    render(<OrderForm />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Fill out form
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField); // Open dropdown
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    fireEvent.change(screen.getByLabelText(/order number/i), {
      target: { value: 'TEST-123' }
    });
    
    fireEvent.change(screen.getByLabelText(/shipping address/i), {
      target: { value: '123 Test St, Test City, TC 12345' }
    });
    
    fireEvent.change(screen.getByLabelText(/shipping method/i), {
      target: { value: 'Standard' }
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    
    // Check API called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/orders/'),
        expect.objectContaining({
          customer: 1,
          order_number: 'TEST-123',
          shipping_address: '123 Test St, Test City, TC 12345',
          shipping_method: 'Standard'
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
          order_number: ['Order number already exists']
        }
      }
    });
    
    render(<OrderForm />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Fill out form minimally
    const customerField = screen.getByLabelText(/customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    fireEvent.change(screen.getByLabelText(/order number/i), {
      target: { value: 'DUPLICATE-ORDER' }
    });
    
    fireEvent.change(screen.getByLabelText(/shipping address/i), {
      target: { value: '123 Test St' }
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(screen.getByText(/Order number already exists/i)).toBeInTheDocument();
    });
  });
});