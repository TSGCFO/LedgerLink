import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProtectedRoute from '../ProtectedRoute';

// Mock localStorage
const mockLocalStorage = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

describe('ProtectedRoute Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  test('renders child component', () => {
    render(
      <ProtectedRoute>
        <div data-testid="test-child">Protected Content</div>
      </ProtectedRoute>
    );
    
    expect(screen.getByTestId('test-child')).toBeInTheDocument();
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('sets development token if no token exists', () => {
    // Ensure no token exists initially
    expect(localStorage.getItem('auth_token')).toBeNull();
    
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );
    
    // Check that token was set
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'development_token');
    expect(localStorage.getItem('auth_token')).toBe('development_token');
  });

  test('does not set development token if token already exists', () => {
    // Set a token before rendering
    localStorage.setItem('auth_token', 'existing_token');
    
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );
    
    // Token should still be the existing one
    expect(localStorage.getItem('auth_token')).toBe('existing_token');
    
    // localStorage.setItem should be called just once (in our beforeEach setup)
    expect(localStorage.setItem).toHaveBeenCalledTimes(1);
  });

  test('handles multiple children correctly', () => {
    render(
      <ProtectedRoute>
        <div data-testid="child1">Child 1</div>
        <div data-testid="child2">Child 2</div>
      </ProtectedRoute>
    );
    
    expect(screen.getByTestId('child1')).toBeInTheDocument();
    expect(screen.getByTestId('child2')).toBeInTheDocument();
    expect(screen.getByText('Child 1')).toBeInTheDocument();
    expect(screen.getByText('Child 2')).toBeInTheDocument();
  });
});