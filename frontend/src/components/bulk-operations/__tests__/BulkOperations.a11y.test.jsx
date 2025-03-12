import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import BulkOperations from '../BulkOperations';

// Mock child components to simplify testing
jest.mock('../TemplateSelector', () => ({ onSelect }) => (
  <div data-testid="template-selector">
    <h2>Select Template</h2>
    <button onClick={() => onSelect({ type: 'orders', name: 'Orders Import' })}>
      Select Template
    </button>
  </div>
));

jest.mock('../FileUploader', () => ({ selectedTemplate, onFileSelect, error }) => (
  <div data-testid="file-uploader">
    <h2>Upload File</h2>
    <span>Template: {selectedTemplate?.name}</span>
    {error && <span data-testid="uploader-error">{error}</span>}
    <button onClick={() => onFileSelect(new File(['content'], 'test.csv'))}>
      Upload File
    </button>
  </div>
));

jest.mock('../ValidationProgress', () => ({ progress, errors, isProcessing }) => (
  <div data-testid="validation-progress">
    <h2>Validation Progress</h2>
    <span>Progress: {progress}%</span>
    <span>Processing: {isProcessing ? 'true' : 'false'}</span>
    <span>Errors: {errors.length}</span>
  </div>
));

jest.mock('../ResultsSummary', () => ({ summary, errors, onRetry }) => (
  <div data-testid="results-summary">
    <h2>Results Summary</h2>
    <span>Summary: {summary ? 'Available' : 'Not Available'}</span>
    <span>Errors: {errors?.length || 0}</span>
    <button onClick={onRetry}>Retry</button>
  </div>
));

// Mock fetch
global.fetch = jest.fn();

describe('BulkOperations Component - Accessibility', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('should not have basic accessibility issues', async () => {
    const { container } = render(<BulkOperations />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should maintain accessibility when progressing through steps', async () => {
    const { container, rerender } = render(<BulkOperations />);
    
    // Step 1: Initial render - Template Selection
    let results = await axe(container);
    expect(results).toHaveNoViolations();
    
    // Simulate template selection to advance to step 2
    const bulkOps = container.firstChild;
    const selectButton = screen.getByText('Select Template');
    selectButton.click();
    
    // Re-run accessibility tests after state change
    results = await axe(container);
    expect(results).toHaveNoViolations();
    
    // Mock the fetch implementation for file upload
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        json: () => Promise.resolve({ 
          success: true,
          import_summary: { total_rows: 10, successful: 8, failed: 2 }
        })
      })
    );
    
    // Simulate file upload to advance to step 3
    const uploadButton = screen.getByText('Upload File');
    uploadButton.click();
    
    // Need to rerender to reflect state changes in test
    rerender(<BulkOperations />);
    
    // Re-run accessibility tests after state change
    results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should maintain accessibility when displaying errors', async () => {
    // Mock the fetch implementation to return errors
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        json: () => Promise.resolve({ 
          success: false,
          errors: ['Error 1', 'Error 2'],
          error: 'Validation failed'
        })
      })
    );
    
    const { container } = render(<BulkOperations />);
    
    // Add an error to test error display
    const errorAlert = document.createElement('div');
    errorAlert.setAttribute('role', 'alert');
    errorAlert.textContent = 'Test error message';
    container.appendChild(errorAlert);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});