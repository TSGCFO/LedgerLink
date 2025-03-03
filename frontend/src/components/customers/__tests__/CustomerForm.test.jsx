import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import CustomerForm from '../CustomerForm';

// Mock dependencies
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({ id: null }) // Default to create mode
}));

vi.mock('../../../utils/apiClient', () => ({
  customerApi: {
    create: vi.fn(() => Promise.resolve({ id: '123' })),
    update: vi.fn(() => Promise.resolve({ id: '123' })),
    get: vi.fn(() => Promise.resolve({
      id: '123',
      company_name: 'Test Company',
      legal_business_name: 'Test Legal Name',
      email: 'test@example.com',
      phone: '123-456-7890',
      address: '123 Test St',
      city: 'Test City',
      state: 'TS',
      zip: '12345',
      country: 'Test Country',
      business_type: 'Test Type',
      is_active: true
    }))
  },
  handleApiError: vi.fn(error => error.message || 'Unknown error')
}));

describe('CustomerForm Component', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders the form in create mode', () => {
    render(<CustomerForm />);
    
    expect(screen.getByText('New Customer')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create customer/i })).toBeInTheDocument();

    // Check form fields are present
    expect(screen.getByLabelText(/company name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/legal business name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/city/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/state\/province/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/zip\/postal code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/country/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/business type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/active/i)).toBeInTheDocument();
  });

  it('shows validation errors when form is submitted with invalid data', async () => {
    render(<CustomerForm />);
    
    // Submit the form without filling required fields
    const submitButton = screen.getByRole('button', { name: /create customer/i });
    fireEvent.click(submitButton);
    
    // Wait for validation errors to appear
    await waitFor(() => {
      expect(screen.getByText(/company name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/legal business name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    render(<CustomerForm />);
    
    const emailInput = screen.getByLabelText(/email/i);
    userEvent.type(emailInput, 'invalid-email');
    
    // Click elsewhere to trigger validation
    userEvent.click(screen.getByLabelText(/company name/i));
    
    // Submit the form to trigger validation
    const submitButton = screen.getByRole('button', { name: /create customer/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it('validates phone number format', async () => {
    render(<CustomerForm />);
    
    // Fill required fields first
    userEvent.type(screen.getByLabelText(/company name/i), 'Test Company');
    userEvent.type(screen.getByLabelText(/legal business name/i), 'Test Legal Name');
    userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    
    // Enter invalid phone number
    const phoneInput = screen.getByLabelText(/phone/i);
    userEvent.type(phoneInput, 'abc');
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create customer/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid phone number/i)).toBeInTheDocument();
    });
  });

  it('submits the form with valid data in create mode', async () => {
    const { customerApi } = await import('../../../utils/apiClient');
    
    render(<CustomerForm />);
    
    // Fill required fields
    userEvent.type(screen.getByLabelText(/company name/i), 'Test Company');
    userEvent.type(screen.getByLabelText(/legal business name/i), 'Test Legal Name');
    userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create customer/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(customerApi.create).toHaveBeenCalledTimes(1);
      expect(customerApi.create).toHaveBeenCalledWith(expect.objectContaining({
        company_name: 'Test Company',
        legal_business_name: 'Test Legal Name',
        email: 'test@example.com'
      }));
    });
    
    // Check success message appears
    await waitFor(() => {
      expect(screen.getByText(/customer created successfully/i)).toBeInTheDocument();
    });
  });

  it('loads customer data in edit mode', async () => {
    // Mock route params to simulate edit mode
    vi.mocked(useParams).mockReturnValue({ id: '123' });
    
    const { customerApi } = await import('../../../utils/apiClient');
    
    render(<CustomerForm />);
    
    await waitFor(() => {
      expect(customerApi.get).toHaveBeenCalledTimes(1);
      expect(customerApi.get).toHaveBeenCalledWith('123');
    });
    
    // Check form is populated with customer data
    await waitFor(() => {
      expect(screen.getByLabelText(/company name/i)).toHaveValue('Test Company');
      expect(screen.getByLabelText(/legal business name/i)).toHaveValue('Test Legal Name');
      expect(screen.getByLabelText(/email/i)).toHaveValue('test@example.com');
      expect(screen.getByLabelText(/phone/i)).toHaveValue('123-456-7890');
    });
    
    // Check that we're in edit mode
    expect(screen.getByText('Edit Customer')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /update customer/i })).toBeInTheDocument();
  });

  it('handles API errors on form submission', async () => {
    const { customerApi, handleApiError } = await import('../../../utils/apiClient');
    
    // Mock API error
    customerApi.create.mockRejectedValueOnce(new Error('API Error'));
    
    render(<CustomerForm />);
    
    // Fill required fields
    userEvent.type(screen.getByLabelText(/company name/i), 'Test Company');
    userEvent.type(screen.getByLabelText(/legal business name/i), 'Test Legal Name');
    userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create customer/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(customerApi.create).toHaveBeenCalledTimes(1);
      expect(handleApiError).toHaveBeenCalledTimes(1);
    });
    
    // Check error message appears
    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('disables form submission during loading', async () => {
    render(<CustomerForm />);
    
    // Fill required fields
    userEvent.type(screen.getByLabelText(/company name/i), 'Test Company');
    userEvent.type(screen.getByLabelText(/legal business name/i), 'Test Legal Name');
    userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create customer/i });
    fireEvent.click(submitButton);
    
    // Check button is disabled during submission
    expect(submitButton).toBeDisabled();
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(screen.getByText(/customer created successfully/i)).toBeInTheDocument();
    });
  });
});