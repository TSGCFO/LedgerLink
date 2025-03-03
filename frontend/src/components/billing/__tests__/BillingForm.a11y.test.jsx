import React from 'react';
import { render } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import BillingForm from '../BillingForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }),
}));

describe('BillingForm Accessibility', () => {
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
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('should not have accessibility violations', async () => {
    const { container, findByLabelText } = render(<BillingForm />);
    
    // Wait for form to load
    await findByLabelText(/customer/i);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with validation errors should still be accessible', async () => {
    const { container, findByLabelText, getByRole } = render(<BillingForm />);
    
    // Wait for form to load
    await findByLabelText(/customer/i);
    
    // Submit without filling required fields to trigger validation errors
    const submitButton = getByRole('button', { name: /generate report/i });
    submitButton.click();
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('preview dialog should be accessible', async () => {
    // Mock the preview data
    axios.post.mockResolvedValue({
      data: {
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
            }
          ]
        },
        service_totals: {
          1: { name: 'Standard Shipping', amount: 25.00, order_count: 1 }
        }
      }
    });
    
    const { container, findByLabelText, getByRole, findByText } = render(<BillingForm />);
    
    // Wait for form to load
    const customerField = await findByLabelText(/customer/i);
    
    // Fill form and submit to show preview
    // Fill out form minimally
    customerField.click();
    await findByText('Test Company');
    getByRole('option', { name: 'Test Company' }).click();
    
    // Set dates
    const startDateInput = getByRole('textbox', { name: /start date/i });
    fireEvent.change(startDateInput, { target: { value: '01/01/2025' } });
    
    const endDateInput = getByRole('textbox', { name: /end date/i });
    fireEvent.change(endDateInput, { target: { value: '02/01/2025' } });
    
    // Set output format to preview
    // This is complex with MaterialUI and would need to be handled through internal state
    // For this test we'll mock the API response and submit
    
    // Submit form
    getByRole('button', { name: /generate report/i }).click();
    
    // Wait for preview dialog to appear
    await findByText(/report preview/i);
    
    // Run accessibility tests on dialog
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});