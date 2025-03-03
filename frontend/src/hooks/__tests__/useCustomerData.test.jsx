import { renderHook, act, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { useCustomerData } from '../useCustomerData';

// Mock API client
vi.mock('../../utils/apiClient', () => ({
  customerApi: {
    get: vi.fn(),
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  handleApiError: vi.fn(error => error.message || 'Unknown error')
}));

describe('useCustomerData Hook', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useCustomerData());
    
    expect(result.current.customers).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(typeof result.current.fetchCustomers).toBe('function');
    expect(typeof result.current.fetchCustomer).toBe('function');
    expect(typeof result.current.createCustomer).toBe('function');
    expect(typeof result.current.updateCustomer).toBe('function');
    expect(typeof result.current.deleteCustomer).toBe('function');
  });

  it('fetches customers list', async () => {
    const mockCustomers = [
      { id: '1', company_name: 'Company 1' },
      { id: '2', company_name: 'Company 2' }
    ];
    
    const { customerApi } = await import('../../utils/apiClient');
    customerApi.list.mockResolvedValueOnce({
      results: mockCustomers,
      count: 2
    });
    
    const { result } = renderHook(() => useCustomerData());
    
    // Execute the fetch function
    act(() => {
      result.current.fetchCustomers();
    });
    
    // Should set loading state
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.customers).toEqual(mockCustomers);
      expect(result.current.totalCount).toBe(2);
      expect(customerApi.list).toHaveBeenCalledTimes(1);
    });
  });

  it('fetches a single customer', async () => {
    const mockCustomer = { id: '1', company_name: 'Test Company' };
    
    const { customerApi } = await import('../../utils/apiClient');
    customerApi.get.mockResolvedValueOnce(mockCustomer);
    
    const { result } = renderHook(() => useCustomerData());
    
    // Execute the fetch function
    act(() => {
      result.current.fetchCustomer('1');
    });
    
    // Should set loading state
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.currentCustomer).toEqual(mockCustomer);
      expect(customerApi.get).toHaveBeenCalledTimes(1);
      expect(customerApi.get).toHaveBeenCalledWith('1');
    });
  });

  it('creates a new customer', async () => {
    const newCustomer = {
      company_name: 'New Company',
      email: 'new@example.com'
    };
    
    const createdCustomer = {
      id: '3',
      ...newCustomer,
      created_at: '2025-03-03T00:00:00Z'
    };
    
    const { customerApi } = await import('../../utils/apiClient');
    customerApi.create.mockResolvedValueOnce(createdCustomer);
    
    const { result } = renderHook(() => useCustomerData());
    
    // Execute the create function
    let returnValue;
    await act(async () => {
      returnValue = await result.current.createCustomer(newCustomer);
    });
    
    expect(returnValue).toEqual(createdCustomer);
    expect(customerApi.create).toHaveBeenCalledTimes(1);
    expect(customerApi.create).toHaveBeenCalledWith(newCustomer);
  });

  it('updates an existing customer', async () => {
    const updatedData = {
      company_name: 'Updated Company',
      email: 'updated@example.com'
    };
    
    const updatedCustomer = {
      id: '1',
      ...updatedData,
      updated_at: '2025-03-03T00:00:00Z'
    };
    
    const { customerApi } = await import('../../utils/apiClient');
    customerApi.update.mockResolvedValueOnce(updatedCustomer);
    
    const { result } = renderHook(() => useCustomerData());
    
    // Execute the update function
    let returnValue;
    await act(async () => {
      returnValue = await result.current.updateCustomer('1', updatedData);
    });
    
    expect(returnValue).toEqual(updatedCustomer);
    expect(customerApi.update).toHaveBeenCalledTimes(1);
    expect(customerApi.update).toHaveBeenCalledWith('1', updatedData);
  });

  it('deletes a customer', async () => {
    const { customerApi } = await import('../../utils/apiClient');
    customerApi.delete.mockResolvedValueOnce({});
    
    const { result } = renderHook(() => useCustomerData());
    
    // Execute the delete function
    await act(async () => {
      await result.current.deleteCustomer('1');
    });
    
    expect(customerApi.delete).toHaveBeenCalledTimes(1);
    expect(customerApi.delete).toHaveBeenCalledWith('1');
  });

  it('handles errors when fetching customers', async () => {
    const { customerApi, handleApiError } = await import('../../utils/apiClient');
    customerApi.list.mockRejectedValueOnce(new Error('Network error'));
    
    const { result } = renderHook(() => useCustomerData());
    
    // Execute the fetch function
    act(() => {
      result.current.fetchCustomers();
    });
    
    // Should initially set loading state
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Network error');
      expect(handleApiError).toHaveBeenCalledTimes(1);
    });
  });
});