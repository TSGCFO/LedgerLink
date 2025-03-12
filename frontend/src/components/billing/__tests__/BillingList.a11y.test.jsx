import React from 'react';
import { render } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import BillingList from '../BillingList';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('BillingList Accessibility', () => {
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
  
  test('should not have accessibility violations', async () => {
    const { container, findByLabelText } = render(<BillingList />);
    
    // Wait for form to load
    await findByLabelText(/customer/i);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with validation errors should still be accessible', async () => {
    const { container, findByLabelText, getByRole } = render(<BillingList />);
    
    // Wait for form to load
    await findByLabelText(/customer/i);
    
    // Submit without filling required fields to trigger validation errors
    const calculateButton = getByRole('button', { name: /calculate/i });
    calculateButton.click();
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('billing data table should be accessible', async () => {
    const { container, findByLabelText, getByRole, findByText } = render(<BillingList />);
    
    // Wait for form to load
    const customerField = await findByLabelText(/customer/i);
    
    // Fill form and submit to show table
    customerField.click();
    const customerOption = await findByText('Test Company');
    fireEvent.click(customerOption);
    
    // Set dates
    const startDateInput = getByRole('textbox', { name: /start date/i });
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = getByRole('textbox', { name: /end date/i });
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Click calculate
    getByRole('button', { name: /calculate/i }).click();
    
    // Wait for table to appear
    await findByText('ORD-001');
    
    // Run accessibility tests on table
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});