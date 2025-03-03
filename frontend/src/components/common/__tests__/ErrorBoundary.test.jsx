import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '../ErrorBoundary';

// Mock console.error to prevent output during tests
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

// Create a component that throws an error
const ThrowError = () => {
  throw new Error('Test error');
};

describe('ErrorBoundary', () => {
  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <div data-testid="test-child">Test Content</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByTestId('test-child')).toBeInTheDocument();
    expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
  });
  
  it('renders error message when an error occurs', () => {
    // Suppress React's error boundary warning in test
    const spy = jest.spyOn(console, 'error');
    spy.mockImplementation(() => {});
    
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/please try again/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    
    spy.mockRestore();
  });
  
  it('calls onError when an error occurs', () => {
    const onError = jest.fn();
    
    // Suppress React's error boundary warning in test
    const spy = jest.spyOn(console, 'error');
    spy.mockImplementation(() => {});
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(onError).toHaveBeenCalled();
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error);
    expect(onError.mock.calls[0][0].message).toBe('Test error');
    
    spy.mockRestore();
  });
  
  it('retries rendering when retry button is clicked', () => {
    const resetErrorBoundary = jest.fn();
    
    // Suppress React's error boundary warning in test
    const spy = jest.spyOn(console, 'error');
    spy.mockImplementation(() => {});
    
    render(
      <ErrorBoundary resetErrorBoundary={resetErrorBoundary}>
        <ThrowError />
      </ErrorBoundary>
    );
    
    const retryButton = screen.getByRole('button', { name: /retry/i });
    retryButton.click();
    
    expect(resetErrorBoundary).toHaveBeenCalledTimes(1);
    
    spy.mockRestore();
  });
});