import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import ErrorDisplay from '../ErrorDisplay';

// Mock console.error to prevent test output noise
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});
afterAll(() => {
  console.error = originalError;
});

describe('ErrorDisplay Component', () => {
  beforeEach(() => {
    // Clear the mocks before each test
    console.error.mockClear();
  });
  
  it('renders children when there is no error', () => {
    render(
      <ErrorDisplay>
        <div data-testid="test-child">Child Component</div>
      </ErrorDisplay>
    );
    
    expect(screen.getByTestId('test-child')).toBeInTheDocument();
    expect(screen.getByText('Child Component')).toBeInTheDocument();
  });
  
  it('renders error UI when an error occurs', () => {
    // Create a component that will throw an error
    const ComponentWithError = () => {
      throw new Error('Test error message');
      return <div>This won't render</div>;
    };
    
    // Suppress React's error boundary logs for this test
    const originalConsoleError = console.error;
    console.error = jest.fn();
    
    render(
      <ErrorDisplay>
        <ComponentWithError />
      </ErrorDisplay>
    );
    
    // Check that error boundary caught the error
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByText('Error Details')).toBeInTheDocument();
    expect(screen.getByText('Reload Page')).toBeInTheDocument();
    
    // Verify console.error was called to log the error
    expect(console.error).toHaveBeenCalled();
  });
  
  it('shows generic message when error has no message', () => {
    // Create a component that will throw an error without a message
    const ComponentWithGenericError = () => {
      throw new Error();
      return <div>This won't render</div>;
    };
    
    render(
      <ErrorDisplay>
        <ComponentWithGenericError />
      </ErrorDisplay>
    );
    
    // Check that a generic error message is shown
    expect(screen.getByText('An unexpected error occurred')).toBeInTheDocument();
  });
  
  it('displays error stack trace', () => {
    // Create an error with a stack trace
    const error = new Error('Stack trace test');
    error.stack = 'Error: Stack trace test\n    at Component\n    at ErrorBoundary';
    
    // Component that throws the prepared error
    const ComponentWithStackTrace = () => {
      throw error;
      return <div>This won't render</div>;
    };
    
    render(
      <ErrorDisplay>
        <ComponentWithStackTrace />
      </ErrorDisplay>
    );
    
    // Check that the stack trace is displayed
    expect(screen.getByText(/Error: Stack trace test/)).toBeInTheDocument();
    expect(screen.getByText(/at Component/)).toBeInTheDocument();
    expect(screen.getByText(/at ErrorBoundary/)).toBeInTheDocument();
  });
  
  it('calls componentDidCatch when an error occurs', () => {
    // Mock componentDidCatch
    const originalComponentDidCatch = ErrorDisplay.prototype.componentDidCatch;
    ErrorDisplay.prototype.componentDidCatch = jest.fn();
    
    // Component that throws an error
    const ErrorComponent = () => {
      throw new Error('Component error');
      return null;
    };
    
    render(
      <ErrorDisplay>
        <ErrorComponent />
      </ErrorDisplay>
    );
    
    // Verify componentDidCatch was called
    expect(ErrorDisplay.prototype.componentDidCatch).toHaveBeenCalled();
    
    // Restore original method
    ErrorDisplay.prototype.componentDidCatch = originalComponentDidCatch;
  });
});