import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import ValidationProgress from '../ValidationProgress';

describe('ValidationProgress Component', () => {
  it('displays progress bar with correct value', () => {
    render(
      <ValidationProgress 
        progress={50} 
        errors={[]} 
        isProcessing={true} 
      />
    );
    
    expect(screen.getByText('File Validation')).toBeInTheDocument();
    expect(screen.getByText('Validating...')).toBeInTheDocument();
    expect(screen.getByText('50% Complete')).toBeInTheDocument();
    
    // Check progress bar exists
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
  });
  
  it('shows processing state correctly', () => {
    render(
      <ValidationProgress 
        progress={75} 
        errors={[]} 
        isProcessing={true} 
      />
    );
    
    expect(screen.getByText('Validating...')).toBeInTheDocument();
    expect(screen.getByText('Validating file contents and processing data. This may take a few moments...')).toBeInTheDocument();
  });
  
  it('shows completion state with no errors', () => {
    render(
      <ValidationProgress 
        progress={100} 
        errors={[]} 
        isProcessing={false} 
      />
    );
    
    expect(screen.getByText('Validation Complete')).toBeInTheDocument();
    expect(screen.getByText('File validation successful. Processing data...')).toBeInTheDocument();
  });
  
  it('displays errors when validation fails', () => {
    const mockErrors = [
      { row: 1, errors: { name: ['This field is required'] } },
      { row: 2, errors: { quantity: ['Must be a positive number'] } },
      'Invalid file structure'
    ];
    
    render(
      <ValidationProgress 
        progress={100} 
        errors={mockErrors} 
        isProcessing={false} 
      />
    );
    
    expect(screen.getByText('Validation Failed')).toBeInTheDocument();
    expect(screen.getByText('Validation Errors:')).toBeInTheDocument();
    expect(screen.getByText('3 Errors Found')).toBeInTheDocument();
    
    // Check specific error messages
    expect(screen.getByText('Row 1')).toBeInTheDocument();
    expect(screen.getByText(/name: This field is required/)).toBeInTheDocument();
    expect(screen.getByText('Row 2')).toBeInTheDocument();
    expect(screen.getByText(/quantity: Must be a positive number/)).toBeInTheDocument();
    expect(screen.getByText('Invalid file structure')).toBeInTheDocument();
    
    // Check warning message
    expect(screen.getByText('Please correct these errors and try uploading again.')).toBeInTheDocument();
  });
  
  it('handles string error format correctly', () => {
    render(
      <ValidationProgress 
        progress={100} 
        errors={['Generic error message']} 
        isProcessing={false} 
      />
    );
    
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Generic error message')).toBeInTheDocument();
  });
  
  it('handles object error format correctly', () => {
    const complexError = {
      row: 5,
      errors: {
        field1: ['Error 1', 'Error 2'],
        field2: ['Error 3']
      }
    };
    
    render(
      <ValidationProgress 
        progress={100} 
        errors={[complexError]} 
        isProcessing={false} 
      />
    );
    
    expect(screen.getByText('Row 5')).toBeInTheDocument();
    expect(screen.getByText(/field1: Error 1, Error 2; field2: Error 3/)).toBeInTheDocument();
  });
  
  it('updates UI based on processing state change', () => {
    const { rerender } = render(
      <ValidationProgress 
        progress={50} 
        errors={[]} 
        isProcessing={true} 
      />
    );
    
    expect(screen.getByText('Validating...')).toBeInTheDocument();
    
    // Update to finished state
    rerender(
      <ValidationProgress 
        progress={100} 
        errors={[]} 
        isProcessing={false} 
      />
    );
    
    expect(screen.getByText('Validation Complete')).toBeInTheDocument();
    expect(screen.getByText('File validation successful. Processing data...')).toBeInTheDocument();
  });
});