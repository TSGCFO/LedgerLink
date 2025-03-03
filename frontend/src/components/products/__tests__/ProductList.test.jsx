import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import ProductList from '../ProductList';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('ProductList Component', () => {
  const mockProducts = [
    {
      id: 1,
      sku: 'SKU-001',
      customer: 1,
      customer_details: { company_name: 'Test Company' },
      labeling_unit_1: 'Box',
      labeling_quantity_1: 10,
      labeling_unit_2: 'Case',
      labeling_quantity_2: 5,
      created_at: '2025-03-01T10:00:00Z',
      updated_at: '2025-03-01T10:00:00Z',
    },
    {
      id: 2,
      sku: 'SKU-002',
      customer: 2,
      customer_details: { company_name: 'Another Company' },
      labeling_unit_1: 'Pallet',
      labeling_quantity_1: 1,
      created_at: '2025-03-02T10:00:00Z',
      updated_at: '2025-03-02T10:00:00Z',
    }
  ];
  
  const mockStats = {
    total_products: 2,
    products_by_customer: [
      { customer__company_name: 'Test Company', count: 1 },
      { customer__company_name: 'Another Company', count: 1 }
    ]
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API calls
    axios.get.mockImplementation((url) => {
      if (url.includes('/products') && !url.includes('/stats')) {
        return Promise.resolve({ data: { success: true, data: mockProducts } });
      } else if (url.includes('/products/stats')) {
        return Promise.resolve({ data: { success: true, data: mockStats } });
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });
    
    axios.delete.mockResolvedValue({
      data: { success: true }
    });
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders products table with data', async () => {
    render(<ProductList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/products'),
        expect.any(Object)
      );
    });
    
    // Check that table is rendered with headers
    expect(screen.getByRole('table')).toBeInTheDocument();
    
    // Check for product data
    expect(screen.getByText('SKU-001')).toBeInTheDocument();
    expect(screen.getByText('SKU-002')).toBeInTheDocument();
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('Another Company')).toBeInTheDocument();
    expect(screen.getByText('Box')).toBeInTheDocument();
    expect(screen.getByText('Case')).toBeInTheDocument();
    expect(screen.getByText('Pallet')).toBeInTheDocument();
  });
  
  test('renders statistics chips', async () => {
    render(<ProductList />);
    
    // Wait for stats to load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/products/stats'),
        expect.any(Object)
      );
    });
    
    // Check that stats are displayed
    expect(screen.getByText('Total Products: 2')).toBeInTheDocument();
    expect(screen.getByText('Test Company: 1')).toBeInTheDocument();
    expect(screen.getByText('Another Company: 1')).toBeInTheDocument();
  });
  
  test('handles product deletion', async () => {
    render(<ProductList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('SKU-001')).toBeInTheDocument();
    });
    
    // Find and click the first delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    // Check that confirmation was shown
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this product?');
    
    // Check API call made
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith(
        expect.stringContaining('/products/1'),
        expect.any(Object)
      );
    });
    
    // Check success message
    expect(screen.getByText('Product deleted successfully')).toBeInTheDocument();
    
    // Check that product list was refreshed
    expect(axios.get).toHaveBeenCalledTimes(4); // 2 initial calls + 2 refresh calls
  });
  
  test('navigates to edit page when edit button clicked', async () => {
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(<ProductList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('SKU-001')).toBeInTheDocument();
    });
    
    // Find and click the first edit button
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);
    
    // Check navigation was called
    expect(navigateMock).toHaveBeenCalledWith('/products/1/edit');
  });
  
  test('navigates to new product page when add button clicked', async () => {
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(<ProductList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('SKU-001')).toBeInTheDocument();
    });
    
    // Find and click the add button
    const addButton = screen.getByRole('button', { name: /new product/i });
    fireEvent.click(addButton);
    
    // Check navigation was called
    expect(navigateMock).toHaveBeenCalledWith('/products/new');
  });
  
  test('handles API error when loading products', async () => {
    // Mock API error
    axios.get.mockRejectedValueOnce({
      response: {
        status: 500,
        data: {
          detail: 'Server error'
        }
      }
    });
    
    render(<ProductList />);
    
    // Should display error
    await waitFor(() => {
      expect(screen.getByText(/server error/i)).toBeInTheDocument();
    });
  });
  
  test('handles cancellation of product deletion', async () => {
    // Mock user cancelling the confirm dialog
    window.confirm.mockImplementationOnce(() => false);
    
    render(<ProductList />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('SKU-001')).toBeInTheDocument();
    });
    
    // Find and click the first delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    // Check that confirmation was shown
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this product?');
    
    // Delete API should not be called since user cancelled
    expect(axios.delete).not.toHaveBeenCalled();
  });
});