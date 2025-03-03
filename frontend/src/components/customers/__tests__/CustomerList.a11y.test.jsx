import React from 'react';
import { render } from '../../../utils/test-utils';
import { axe, toHaveNoViolations } from 'jest-axe';
import CustomerList from '../CustomerList';
import axios from 'axios';

// Add jest-axe matcher
expect.extend(toHaveNoViolations);

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

describe('CustomerList Component Accessibility', () => {
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
  
  it('should not have accessibility violations in loading state', async () => {
    const { container } = render(<CustomerList />);
    
    // Run axe
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should not have accessibility violations when displaying customers', async () => {
    // Mock resolved API response
    axios.get.mockImplementationOnce(() => {
      return Promise.resolve({
        data: mockCustomers,
        status: 200
      });
    });
    
    const { container, findByText } = render(<CustomerList />);
    
    // Wait for customers to display
    await findByText('Acme Inc');
    
    // Run axe
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should not have accessibility violations in empty state', async () => {
    // Mock empty customer list
    axios.get.mockImplementationOnce(() => {
      return Promise.resolve({
        data: {
          count: 0,
          next: null,
          previous: null,
          results: []
        },
        status: 200
      });
    });
    
    const { container, findByText } = render(<CustomerList />);
    
    // Wait for empty message
    await findByText(/no customers found/i);
    
    // Run axe
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should not have accessibility violations in error state', async () => {
    // Mock API error
    axios.get.mockImplementationOnce(() => {
      return Promise.reject(new Error('Network error'));
    });
    
    const { container, findByText } = render(<CustomerList />);
    
    // Wait for error message
    await findByText(/error loading customers/i);
    
    // Run axe
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});