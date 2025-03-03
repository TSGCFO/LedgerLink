import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import { act } from 'react-dom/test-utils';
import BulkOperations from '../BulkOperations';
import * as apiMock from '../../../utils/apiClient';

// Mock child components
jest.mock('../TemplateSelector', () => ({ onSelect }) => (
  <div data-testid="template-selector">
    <button onClick={() => onSelect({ type: 'orders', name: 'Orders Import' })}>
      Select Template
    </button>
  </div>
));

jest.mock('../FileUploader', () => ({ selectedTemplate, onFileSelect, error }) => (
  <div data-testid="file-uploader">
    <span>Template: {selectedTemplate?.name}</span>
    {error && <span data-testid="uploader-error">{error}</span>}
    <button onClick={() => onFileSelect(new File(['content'], 'test.csv'))}>
      Upload File
    </button>
  </div>
));

jest.mock('../ValidationProgress', () => ({ progress, errors, isProcessing }) => (
  <div data-testid="validation-progress">
    <span>Progress: {progress}%</span>
    <span>Processing: {isProcessing ? 'true' : 'false'}</span>
    <span>Errors: {errors.length}</span>
  </div>
));

jest.mock('../ResultsSummary', () => ({ summary, errors, onRetry }) => (
  <div data-testid="results-summary">
    <span>Summary: {summary ? 'Available' : 'Not Available'}</span>
    <span>Errors: {errors?.length || 0}</span>
    <button onClick={onRetry}>Retry</button>
  </div>
));

// Mock fetch
global.fetch = jest.fn();

describe('BulkOperations Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('renders the component with initial stepper and template selector', () => {
    render(<BulkOperations />);
    
    // Check that initial stepper is displayed
    expect(screen.getByText('Select Template')).toBeInTheDocument();
    expect(screen.getByText('Upload File')).toBeInTheDocument();
    expect(screen.getByText('Validation')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
    
    // Check that template selector is displayed
    expect(screen.getByTestId('template-selector')).toBeInTheDocument();
  });

  it('progresses through the workflow when selecting a template', async () => {
    render(<BulkOperations />);
    
    // Step 1: Select template
    fireEvent.click(screen.getByText('Select Template'));
    
    // Check we're now at step 2 with the file uploader
    expect(screen.getByTestId('file-uploader')).toBeInTheDocument();
    expect(screen.getByText('Template: Orders Import')).toBeInTheDocument();
  });

  it('displays errors when they occur', async () => {
    render(<BulkOperations />);
    
    // Step 1: Select template
    fireEvent.click(screen.getByText('Select Template'));
    
    // Simulate an error
    act(() => {
      // Access the component instance and set error state
      const bulkOperationsInstance = screen.getByTestId('file-uploader').closest('div');
      const errorComponent = screen.getByText('Bulk Operations').closest('div');
      
      // Fire a custom error event that will be caught by the error handler
      const errorEvent = new CustomEvent('error', { 
        detail: { message: 'Test error message' } 
      });
      errorComponent.dispatchEvent(errorEvent);
    });
    
    // Now check if error is displayed
    await waitFor(() => {
      const errorAlert = screen.queryByText('Test error message');
      expect(errorAlert).toBeTruthy();
    });
  });

  it('handles file upload and moves to validation step', async () => {
    // Mock the fetch implementation for file upload
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        json: () => Promise.resolve({ 
          success: true,
          import_summary: { total_rows: 10, successful: 8, failed: 2 }
        })
      })
    );

    render(<BulkOperations />);
    
    // Step 1: Select template
    fireEvent.click(screen.getByText('Select Template'));
    
    // Step 2: Upload file
    fireEvent.click(screen.getByText('Upload File'));
    
    // Check that we're at step 3 with validation progress
    await waitFor(() => {
      expect(screen.getByTestId('validation-progress')).toBeInTheDocument();
    });
    
    // Check that progress is being tracked
    expect(screen.getByText(/Progress: \d+%/)).toBeInTheDocument();
    
    // Wait for validation to complete and move to results
    await waitFor(() => {
      expect(screen.getByTestId('results-summary')).toBeInTheDocument();
    });
  });

  it('allows retry after completion', async () => {
    // Mock the fetch implementation for file upload
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        json: () => Promise.resolve({ 
          success: true,
          import_summary: { total_rows: 10, successful: 10, failed: 0 }
        })
      })
    );

    render(<BulkOperations />);
    
    // Step 1: Select template
    fireEvent.click(screen.getByText('Select Template'));
    
    // Step 2: Upload file
    fireEvent.click(screen.getByText('Upload File'));
    
    // Wait for validation to complete and move to results
    await waitFor(() => {
      expect(screen.getByTestId('results-summary')).toBeInTheDocument();
    });
    
    // Click retry button
    fireEvent.click(screen.getByText('Retry'));
    
    // Check we're back at the file uploader
    await waitFor(() => {
      expect(screen.getByTestId('file-uploader')).toBeInTheDocument();
    });
  });

  it('handles validation errors', async () => {
    // Mock the fetch implementation to return validation errors
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        json: () => Promise.resolve({ 
          success: false,
          errors: [
            { row: 1, errors: { 'field1': ['Invalid value'] } },
            { row: 2, errors: { 'field2': ['Required field'] } }
          ],
          error: 'Validation failed with 2 errors'
        })
      })
    );

    render(<BulkOperations />);
    
    // Step 1: Select template
    fireEvent.click(screen.getByText('Select Template'));
    
    // Step 2: Upload file
    fireEvent.click(screen.getByText('Upload File'));
    
    // Check that validation is showing errors
    await waitFor(() => {
      expect(screen.getByText('Errors: 2')).toBeInTheDocument();
    });
  });
});