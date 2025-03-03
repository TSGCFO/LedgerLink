import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import FileUploader from '../FileUploader';

describe('FileUploader Component', () => {
  const mockSelectedTemplate = {
    type: 'orders',
    name: 'Orders Import',
    requiredFields: ['id', 'name', 'quantity'],
    fieldTypes: {
      id: 'integer',
      name: 'string',
      quantity: 'integer',
      price: 'decimal',
      date: 'date'
    },
    fields: {
      id: { description: 'Unique identifier' },
      name: { description: 'Product name' },
      quantity: { description: 'Order quantity' },
      price: { description: 'Unit price' },
      date: { description: 'Order date' }
    }
  };
  
  const mockOnFileSelect = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders the file upload area with template name', () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    expect(screen.getByText('Upload Orders Import File')).toBeInTheDocument();
    expect(screen.getByText('Drag and drop your file here or click to browse')).toBeInTheDocument();
    expect(screen.getByText('Supported formats: CSV, XLSX, XLS (Max 10MB)')).toBeInTheDocument();
  });
  
  it('displays field requirements table', () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    expect(screen.getByText('Field Requirements')).toBeInTheDocument();
    
    // Check that all fields are listed
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('name')).toBeInTheDocument();
    expect(screen.getByText('quantity')).toBeInTheDocument();
    expect(screen.getByText('price')).toBeInTheDocument();
    expect(screen.getByText('date')).toBeInTheDocument();
    
    // Check that field types are displayed
    expect(screen.getByText('integer')).toBeInTheDocument();
    expect(screen.getByText('string')).toBeInTheDocument();
    expect(screen.getByText('decimal')).toBeInTheDocument();
    expect(screen.getByText('date')).toBeInTheDocument();
    
    // Check required indicators
    const successIcons = document.querySelectorAll('.MuiSvgIcon-colorSuccess');
    expect(successIcons.length).toBeGreaterThanOrEqual(3); // At least 3 required fields
  });
  
  it('handles file input change', async () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    // Create a test file
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    
    // Get the hidden file input
    const input = document.querySelector('input[type="file"]');
    
    // Mock the file.text() method
    file.text = jest.fn().mockResolvedValue('id,name,quantity,price,date\n1,Test,5,10.99,2023-01-01');
    
    // Trigger file selection
    fireEvent.change(input, { target: { files: [file] } });
    
    // Wait for validation to complete
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });
  
  it('displays validation errors for invalid files', async () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    // Create a test file with wrong extension
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    // Get the hidden file input
    const input = document.querySelector('input[type="file"]');
    
    // Trigger file selection
    fireEvent.change(input, { target: { files: [file] } });
    
    // Wait for validation error to appear
    await waitFor(() => {
      expect(screen.getByText('Unsupported file format. Please use CSV or Excel files.')).toBeInTheDocument();
    });
    
    // Check that onFileSelect was not called
    expect(mockOnFileSelect).not.toHaveBeenCalled();
  });
  
  it('validates CSV header rows', async () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    // Create a test file with missing required fields
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    
    // Mock the file.text() method to return CSV with missing required fields
    file.text = jest.fn().mockResolvedValue('id,price,date\n1,10.99,2023-01-01');
    
    // Get the hidden file input
    const input = document.querySelector('input[type="file"]');
    
    // Trigger file selection
    fireEvent.change(input, { target: { files: [file] } });
    
    // Wait for validation error to appear
    await waitFor(() => {
      expect(screen.getByText('Missing required columns: name, quantity')).toBeInTheDocument();
    });
    
    // Check that onFileSelect was not called
    expect(mockOnFileSelect).not.toHaveBeenCalled();
  });
  
  it('shows external error message when provided', () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
        error="External error from parent component"
      />
    );
    
    expect(screen.getByText('External error from parent component')).toBeInTheDocument();
  });
  
  it('handles drag and drop', async () => {
    render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    // Create a test file
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    file.text = jest.fn().mockResolvedValue('id,name,quantity,price,date\n1,Test,5,10.99,2023-01-01');
    
    // Get the drop area
    const dropArea = screen.getByText('Drag and drop your file here or click to browse').closest('div');
    
    // Mock DataTransfer
    const dataTransfer = {
      files: [file]
    };
    
    // Trigger drag events
    fireEvent.dragEnter(dropArea, { dataTransfer });
    fireEvent.dragOver(dropArea, { dataTransfer });
    fireEvent.drop(dropArea, { dataTransfer });
    
    // Wait for validation to complete
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });
});