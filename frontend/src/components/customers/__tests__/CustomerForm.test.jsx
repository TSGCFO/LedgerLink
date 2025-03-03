import React from 'react';
import { render, screen, waitFor, fireEvent } from '../../../utils/test-utils';
import CustomerForm from '../CustomerForm';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';

// Mock the axios module
jest.mock('axios');

// Mock react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(),
  useNavigate: jest.fn()
}));

// Sample customer data for edit mode
const mockCustomer = {
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
};

describe('CustomerForm Component', () => {
  let mockNavigate;
  
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Set up mocks
    mockNavigate = jest.fn();
    useNavigate.mockReturnValue(mockNavigate);
    useParams.mockReturnValue({ id: undefined }); // Default to create mode
    
    // Mock localStorage getItem for auth token
    Storage.prototype.getItem = jest.fn(() => 'fake-token');
  });
  
  test('renders empty form in create mode', () => {
    render(<CustomerForm />);
    
    // Check that the form title indicates create mode
    expect(screen.getByText(/create customer/i)).toBeInTheDocument();
    
    // Check that form fields are empty
    expect(screen.getByLabelText(/company name/i)).toHaveValue('');
    expect(screen.getByLabelText(/contact name/i)).toHaveValue('');
    expect(screen.getByLabelText(/email/i)).toHaveValue('');
  });
  
  test('loads customer data in edit mode', async () => {
    // Set up for edit mode
    useParams.mockReturnValue({ id: '1' });
    
    // Mock the API response for getting a customer
    axios.get.mockResolvedValueOnce({
      data: mockCustomer,
      status: 200
    });
    
    render(<CustomerForm />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/edit customer/i)).toBeInTheDocument();
    });
    
    // Check that form fields are pre-filled with customer data
    expect(screen.getByLabelText(/company name/i)).toHaveValue(mockCustomer.company_name);
    expect(screen.getByLabelText(/contact name/i)).toHaveValue(mockCustomer.contact_name);
    expect(screen.getByLabelText(/email/i)).toHaveValue(mockCustomer.email);
  });
  
  test('validates required fields on submit', async () => {
    render(<CustomerForm />);
    
    // Submit the form without filling required fields
    const submitButton = screen.getByRole('button', { name: /submit|save/i });
    fireEvent.click(submitButton);
    
    // Check for validation error messages
    await waitFor(() => {
      expect(screen.getByText(/company name is required/i)).toBeInTheDocument();
    });
  });
  
  test('validates email format on submit', async () => {
    render(<CustomerForm />);
    
    // Fill out the form with invalid email
    fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'Test Company' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'invalid-email' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /submit|save/i });
    fireEvent.click(submitButton);
    
    // Check for email validation error
    await waitFor(() => {
      expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
    });
  });
  
  test('creates new customer on submit in create mode', async () => {
    // Mock the API response for creating a customer
    axios.post.mockResolvedValueOnce({
      data: { ...mockCustomer, id: '2', company_name: 'New Company' },
      status: 201
    });
    
    render(<CustomerForm />);
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'New Company' } });
    fireEvent.change(screen.getByLabelText(/contact name/i), { target: { value: 'Jane Smith' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText(/phone/i), { target: { value: '555-5678' } });
    fireEvent.change(screen.getByLabelText(/address/i), { target: { value: '456 Oak St' } });
    fireEvent.change(screen.getByLabelText(/city/i), { target: { value: 'Somewhere' } });
    fireEvent.change(screen.getByLabelText(/state/i), { target: { value: 'NY' } });
    fireEvent.change(screen.getByLabelText(/zip code/i), { target: { value: '67890' } });
    fireEvent.change(screen.getByLabelText(/country/i), { target: { value: 'US' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /submit|save/i });
    fireEvent.click(submitButton);
    
    // Check that the API was called with the correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        '/api/v1/customers/',
        expect.objectContaining({
          company_name: 'New Company',
          contact_name: 'Jane Smith',
          email: 'jane@example.com'
        }),
        expect.anything()
      );
    });
    
    // Check that we navigated back to the customer list
    expect(mockNavigate).toHaveBeenCalledWith('/customers');
  });
  
  test('updates customer on submit in edit mode', async () => {
    // Set up for edit mode
    useParams.mockReturnValue({ id: '1' });
    
    // Mock the API responses
    axios.get.mockResolvedValueOnce({
      data: mockCustomer,
      status: 200
    });
    
    axios.put.mockResolvedValueOnce({
      data: { ...mockCustomer, company_name: 'Updated Company' },
      status: 200
    });
    
    render(<CustomerForm />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/edit customer/i)).toBeInTheDocument();
    });
    
    // Change some fields
    fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'Updated Company' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /submit|save/i });
    fireEvent.click(submitButton);
    
    // Check that the API was called with the correct data
    await waitFor(() => {
      expect(axios.put).toHaveBeenCalledWith(
        `/api/v1/customers/${mockCustomer.id}/`,
        expect.objectContaining({
          company_name: 'Updated Company'
        }),
        expect.anything()
      );
    });
    
    // Check that we navigated back to the customer list
    expect(mockNavigate).toHaveBeenCalledWith('/customers');
  });
  
  test('handles API errors on submit', async () => {
    // Mock the API to return an error
    axios.post.mockRejectedValueOnce({
      response: {
        data: {
          company_name: ['A customer with this name already exists.']
        },
        status: 400
      }
    });
    
    render(<CustomerForm />);
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'Existing Company' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /submit|save/i });
    fireEvent.click(submitButton);
    
    // Check that error is displayed
    await waitFor(() => {
      expect(screen.getByText(/customer with this name already exists/i)).toBeInTheDocument();
    });
    
    // We should not navigate away
    expect(mockNavigate).not.toHaveBeenCalled();
  });
  
  test('cancels and returns to customer list', () => {
    render(<CustomerForm />);
    
    // Click the cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    // Check that we navigated back to the customer list
    expect(mockNavigate).toHaveBeenCalledWith('/customers');
  });
});