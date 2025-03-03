import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import ProductForm from '../ProductForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: undefined }), // No ID by default (create mode)
}));

describe('ProductForm Component', () => {
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
    
    axios.post.mockResolvedValue({
      data: {
        id: 123,
        sku: 'TEST-SKU',
        customer: 1,
        labeling_unit_1: 'Box',
        labeling_quantity_1: 10
      }
    });
    
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders form with all fields in create mode', async () => {
    render(<ProductForm />);
    
    // Wait for form to load customer dropdown
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Check form title
    expect(screen.getByText('New Product')).toBeInTheDocument();
    
    // Check all form fields are rendered
    expect(screen.getByLabelText(/SKU/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Customer/i)).toBeInTheDocument();
    
    // Check unit and quantity fields
    expect(screen.getByLabelText(/Labeling Unit 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Quantity 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Unit 2/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Quantity 2/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Unit 3/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Quantity 3/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Unit 4/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Quantity 4/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Unit 5/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Labeling Quantity 5/i)).toBeInTheDocument();
    
    // Check buttons
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create product/i })).toBeInTheDocument();
  });
  
  test('validates required fields', async () => {
    render(<ProductForm />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Submit without filling required fields
    fireEvent.click(screen.getByRole('button', { name: /create product/i }));
    
    // Check validation errors
    await waitFor(() => {
      expect(screen.getByText(/SKU is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Customer is required/i)).toBeInTheDocument();
    });
    
    // Should not call API
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('validates labeling unit and quantity pairs', async () => {
    render(<ProductForm />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Fill out SKU and customer
    fireEvent.change(screen.getByLabelText(/SKU/i), {
      target: { value: 'TEST-SKU' }
    });
    
    const customerField = screen.getByLabelText(/Customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Fill unit but not quantity
    fireEvent.change(screen.getByLabelText(/Labeling Unit 1/i), {
      target: { value: 'Box' }
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create product/i }));
    
    // Should show unit-quantity validation error
    await waitFor(() => {
      expect(screen.getByText(/Quantity is required when unit is provided/i)).toBeInTheDocument();
    });
    
    // Now fill quantity but clear unit
    fireEvent.change(screen.getByLabelText(/Labeling Quantity 1/i), {
      target: { value: '10' }
    });
    
    fireEvent.change(screen.getByLabelText(/Labeling Unit 1/i), {
      target: { value: '' }
    });
    
    // Submit form again
    fireEvent.click(screen.getByRole('button', { name: /create product/i }));
    
    // Should show unit validation error
    await waitFor(() => {
      expect(screen.getByText(/Unit is required when quantity is provided/i)).toBeInTheDocument();
    });
  });
  
  test('submits form with valid data', async () => {
    render(<ProductForm />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Fill out SKU
    fireEvent.change(screen.getByLabelText(/SKU/i), {
      target: { value: 'TEST-SKU' }
    });
    
    // Select customer
    const customerField = screen.getByLabelText(/Customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Fill unit and quantity
    fireEvent.change(screen.getByLabelText(/Labeling Unit 1/i), {
      target: { value: 'Box' }
    });
    
    fireEvent.change(screen.getByLabelText(/Labeling Quantity 1/i), {
      target: { value: '10' }
    });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create product/i }));
    
    // Check API was called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/products/'),
        expect.objectContaining({
          sku: 'TEST-SKU',
          customer: 1,
          labeling_unit_1: 'Box',
          labeling_quantity_1: 10
        }),
        expect.any(Object)
      );
    });
    
    // Check success message
    expect(screen.getByText(/Product created successfully/i)).toBeInTheDocument();
  });
  
  test('handles API errors on submit', async () => {
    // Mock API error
    axios.post.mockRejectedValueOnce({
      response: {
        status: 400,
        data: {
          sku: ['SKU already exists']
        }
      }
    });
    
    render(<ProductForm />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    
    // Fill out form with minimal data
    fireEvent.change(screen.getByLabelText(/SKU/i), {
      target: { value: 'DUPLICATE-SKU' }
    });
    
    const customerField = screen.getByLabelText(/Customer/i);
    fireEvent.mouseDown(customerField);
    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Test Company'));
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create product/i }));
    
    // Should show API error
    await waitFor(() => {
      expect(screen.getByText(/SKU already exists/i)).toBeInTheDocument();
    });
  });
});