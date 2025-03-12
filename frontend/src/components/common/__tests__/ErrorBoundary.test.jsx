import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import ErrorBoundary from '../ErrorBoundary';

// Create a test component that throws an error
const ErrorComponent = () => {
  throw new Error('Test error');
};

// Mock console.error to prevent error logs in test output
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

describe('ErrorBoundary', () => {
  test('renders children when no error occurs', () => {
    const testMessage = 'Test content';
    render(
      <ErrorBoundary>
        <div>{testMessage}</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByText(testMessage)).toBeInTheDocument();
  });
  
  test('renders error UI when an error occurs', () => {
    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );
    
    // Check that the error message is displayed
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/Test error/i)).toBeInTheDocument();
  });
});