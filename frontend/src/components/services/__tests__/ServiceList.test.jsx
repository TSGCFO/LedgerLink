import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import ServiceList from '../ServiceList';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('ServiceList Component', () => {
  const mockServices = [
    {
      id: 1,
      service_name: 'Packaging',
      description: 'Packaging and preparation of materials',
      charge_type: 'quantity'
    },
    {
      id: 2,
      service_name: 'Shipping',
      description: 'Standard shipping service',
      charge_type: 'weight'
    },
    {
      id: 3,
      service_name: 'Consulting',
      description: 'Expert consulting services',
      charge_type: 'hourly'
    }
  ];
  
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
      if (url.includes('/services') && !url.includes('/charge_types')) {
        return Promise.resolve({ data: { success: true, data: mockServices } });
      } else if (url.includes('/services/charge_types')) {
        return Promise.resolve({ data: { success: true, data: mockChargeTypes } });
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    axios.delete.mockResolvedValue({
      data: { success: true }
    });
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
  });
  
  test('renders services table with data', async () => {
    render(<ServiceList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/services'),
        expect.any(Object)
      );
    });
    
    // Check that table is rendered with headers
    expect(screen.getByRole('table')).toBeInTheDocument();
    
    // Check for column headers
    expect(screen.getByText('Service Name')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Charge Type')).toBeInTheDocument();
    
    // Check service data
    expect(screen.getByText('Packaging')).toBeInTheDocument();
    expect(screen.getByText('Shipping')).toBeInTheDocument();
    expect(screen.getByText('Consulting')).toBeInTheDocument();
    expect(screen.getByText('Packaging and preparation of materials')).toBeInTheDocument();
  });
  
  test('renders new service button', async () => {
    render(<ServiceList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
    
    // Check for New Service button
    expect(screen.getByRole('button', { name: /new service/i })).toBeInTheDocument();
  });
  
  test('handles service deletion', async () => {
    render(<ServiceList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Packaging')).toBeInTheDocument();
    });
    
    // Find and click delete button (first service)
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion dialog should be shown
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this service?');
    
    // Check delete API was called with correct ID
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith(
        expect.stringContaining('/services/1'),
        expect.any(Object)
      );
    });
    
    // Check for success message
    expect(screen.getByText('Service deleted successfully')).toBeInTheDocument();
    
    // Check that services list was refreshed
    expect(axios.get).toHaveBeenCalledTimes(3); // Initial 2 calls + 1 refresh call
  });
  
  test('navigates to edit page when edit button clicked', async () => {
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(<ServiceList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Packaging')).toBeInTheDocument();
    });
    
    // Find and click the first edit button
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);
    
    // Check navigation was called with correct path
    expect(navigateMock).toHaveBeenCalledWith('/services/1/edit');
  });
  
  test('navigates to new service page when add button clicked', async () => {
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(<ServiceList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Packaging')).toBeInTheDocument();
    });
    
    // Click New Service button
    fireEvent.click(screen.getByRole('button', { name: /new service/i }));
    
    // Check navigation was called with correct path
    expect(navigateMock).toHaveBeenCalledWith('/services/new');
  });
  
  test('handles API error when loading services', async () => {
    // Mock API error
    axios.get.mockRejectedValueOnce({
      response: {
        status: 500,
        data: {
          detail: 'Internal server error'
        }
      }
    });
    
    render(<ServiceList />);
    
    // Wait for error to display
    await waitFor(() => {
      expect(screen.getByText(/internal server error/i)).toBeInTheDocument();
    });
  });
  
  test('handles cancellation of deletion', async () => {
    // Mock window.confirm to return false (cancel)
    window.confirm.mockImplementationOnce(() => false);
    
    render(<ServiceList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Packaging')).toBeInTheDocument();
    });
    
    // Find and click delete button (first service)
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion dialog should be shown
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this service?');
    
    // Delete API should not be called
    expect(axios.delete).not.toHaveBeenCalled();
  });
});