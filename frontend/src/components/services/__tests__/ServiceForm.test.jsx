import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import ServiceForm from '../ServiceForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }), // No ID by default (create mode)
}));

describe('ServiceForm Component', () => {
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
    
    axios.post.mockResolvedValue({
      data: {
        id: 123,
        service_name: 'Test Service',
        description: 'Test Description',
        charge_type: 'quantity'
      }
    });
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders form with all fields in create mode', async () => {
    render(<ServiceForm />);
    
    // Wait for charge types to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/services/charge_types'),
        expect.any(Object)
      );
    });
    
    // Check form title
    expect(screen.getByText('New Service')).toBeInTheDocument();
    
    // Check form fields
    expect(screen.getByLabelText(/Service Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Charge Type/i)).toBeInTheDocument();
    
    // Check buttons
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Service/i })).toBeInTheDocument();
  });
  
  test('validates required fields', async () => {
    render(<ServiceForm />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
    
    // Submit form without filling required fields
    fireEvent.click(screen.getByRole('button', { name: /Create Service/i }));
    
    // Check validation errors
    await waitFor(() => {
      expect(screen.getByText(/Service name is required/i)).toBeInTheDocument();
    });
    
    // Should not call API
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('submits form with valid data', async () => {
    render(<ServiceForm />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
    
    // Fill service name
    fireEvent.change(screen.getByLabelText(/Service Name/i), {
      target: { value: 'Test Service' }
    });
    
    // Fill description
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'Test Description' }
    });
    
    // Select charge type
    const chargeTypeField = screen.getByLabelText(/Charge Type/i);
    fireEvent.mouseDown(chargeTypeField);
    await waitFor(() => {
      // Find and click the "Per Quantity" option
      const options = screen.getAllByRole('option');
      fireEvent.click(options[0]); // Select first option (quantity)
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Create Service/i }));
    
    // Check API was called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/services/'),
        expect.objectContaining({
          service_name: 'Test Service',
          description: 'Test Description',
          charge_type: 'quantity'
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
          service_name: ['Service name already exists']
        }
      }
    });
    
    render(<ServiceForm />);
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
    
    // Fill service name
    fireEvent.change(screen.getByLabelText(/Service Name/i), {
      target: { value: 'Duplicate Service' }
    });
    
    // Fill description
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'Test Description' }
    });
    
    // Select charge type
    const chargeTypeField = screen.getByLabelText(/Charge Type/i);
    fireEvent.mouseDown(chargeTypeField);
    await waitFor(() => {
      const options = screen.getAllByRole('option');
      fireEvent.click(options[0]);
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Create Service/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(screen.getByText(/Service name already exists/i)).toBeInTheDocument();
    });
  });
  
  test('loads service data in edit mode', async () => {
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
    
    render(<ServiceForm />);
    
    // Wait for service data to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/services/123'),
        expect.any(Object)
      );
    });
    
    // Check form title and fields are populated
    expect(screen.getByText('Edit Service')).toBeInTheDocument();
    expect(screen.getByLabelText(/Service Name/i).value).toBe('Existing Service');
    expect(screen.getByLabelText(/Description/i).value).toBe('Existing Description');
    
    // Check edit button text
    expect(screen.getByRole('button', { name: /Update Service/i })).toBeInTheDocument();
  });
});