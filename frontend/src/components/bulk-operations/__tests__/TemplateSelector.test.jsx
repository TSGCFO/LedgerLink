import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import TemplateSelector from '../TemplateSelector';

// Mock fetch API
global.fetch = jest.fn();

describe('TemplateSelector Component', () => {
  const mockTemplates = [
    {
      type: 'orders',
      name: 'Orders Import',
      description: 'Import order data',
      fieldCount: 10
    },
    {
      type: 'products',
      name: 'Products Import',
      description: 'Import product data',
      fieldCount: 5
    }
  ];

  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
    
    // Mock successful API response
    global.fetch.mockImplementation((url) => {
      if (url === '/api/v1/bulk-operations/templates/') {
        return Promise.resolve({
          json: () => Promise.resolve({
            success: true,
            data: { templates: mockTemplates }
          })
        });
      } else if (url.includes('/template-info/')) {
        return Promise.resolve({
          json: () => Promise.resolve({
            success: true,
            data: {
              fields: {
                id: { description: 'Unique identifier' },
                name: { description: 'Name of the item' }
              },
              requiredFields: ['id', 'name'],
              fieldTypes: { id: 'integer', name: 'string' }
            }
          })
        });
      }
      return Promise.reject(new Error('Unhandled API call'));
    });
  });

  it('displays loading state initially', () => {
    render(<TemplateSelector onSelect={mockOnSelect} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('fetches and displays templates', async () => {
    render(<TemplateSelector onSelect={mockOnSelect} />);
    
    // Wait for templates to load
    await waitFor(() => {
      expect(screen.getByText('Orders Import')).toBeInTheDocument();
      expect(screen.getByText('Products Import')).toBeInTheDocument();
    });
    
    // Check for template descriptions
    expect(screen.getByText('Import order data')).toBeInTheDocument();
    expect(screen.getByText('Import product data')).toBeInTheDocument();
    
    // Check field counts are displayed
    expect(screen.getByText('10 fields')).toBeInTheDocument();
    expect(screen.getByText('5 fields')).toBeInTheDocument();
  });

  it('allows template selection', async () => {
    render(<TemplateSelector onSelect={mockOnSelect} />);
    
    // Wait for templates to load
    await waitFor(() => {
      expect(screen.getByText('Orders Import')).toBeInTheDocument();
    });
    
    // Click on a template
    fireEvent.click(screen.getByText('Orders Import').closest('.MuiCardContent-root'));
    
    // Check that second fetch was called to get template info
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/templates/template-info/orders/')
      );
    });
    
    // Wait for the Next button to appear
    await waitFor(() => {
      expect(screen.getByText('Next: Upload File')).toBeInTheDocument();
    });
    
    // Click the Next button
    fireEvent.click(screen.getByText('Next: Upload File'));
    
    // Check that onSelect was called with the template data
    expect(mockOnSelect).toHaveBeenCalledWith(expect.objectContaining({
      type: 'orders',
      name: 'Orders Import',
      fields: expect.any(Object),
      requiredFields: expect.any(Array),
      fieldTypes: expect.any(Object)
    }));
  });

  it('handles template download', async () => {
    // Mock to test download functionality
    const createObjectURL = jest.fn();
    const revokObjectURL = jest.fn();
    
    global.URL.createObjectURL = createObjectURL;
    global.URL.revokeObjectURL = revokObjectURL;
    
    const appendChildMock = jest.fn();
    const removeChildMock = jest.fn();
    const clickMock = jest.fn();
    
    document.body.appendChild = appendChildMock;
    document.body.removeChild = removeChildMock;
    
    // Mock blob response for download
    global.fetch.mockImplementationOnce((url) => {
      if (url === '/api/v1/bulk-operations/templates/') {
        return Promise.resolve({
          json: () => Promise.resolve({
            success: true,
            data: { templates: mockTemplates }
          })
        });
      }
      return Promise.resolve({
        ok: true,
        blob: () => Promise.resolve(new Blob(['test data']))
      });
    });
    
    render(<TemplateSelector onSelect={mockOnSelect} />);
    
    // Wait for templates to load
    await waitFor(() => {
      expect(screen.getByText('Orders Import')).toBeInTheDocument();
    });
    
    // Find and click the Template download button
    const downloadButtons = screen.getAllByText('Template');
    fireEvent.click(downloadButtons[0]);
    
    // Wait for download logic to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/templates/orders/download/')
      );
      expect(createObjectURL).toHaveBeenCalled();
    });
  });

  it('displays error when template fetch fails', async () => {
    // Mock API failure
    global.fetch.mockImplementationOnce(() => 
      Promise.resolve({
        json: () => Promise.resolve({
          success: false,
          error: 'Failed to fetch templates'
        })
      })
    );
    
    render(<TemplateSelector onSelect={mockOnSelect} />);
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch templates')).toBeInTheDocument();
    });
  });

  it('displays error when network request fails', async () => {
    // Mock network failure
    global.fetch.mockImplementationOnce(() => 
      Promise.reject(new Error('Network error'))
    );
    
    render(<TemplateSelector onSelect={mockOnSelect} />);
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText('Error loading templates: Network error')).toBeInTheDocument();
    });
  });
});