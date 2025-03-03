import React from 'react';
import { render } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import ProductForm from '../ProductForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }),
}));

describe('ProductForm Accessibility', () => {
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
    const { container, findByLabelText } = render(<ProductForm />);
    
    // Wait for form to load
    await findByLabelText(/SKU/i);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with validation errors should still be accessible', async () => {
    const { container, findByLabelText, getByRole } = render(<ProductForm />);
    
    // Wait for form to load
    await findByLabelText(/SKU/i);
    
    // Submit without filling required fields to trigger validation errors
    const submitButton = getByRole('button', { name: /create product/i });
    submitButton.click();
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with partial data should still be accessible', async () => {
    const { container, findByLabelText, getByRole, getByText } = render(<ProductForm />);
    
    // Wait for form to load
    await findByLabelText(/SKU/i);
    
    // Fill out SKU but leave customer empty
    const skuField = getByLabelText(/SKU/i);
    fireEvent.change(skuField, { target: { value: 'TEST-SKU' } });
    
    // Fill unit but not quantity
    fireEvent.change(getByLabelText(/Labeling Unit 1/i), {
      target: { value: 'Box' }
    });
    
    // Submit form to trigger validation errors
    getByRole('button', { name: /create product/i }).click();
    
    await findByText(/Customer is required/i);
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});