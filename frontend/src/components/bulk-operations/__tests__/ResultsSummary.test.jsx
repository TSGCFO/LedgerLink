import React from 'react';
import { render, screen, fireEvent } from '../../../utils/test-utils';
import ResultsSummary from '../ResultsSummary';

describe('ResultsSummary Component', () => {
  const mockSummary = {
    total_rows: 100,
    successful: 95,
    failed: 5
  };
  
  const mockErrors = [
    { row: 1, errors: { 'field1': ['Invalid value'] } },
    { row: 2, errors: { 'field2': ['Required field'] } },
    { row: 3, errors: { 'field3': ['Out of range'] } },
    { row: 4, errors: { 'field4': ['Invalid format'] } },
    { row: 5, errors: { 'field5': ['Duplicate value'] } }
  ];
  
  const mockOnRetry = jest.fn();
  
  it('displays successful import results', () => {
    const successfulSummary = {
      total_rows: 100,
      successful: 100,
      failed: 0
    };
    
    render(
      <ResultsSummary 
        summary={successfulSummary} 
        errors={[]} 
        onRetry={mockOnRetry} 
      />
    );
    
    // Check title and status
    expect(screen.getByText('Import Results')).toBeInTheDocument();
    expect(screen.getByText('Import Successful')).toBeInTheDocument();
    
    // Check summary cards
    expect(screen.getByText('Total Rows')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('Successful')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
    
    // Check retry button
    expect(screen.getByText('Upload Another File')).toBeInTheDocument();
  });
  
  it('displays partially successful import results with errors', () => {
    render(
      <ResultsSummary 
        summary={mockSummary} 
        errors={mockErrors} 
        onRetry={mockOnRetry} 
      />
    );
    
    // Check title and status
    expect(screen.getByText('Import Results')).toBeInTheDocument();
    expect(screen.getByText('Import Completed with Errors')).toBeInTheDocument();
    
    // Check summary cards
    expect(screen.getByText('Total Rows')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument(); // total rows
    expect(screen.getByText('95')).toBeInTheDocument(); // successful
    expect(screen.getByText('5')).toBeInTheDocument(); // failed
    
    // Check warning message
    expect(screen.getByText('Some records failed to import. Please review the errors below and try again with corrected data.')).toBeInTheDocument();
    
    // Check errors section
    expect(screen.getByText('Hide Errors (5)')).toBeInTheDocument();
    
    // Check error details
    expect(screen.getByText('Row 1')).toBeInTheDocument();
    expect(screen.getByText(/field1: Invalid value/)).toBeInTheDocument();
  });
  
  it('displays failed import state when summary is null', () => {
    render(
      <ResultsSummary 
        summary={null} 
        errors={mockErrors} 
        onRetry={mockOnRetry} 
      />
    );
    
    expect(screen.getByText('Import Failed')).toBeInTheDocument();
    expect(screen.getByText('Hide Errors (5)')).toBeInTheDocument();
  });
  
  it('toggles error visibility when hide/show button is clicked', () => {
    render(
      <ResultsSummary 
        summary={mockSummary} 
        errors={mockErrors} 
        onRetry={mockOnRetry} 
      />
    );
    
    // Errors should be visible by default
    expect(screen.getByText('Row 1')).toBeInTheDocument();
    
    // Click hide button
    fireEvent.click(screen.getByText('Hide Errors (5)'));
    
    // Button text should change, and errors should be hidden
    expect(screen.getByText('Show Errors (5)')).toBeInTheDocument();
    expect(screen.queryByText('Row 1')).not.toBeInTheDocument();
    
    // Click show button
    fireEvent.click(screen.getByText('Show Errors (5)'));
    
    // Errors should be visible again
    expect(screen.getByText('Row 1')).toBeInTheDocument();
  });
  
  it('handles string error format correctly', () => {
    const stringErrors = [
      'Generic error message',
      'Another general error'
    ];
    
    render(
      <ResultsSummary 
        summary={mockSummary} 
        errors={stringErrors} 
        onRetry={mockOnRetry} 
      />
    );
    
    expect(screen.getByText('Generic error message')).toBeInTheDocument();
    expect(screen.getByText('Another general error')).toBeInTheDocument();
  });
  
  it('calls onRetry when upload another file button is clicked', () => {
    render(
      <ResultsSummary 
        summary={mockSummary} 
        errors={mockErrors} 
        onRetry={mockOnRetry} 
      />
    );
    
    // Click the retry button
    fireEvent.click(screen.getByText('Upload Another File'));
    
    // Verify onRetry callback was called
    expect(mockOnRetry).toHaveBeenCalledTimes(1);
  });
});