import React from 'react';
import { render, screen, waitFor, fireEvent } from '../../../utils/test-utils';
import CustomerList from '../CustomerList';
import axios from 'axios';

// Mock the axios module
jest.mock('axios');

// Sample customer data
const mockCustomers = {
  count: 3,
  next: null,
  previous: null,
  results: [
    {
      id: '1',
      company_name: 'Acme Inc',
      contact_name: 'John Doe',
      email: 'john@acme.com',
      phone: '555-1234',
      address: '123 Main St',
      city: 'Anytown',
      state: 'CA',
      zip_code: '12345',
      country: 'US',
      is_active: true
    },
    {
      id: '2',
      company_name: 'Beta Corp',
      contact_name: 'Jane Smith',
      email: 'jane@beta.com',
      phone: '555-5678',
      address: '456 Oak Ave',
      city: 'Somewhere',
      state: 'NY',
      zip_code: '67890',
      country: 'US',
      is_active: true
    },
    {
      id: '3',
      company_name: 'Gamma LLC',
      contact_name: 'Bob Johnson',
      email: 'bob@gamma.com',
      phone: '555-9012',
      address: '789 Pine Rd',
      city: 'Elsewhere',
      state: 'TX',
      zip_code: '34567',
      country: 'US',
      is_active: false
    }
  ]
};

describe('CustomerList Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Mock the axios get method
    axios.get.mockResolvedValue({
      data: mockCustomers,
      status: 200,
      statusText: 'OK'
    });
    
    // Mock localStorage getItem for auth token
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders loading state initially', () => {
    render(<CustomerList />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
  
  test('renders customer data after loading', async () => {
    render(<CustomerList />);
    
    // Wait for the loading state to be replaced by the customer list
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Check that customer data is displayed
    expect(screen.getByText('Acme Inc')).toBeInTheDocument();
    expect(screen.getByText('Beta Corp')).toBeInTheDocument();
    expect(screen.getByText('Gamma LLC')).toBeInTheDocument();
  });
  
  test('displays inactive customers correctly', async () => {
    render(<CustomerList />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Find the active/inactive indicators
    const statusCells = screen.getAllByRole('cell', { name: /active|inactive/i });
    
    // Check that we display the correct status for each customer
    expect(statusCells[0]).toHaveTextContent(/active/i);
    expect(statusCells[2]).toHaveTextContent(/inactive/i);
  });
  
  test('handles search functionality', async () => {
    render(<CustomerList />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Mock the search API call
    axios.get.mockResolvedValueOnce({
      data: {
        count: 1,
        next: null,
        previous: null,
        results: [mockCustomers.results[0]] // Just return the first customer
      },
      status: 200,
      statusText: 'OK'
    });
    
    // Get the search input and type in it
    const searchInput = screen.getByPlaceholderText(/search/i);
    fireEvent.change(searchInput, { target: { value: 'Acme' } });
    
    // Submit the search
    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);
    
    // Wait for the search results
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/customers/'),
        expect.objectContaining({
          params: expect.objectContaining({ search: 'Acme' })
        })
      );
    });
    
    // Check that only the searched customer is displayed
    expect(screen.getByText('Acme Inc')).toBeInTheDocument();
    expect(screen.queryByText('Beta Corp')).not.toBeInTheDocument();
    expect(screen.queryByText('Gamma LLC')).not.toBeInTheDocument();
  });
  
  test('navigates to customer form when add button is clicked', async () => {
    // Mock the useNavigate hook
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate
    }));
    
    render(<CustomerList />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Find and click the add button
    const addButton = screen.getByRole('button', { name: /add customer/i });
    fireEvent.click(addButton);
    
    // Check that navigation occurs to the create form
    expect(mockNavigate).toHaveBeenCalledWith('/customers/new');
  });
  
  test('displays error state when API call fails', async () => {
    // Mock the API to return an error
    axios.get.mockRejectedValueOnce(new Error('Network error'));
    
    render(<CustomerList />);
    
    // Wait for the error state
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
    
    // Should display an error message
    expect(screen.getByText(/error loading customers/i)).toBeInTheDocument();
  });
});