import React from 'react';
import { render } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import OrderForm from '../OrderForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }),
}));

describe('OrderForm Accessibility', () => {
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
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('should not have accessibility violations', async () => {
    const { container, findByLabelText } = render(<OrderForm />);
    
    // Wait for form to load
    await findByLabelText(/customer/i);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with validation errors should still be accessible', async () => {
    const { container, findByLabelText, getByRole } = render(<OrderForm />);
    
    // Wait for form to load
    await findByLabelText(/customer/i);
    
    // Submit without filling required fields to trigger validation errors
    const submitButton = getByRole('button', { name: /save/i });
    submitButton.click();
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});