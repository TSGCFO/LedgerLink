import React from 'react';
import { render } from '../../../utils/test-utils';
import { axe } from 'jest-axe';
import FileUploader from '../FileUploader';

describe('FileUploader Component - Accessibility', () => {
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

  it('should not have basic accessibility issues', async () => {
    const { container } = render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should maintain accessibility with error states', async () => {
    const { container } = render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
        error="File upload failed. Please try again."
      />
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should maintain accessibility with file selected state', async () => {
    const { container, rerender } = render(
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
    input.files = [file];
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Force rerender to simulate updated state
    rerender(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible table for field requirements', async () => {
    const { container } = render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    // Focus on the table specifically
    const table = container.querySelector('table');
    const results = await axe(table);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible drag and drop functionality', async () => {
    const { container } = render(
      <FileUploader 
        selectedTemplate={mockSelectedTemplate}
        onFileSelect={mockOnFileSelect}
      />
    );
    
    // Focus on the drag and drop area
    const dragDropArea = container.querySelector('[role="button"]') || 
                         container.querySelector('.MuiPaper-root');
    
    if (dragDropArea) {
      const results = await axe(dragDropArea);
      expect(results).toHaveNoViolations();
    } else {
      // If there's no explicit role, check that the interactive area is still accessible
      const textElement = container.querySelector('*:contains("Drag and drop")');
      const dragArea = textElement ? textElement.closest('div') : null;
      
      if (dragArea) {
        const results = await axe(dragArea);
        expect(results).toHaveNoViolations();
      }
    }
  });
});