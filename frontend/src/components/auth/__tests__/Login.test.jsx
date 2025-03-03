import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Login from '../Login';
import * as auth from '../../../utils/auth';

// Mock the useNavigate hook
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the auth utilities
jest.mock('../../../utils/auth', () => ({
  login: jest.fn(),
}));

describe('Login Component', () => {
  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form with all elements', () => {
    renderLogin();
    
    // Check for heading
    expect(screen.getByText('Sign in to LedgerLink')).toBeInTheDocument();
    
    // Check for username field
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    
    // Check for password field
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    
    // Check for submit button
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('allows entering username and password', () => {
    renderLogin();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    // Type in the inputs
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    // Check if values are updated
    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('password123');
  });

  test('calls login function on form submission with correct credentials', async () => {
    auth.login.mockResolvedValueOnce(true);
    
    renderLogin();
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), { 
      target: { value: 'testuser' } 
    });
    fireEvent.change(screen.getByLabelText(/password/i), { 
      target: { value: 'password123' } 
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    // Check if login was called with correct parameters
    expect(auth.login).toHaveBeenCalledWith('testuser', 'password123');
    
    // Wait for navigation to be called
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  test('shows error message on login failure', async () => {
    // Mock login to reject
    auth.login.mockRejectedValueOnce(new Error('Invalid credentials'));
    
    renderLogin();
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), { 
      target: { value: 'wronguser' } 
    });
    fireEvent.change(screen.getByLabelText(/password/i), { 
      target: { value: 'wrongpass' } 
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    // Check that login was called
    expect(auth.login).toHaveBeenCalledWith('wronguser', 'wrongpass');
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
    });
    
    // Check that navigation was not called
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('prevents default form submission', () => {
    renderLogin();
    
    // Create a mock event
    const mockPreventDefault = jest.fn();
    const mockEvent = { preventDefault: mockPreventDefault };
    
    // Get the form and simulate submit event
    const form = screen.getByRole('form');
    fireEvent.submit(form, mockEvent);
    
    // Check if preventDefault was called
    expect(mockPreventDefault).toHaveBeenCalled();
  });

  test('clears any previous error when submitting the form again', async () => {
    // First mock login to reject
    auth.login.mockRejectedValueOnce(new Error('Invalid credentials'));
    // Then mock login to resolve on second attempt
    auth.login.mockResolvedValueOnce(true);
    
    renderLogin();
    
    // Fill in with wrong credentials
    fireEvent.change(screen.getByLabelText(/username/i), { 
      target: { value: 'wronguser' } 
    });
    fireEvent.change(screen.getByLabelText(/password/i), { 
      target: { value: 'wrongpass' } 
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
    });
    
    // Fill in with correct credentials
    fireEvent.change(screen.getByLabelText(/username/i), { 
      target: { value: 'testuser' } 
    });
    fireEvent.change(screen.getByLabelText(/password/i), { 
      target: { value: 'password123' } 
    });
    
    // Submit the form again
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    // Check error is cleared
    await waitFor(() => {
      expect(screen.queryByText('Invalid username or password')).not.toBeInTheDocument();
    });
  });
});