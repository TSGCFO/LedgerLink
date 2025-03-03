import { render, screen, fireEvent, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import DataTable from '../DataTable';

// Sample test data
const testData = [
  { id: '1', name: 'Alpha Company', revenue: 50000, status: 'active' },
  { id: '2', name: 'Beta Inc', revenue: 75000, status: 'inactive' },
  { id: '3', name: 'Gamma Corp', revenue: 25000, status: 'active' },
  { id: '4', name: 'Delta Ltd', revenue: 100000, status: 'active' },
  { id: '5', name: 'Epsilon Services', revenue: 60000, status: 'pending' }
];

// Column definitions
const columns = [
  { field: 'name', headerName: 'Company Name', sortable: true, width: 200 },
  { field: 'revenue', headerName: 'Annual Revenue', sortable: true, width: 150, 
    valueFormatter: (params) => `$${params.value.toLocaleString()}` },
  { field: 'status', headerName: 'Status', sortable: false, width: 120, 
    renderCell: (params) => (
      <span className={`status-${params.value}`}>{params.value}</span>
    ) }
];

describe('DataTable Component', () => {
  it('renders the table with headers and data', () => {
    render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
      />
    );
    
    // Check headers
    expect(screen.getByText('Company Name')).toBeInTheDocument();
    expect(screen.getByText('Annual Revenue')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    
    // Check data rows
    expect(screen.getByText('Alpha Company')).toBeInTheDocument();
    expect(screen.getByText('$50,000')).toBeInTheDocument();
    expect(screen.getByText('Beta Inc')).toBeInTheDocument();
    expect(screen.getByText('Gamma Corp')).toBeInTheDocument();
    expect(screen.getByText('Delta Ltd')).toBeInTheDocument();
    expect(screen.getByText('Epsilon Services')).toBeInTheDocument();
  });

  it('renders custom cell components', () => {
    render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
      />
    );
    
    // Check custom rendered cells
    const activeStatuses = screen.getAllByText('active');
    const inactiveStatus = screen.getByText('inactive');
    const pendingStatus = screen.getByText('pending');
    
    expect(activeStatuses.length).toBe(3);
    expect(activeStatuses[0].className).toBe('status-active');
    expect(inactiveStatus.className).toBe('status-inactive');
    expect(pendingStatus.className).toBe('status-pending');
  });

  it('handles sorting when headers are clicked', () => {
    const onSortChange = vi.fn();
    
    render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
        onSortChange={onSortChange}
        defaultSortField="name"
        defaultSortDirection="asc"
      />
    );
    
    // Click on sortable header
    const nameHeader = screen.getByText('Company Name');
    fireEvent.click(nameHeader);
    
    // Should call onSortChange with sorting parameters
    expect(onSortChange).toHaveBeenCalledWith('name', 'desc');
    
    // Click again to toggle sort direction
    fireEvent.click(nameHeader);
    expect(onSortChange).toHaveBeenCalledWith('name', 'asc');
    
    // Click on revenue header
    const revenueHeader = screen.getByText('Annual Revenue');
    fireEvent.click(revenueHeader);
    expect(onSortChange).toHaveBeenCalledWith('revenue', 'asc');
  });

  it('renders pagination controls', () => {
    // Create more data to trigger pagination
    const paginatedData = Array(25).fill(null).map((_, index) => ({
      id: `${index + 1}`,
      name: `Company ${index + 1}`,
      revenue: 10000 * (index + 1),
      status: index % 2 === 0 ? 'active' : 'inactive'
    }));
    
    render(
      <DataTable
        data={paginatedData}
        columns={columns}
        pageSize={10}
      />
    );
    
    // Check pagination elements
    expect(screen.getByText('1-10 of 25')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to next page')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to previous page')).toBeInTheDocument();
    
    // Check disabled state of previous page button on first page
    expect(screen.getByLabelText('Go to previous page')).toBeDisabled();
    
    // Go to next page
    fireEvent.click(screen.getByLabelText('Go to next page'));
    
    // Now the previous page button should be enabled
    expect(screen.getByLabelText('Go to previous page')).not.toBeDisabled();
    
    // Should show new range
    expect(screen.getByText('11-20 of 25')).toBeInTheDocument();
  });

  it('handles row selection', async () => {
    const onRowSelect = vi.fn();
    const user = userEvent.setup();
    
    render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
        selectable={true}
        onRowSelect={onRowSelect}
      />
    );
    
    // Check that checkboxes are rendered
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBe(testData.length + 1); // +1 for header checkbox
    
    // Click the first row's checkbox
    await user.click(checkboxes[1]);
    expect(onRowSelect).toHaveBeenCalledWith(['1']);
    
    // Click the second row's checkbox
    await user.click(checkboxes[2]);
    expect(onRowSelect).toHaveBeenCalledWith(['1', '2']);
    
    // Click header checkbox to select all
    await user.click(checkboxes[0]);
    expect(onRowSelect).toHaveBeenCalledWith(testData.map(item => item.id));
  });

  it('handles empty data state', () => {
    render(
      <DataTable
        data={[]}
        columns={columns}
        pageSize={10}
        noDataMessage="No records found"
      />
    );
    
    // Should show empty state message
    expect(screen.getByText('No records found')).toBeInTheDocument();
    
    // Pagination should not be visible
    expect(screen.queryByText('0-0 of 0')).not.toBeInTheDocument();
  });

  it('handles loading state', () => {
    render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
        loading={true}
      />
    );
    
    // Should show loading indicator
    expect(screen.getByTestId('table-loading-indicator')).toBeInTheDocument();
    
    // Table data should not be visible during loading
    expect(screen.queryByText('Alpha Company')).not.toBeInTheDocument();
  });

  it('supports keyboard navigation', async () => {
    const onRowClick = vi.fn();
    const user = userEvent.setup();
    
    render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
        onRowClick={onRowClick}
      />
    );
    
    // Tab to the first row
    const firstRow = screen.getByText('Alpha Company').closest('tr');
    await user.tab();
    await user.tab();
    
    // Press Enter to select row
    await user.keyboard('{Enter}');
    expect(onRowClick).toHaveBeenCalledWith(expect.objectContaining({ 
      id: '1', 
      name: 'Alpha Company' 
    }));
  });

  it('is accessible', () => {
    const { container } = render(
      <DataTable
        data={testData}
        columns={columns}
        pageSize={10}
        aria-label="Companies data"
      />
    );
    
    // Table should have appropriate role
    const table = container.querySelector('table');
    expect(table).toHaveAttribute('role', 'grid');
    
    // Headers should have appropriate role
    const headers = container.querySelectorAll('th');
    headers.forEach(header => {
      expect(header).toHaveAttribute('role', 'columnheader');
    });
    
    // Check for appropriate aria attributes on sortable columns
    const sortableHeaders = Array.from(headers).filter(
      header => header.textContent === 'Company Name' || header.textContent === 'Annual Revenue'
    );
    
    sortableHeaders.forEach(header => {
      expect(header).toHaveAttribute('aria-sort', 'none');
    });
  });
});