import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import OrderList from '../OrderList';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('OrderList Component', () => {
  const mockOrders = {
    count: 3,
    next: null,
    previous: null,
    results: [
      {
        id: 1,
        order_number: 'ORD-001',
        customer: {
          id: 1,
          company_name: 'Test Company',
        },
        order_date: '2025-03-01T10:00:00Z',
        status: 'pending',
        priority: 'normal',
        shipping_method: 'Standard',
        shipping_address: '123 Test St, Test City, TC 12345',
      },
      {
        id: 2,
        order_number: 'ORD-002',
        customer: {
          id: 2,
          company_name: 'Another Company',
        },
        order_date: '2025-03-02T10:00:00Z',
        status: 'in_progress',
        priority: 'high',
        shipping_method: 'Express',
        shipping_address: '456 Test Ave, Test City, TC 12345',
      },
      {
        id: 3,
        order_number: 'ORD-003',
        customer: {
          id: 1,
          company_name: 'Test Company',
        },
        order_date: '2025-03-03T10:00:00Z',
        status: 'completed',
        priority: 'normal',
        shipping_method: 'Standard',
        shipping_address: '789 Test Blvd, Test City, TC 12345',
      }
    ]
  };
  
  const mockStatusCounts = {
    pending: 10,
    in_progress: 5,
    completed: 20,
    cancelled: 2,
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API calls
    axios.get.mockImplementation((url) => {
      if (url.includes('/orders')) {
        if (url.includes('status=pending')) {
          // Filter to just pending orders
          return Promise.resolve({ 
            data: {
              ...mockOrders,
              results: mockOrders.results.filter(o => o.status === 'pending')
            } 
          });
        } else if (url.includes('search=ORD-001')) {
          // Search filter
          return Promise.resolve({ 
            data: {
              ...mockOrders,
              results: mockOrders.results.filter(o => o.order_number === 'ORD-001')
            } 
          });
        } else if (url.includes('status_counts')) {
          return Promise.resolve({ data: mockStatusCounts });
        } else {
          return Promise.resolve({ data: mockOrders });
        }
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    // Mock localStorage for auth token
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders orders table with data', async () => {
    render(<OrderList />);
    
    // Initially should show loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Should display table with headers
    expect(screen.getByRole('table')).toBeInTheDocument();
    
    // Check for column headers
    expect(screen.getByText(/order number/i)).toBeInTheDocument();
    expect(screen.getByText(/customer/i)).toBeInTheDocument();
    expect(screen.getByText(/status/i)).toBeInTheDocument();
    
    // Check that order data is displayed
    expect(screen.getByText('ORD-001')).toBeInTheDocument();
    expect(screen.getByText('ORD-002')).toBeInTheDocument();
    expect(screen.getByText('ORD-003')).toBeInTheDocument();
    expect(screen.getAllByText('Test Company').length).toBeGreaterThan(0);
    expect(screen.getByText('Another Company')).toBeInTheDocument();
  });
  
  test('displays status counts in filter chips', async () => {
    render(<OrderList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Should display status filter chips with counts
    expect(screen.getByText(/pending \(10\)/i)).toBeInTheDocument();
    expect(screen.getByText(/in progress \(5\)/i)).toBeInTheDocument();
    expect(screen.getByText(/completed \(20\)/i)).toBeInTheDocument();
  });
  
  test('filters orders by status when clicking filter chip', async () => {
    render(<OrderList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Click on the pending filter
    fireEvent.click(screen.getByText(/pending \(10\)/i));
    
    // Should make API call with status filter
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining('/orders/?status=pending'),
      expect.any(Object)
    );
    
    // Should update table to show only pending orders
    await waitFor(() => {
      expect(screen.getByText('ORD-001')).toBeInTheDocument();
      expect(screen.queryByText('ORD-002')).not.toBeInTheDocument();
      expect(screen.queryByText('ORD-003')).not.toBeInTheDocument();
    });
  });
  
  test('searches orders by order number', async () => {
    render(<OrderList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Type in search box
    fireEvent.change(screen.getByPlaceholderText(/search/i), {
      target: { value: 'ORD-001' },
    });
    
    // Click search button
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    
    // Should make API call with search parameter
    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining('/orders/?search=ORD-001'),
      expect.any(Object)
    );
    
    // Should update table to show only matching orders
    await waitFor(() => {
      expect(screen.getByText('ORD-001')).toBeInTheDocument();
      expect(screen.queryByText('ORD-002')).not.toBeInTheDocument();
      expect(screen.queryByText('ORD-003')).not.toBeInTheDocument();
    });
  });
  
  test('navigates to order form when add button is clicked', async () => {
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(<OrderList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Click add button
    fireEvent.click(screen.getByRole('button', { name: /add order/i }));
    
    // Should navigate to new order form
    expect(navigateMock).toHaveBeenCalledWith('/orders/new');
  });
  
  test('displays error state when API call fails', async () => {
    // Mock API error
    axios.get.mockRejectedValueOnce(new Error('Network error'));
    
    render(<OrderList />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
    
    // Should display error message
    expect(screen.getByText(/failed to load orders/i)).toBeInTheDocument();
  });
});