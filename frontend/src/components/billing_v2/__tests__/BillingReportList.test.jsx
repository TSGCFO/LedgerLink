import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BillingReportList from '../BillingReportList';
import * as billingV2ApiModule from '../../../utils/api/billingV2Api';
import logger from '../../../utils/logger';

// Mock the API client
jest.mock('../../../utils/api/billingV2Api', () => ({
  billingV2Api: {
    downloadBillingReport: jest.fn().mockResolvedValue(true)
  }
}));

// Mock the logger
jest.mock('../../../utils/logger', () => ({
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  logApiRequest: jest.fn(),
  logApiResponse: jest.fn(),
  logApiError: jest.fn(),
}));

describe('BillingReportList Component', () => {
  const mockReports = [
    {
      id: '123e4567-e89b-12d3-a456-426614174000',
      customer_id: 1,
      customer_name: 'Test Company',
      start_date: '2025-01-01',
      end_date: '2025-02-01',
      total_amount: 1500.00,
      created_at: '2025-01-15T10:30:00Z'
    },
    {
      id: '223e4567-e89b-12d3-a456-426614174001',
      customer_id: 2,
      customer_name: 'Another Company',
      start_date: '2025-02-01',
      end_date: '2025-03-01',
      total_amount: 2500.00,
      created_at: '2025-02-15T10:30:00Z'
    }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock window.location.href
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { href: '' }
    });
  });
  
  test('renders the billing report list with data', () => {
    render(<BillingReportList reports={mockReports} />);
    
    // Check that reports are displayed
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('Another Company')).toBeInTheDocument();
    
    // Check for formatted currency amounts (should match formatCurrency implementation)
    expect(screen.getByText('$1,500.00')).toBeInTheDocument();
    expect(screen.getByText('$2,500.00')).toBeInTheDocument();
  });
  
  test('shows loading state when loading prop is true', () => {
    render(<BillingReportList reports={[]} loading={true} />);
    
    // Should show loading indicator
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.queryByText('No reports found')).not.toBeInTheDocument();
  });
  
  test('shows empty state message when no reports', () => {
    render(<BillingReportList reports={[]} loading={false} />);
    
    // Should show empty state message
    expect(screen.getByText(/No reports found/)).toBeInTheDocument();
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });
  
  test('calls onReportSelected when report is clicked', () => {
    const onReportSelected = jest.fn();
    render(
      <BillingReportList 
        reports={mockReports} 
        onReportSelected={onReportSelected} 
      />
    );
    
    // Find and click view button for first report
    const viewButtons = screen.getAllByRole('button', { name: /view/i });
    fireEvent.click(viewButtons[0]);
    
    // onReportSelected should be called with the report ID
    expect(onReportSelected).toHaveBeenCalledWith(mockReports[0].id);
  });
  
  test('highlights selected report', () => {
    render(
      <BillingReportList 
        reports={mockReports} 
        selectedReportId={mockReports[0].id}
      />
    );
    
    // First report should be highlighted (has Mui-selected class)
    const listItems = screen.getAllByRole('button');
    expect(listItems[0]).toHaveClass('Mui-selected');
  });
  
  test('calls download API when download button is clicked', () => {
    // Mock window.location before the test
    const originalHref = window.location.href;
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { href: '' }
    });
    
    // Mock apiClient baseURL
    const mockBaseURL = 'http://test-api.example.com';
    jest.mock('../../../utils/apiClient', () => ({
      defaults: {
        baseURL: mockBaseURL
      }
    }));
    
    render(<BillingReportList reports={mockReports} />);
    
    // Find and click download button for first report
    const downloadButtons = screen.getAllByRole('button', { name: /download/i });
    fireEvent.click(downloadButtons[0]);
    
    // Should call the API
    expect(billingV2ApiModule.billingV2Api.downloadBillingReport).toHaveBeenCalledWith(
      mockReports[0].id, 
      'csv'
    );
    
    // Restore original window.location
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { href: originalHref }
    });
  });
});