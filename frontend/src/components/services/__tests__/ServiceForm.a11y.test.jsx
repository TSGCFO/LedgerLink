import React from 'react';
import { render, fireEvent } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import ServiceForm from '../ServiceForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }),
}));

describe('ServiceForm Accessibility', () => {
  const mockChargeTypes = [
    { value: 'quantity', label: 'Per Quantity' },
    { value: 'fixed', label: 'Fixed Fee' },
    { value: 'hourly', label: 'Hourly Rate' },
    { value: 'weight', label: 'Per Weight' }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API calls
    axios.get.mockImplementation((url) => {
      if (url.includes('/services/charge_types')) {
        return Promise.resolve({ data: { success: true, data: mockChargeTypes } });
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('should not have accessibility violations', async () => {
    const { container, findByLabelText } = render(<ServiceForm />);
    
    // Wait for form to load
    await findByLabelText(/Service Name/i);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with validation errors should still be accessible', async () => {
    const { container, findByLabelText, getByRole } = render(<ServiceForm />);
    
    // Wait for form to load
    await findByLabelText(/Service Name/i);
    
    // Submit without filling required fields to trigger validation errors
    const submitButton = getByRole('button', { name: /Create Service/i });
    submitButton.click();
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form with filled data should be accessible', async () => {
    const { container, findByLabelText } = render(<ServiceForm />);
    
    // Wait for form to load
    const serviceNameField = await findByLabelText(/Service Name/i);
    const descriptionField = await findByLabelText(/Description/i);
    
    // Fill form fields
    fireEvent.change(serviceNameField, { target: { value: 'Test Service' } });
    fireEvent.change(descriptionField, { target: { value: 'Test Description' } });
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  test('form in edit mode should be accessible', async () => {
    // Mock useParams to return an ID
    jest.spyOn(require('react-router-dom'), 'useParams').mockImplementation(() => ({ id: '123' }));
    
    // Mock service fetch API response
    axios.get.mockImplementation((url) => {
      if (url.includes('/services/charge_types')) {
        return Promise.resolve({ data: { success: true, data: mockChargeTypes } });
      } else if (url.includes('/services/123')) {
        return Promise.resolve({ 
          data: {
            id: 123,
            service_name: 'Existing Service',
            description: 'Existing Description',
            charge_type: 'fixed'
          }
        });
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    const { container, findByText } = render(<ServiceForm />);
    
    // Wait for form to load in edit mode
    await findByText('Edit Service');
    
    // Run accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});