# Writing Effective Tests for LedgerLink

This guide provides detailed instructions and best practices for writing effective tests in the LedgerLink project. It complements the main [TESTING_GUIDE.md](TESTING_GUIDE.md) by focusing on how to write high-quality tests.

## Table of Contents

1. [General Testing Principles](#general-testing-principles)
2. [Backend (Django) Test Patterns](#backend-django-test-patterns)
3. [Frontend (React) Test Patterns](#frontend-react-test-patterns)
4. [E2E (Cypress) Test Patterns](#e2e-cypress-test-patterns)
5. [Contract Test Patterns](#contract-test-patterns)
6. [Test Naming and Organization](#test-naming-and-organization)
7. [Testing Anti-Patterns to Avoid](#testing-anti-patterns-to-avoid)

## General Testing Principles

### The FIRST Principles

All tests in LedgerLink should follow the FIRST principles:

- **Fast**: Tests should run quickly to provide rapid feedback
- **Isolated**: Tests should not depend on each other or external systems
- **Repeatable**: Tests should produce the same results each time they run
- **Self-validating**: Tests should automatically determine if they pass or fail
- **Timely**: Tests should be written at the same time as (or before) the code

### Test Structure

Follow the "Arrange-Act-Assert" pattern:

1. **Arrange**: Set up test data and preconditions
2. **Act**: Execute the code being tested
3. **Assert**: Verify the results are as expected

```python
# Example in Python
def test_something():
    # Arrange
    user = UserFactory(is_active=True)
    
    # Act
    result = is_user_allowed_access(user)
    
    # Assert
    assert result is True
```

```javascript
// Example in JavaScript
it('allows active users access', () => {
    // Arrange
    const user = { id: 1, isActive: true };
    
    // Act
    const result = isUserAllowedAccess(user);
    
    // Assert
    expect(result).toBe(true);
});
```

### Test Coverage Goals

Different parts of the application should have different coverage goals:

- **Critical business logic**: Aim for 90-100% coverage
- **Data models**: 80-90% coverage
- **View/UI components**: 70-80% coverage
- **Configuration and setup code**: 50-70% coverage

## Backend (Django) Test Patterns

### Model Testing

When testing Django models:

1. **Test creation and validation**
   ```python
   def test_customer_creation(test_user):
       customer = CustomerFactory(
           company_name="Test Company",
           created_by=test_user
       )
       assert customer.pk is not None
       assert customer.company_name == "Test Company"
   ```

2. **Test model methods**
   ```python
   def test_customer_get_full_address(test_customer):
       test_customer.address = "123 Main St"
       test_customer.city = "Anytown"
       test_customer.state = "CA"
       test_customer.postal_code = "12345"
       
       full_address = test_customer.get_full_address()
       assert full_address == "123 Main St, Anytown, CA 12345"
   ```

3. **Test constraints and validation**
   ```python
   def test_customer_unique_constraint(test_user):
       CustomerFactory(email="test@example.com", created_by=test_user)
       
       with pytest.raises(IntegrityError):
           CustomerFactory(email="test@example.com", created_by=test_user)
   ```

### API Testing

When testing REST API endpoints:

1. **Test CRUD operations**
   ```python
   def test_create_customer(self):
       data = {
           'company_name': 'New Company',
           'email': 'new@example.com',
       }
       
       response = self.get_json_response(
           self.list_url, 
           method='post', 
           data=data, 
           status_code=201
       )
       
       assert response['company_name'] == data['company_name']
       assert Customer.objects.filter(company_name=data['company_name']).exists()
   ```

2. **Test authentication and permissions**
   ```python
   def test_unauthenticated_access_denied(self):
       self.client.force_authenticate(user=None)
       
       self.get_json_response(
           self.list_url,
           status_code=401
       )
   ```

3. **Test filtering and pagination**
   ```python
   def test_customer_filtering(self):
       response = self.get_json_response(
           f"{self.list_url}?state=CA",
       )
       
       assert all(c['state'] == 'CA' for c in response['results'])
   ```

### Testing Views and Templates

When testing traditional Django views and templates:

1. **Test rendering and context**
   ```python
   def test_dashboard_view(self):
       response = self.get_response(self.dashboard_url)
       
       assert response.status_code == 200
       assert 'stats' in response.context
       assert 'recent_orders' in response.context
   ```

2. **Test form submission**
   ```python
   def test_customer_create_form_submission(self):
       data = {
           'company_name': 'Test Company',
           'email': 'test@example.com',
       }
       
       response = self.get_response(
           self.create_url, 
           method='post', 
           data=data, 
           follow=True
       )
       
       assert 'Customer created successfully' in str(response.content)
       assert Customer.objects.filter(company_name=data['company_name']).exists()
   ```

### Testing Business Logic

When testing services, utilities, and business logic:

1. **Test each component in isolation**
   ```python
   def test_order_total_calculation(self):
       order_items = [
           {'product_id': 1, 'quantity': 2, 'price': Decimal('10.00')},
           {'product_id': 2, 'quantity': 1, 'price': Decimal('5.00')}
       ]
       
       total = calculate_order_total(order_items)
       assert total == Decimal('25.00')
   ```

2. **Use mocks for dependencies**
   ```python
   @patch('myapp.services.external_api.get_tax_rate')
   def test_tax_calculation(self, mock_get_tax_rate):
       mock_get_tax_rate.return_value = Decimal('0.07')
       
       tax = calculate_tax(Decimal('100.00'), 'CA')
       assert tax == Decimal('7.00')
   ```

## Frontend (React) Test Patterns

### Component Testing

When testing React components:

1. **Test rendering and props**
   ```javascript
   it('renders customer information correctly', () => {
       const customer = {
           id: 1,
           name: 'Test Company',
           email: 'test@example.com'
       };
       
       render(<CustomerCard customer={customer} />);
       
       expect(screen.getByText('Test Company')).toBeInTheDocument();
       expect(screen.getByText('test@example.com')).toBeInTheDocument();
   });
   ```

2. **Test user interactions**
   ```javascript
   it('calls onDelete when delete button is clicked', async () => {
       const onDelete = vi.fn();
       const user = userEvent.setup();
       
       render(<CustomerCard customer={mockCustomer} onDelete={onDelete} />);
       
       await user.click(screen.getByRole('button', { name: /delete/i }));
       expect(onDelete).toHaveBeenCalledWith(mockCustomer.id);
   });
   ```

3. **Test conditional rendering**
   ```javascript
   it('shows loading indicator when isLoading is true', () => {
       render(<CustomerList isLoading={true} customers={[]} />);
       
       expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
       expect(screen.queryByRole('table')).not.toBeInTheDocument();
   });
   
   it('shows customers when loaded', () => {
       render(<CustomerList isLoading={false} customers={mockCustomers} />);
       
       expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
       expect(screen.getByRole('table')).toBeInTheDocument();
   });
   ```

### Hook Testing

When testing custom hooks:

1. **Test initial state**
   ```javascript
   it('initializes with default state', () => {
       const { result } = renderHook(() => useCustomerData());
       
       expect(result.current.customers).toEqual([]);
       expect(result.current.loading).toBe(false);
       expect(result.current.error).toBe(null);
   });
   ```

2. **Test state updates**
   ```javascript
   it('updates loading state when fetching', () => {
       const { result } = renderHook(() => useCustomerData());
       
       act(() => {
           result.current.fetchCustomers();
       });
       
       expect(result.current.loading).toBe(true);
   });
   ```

3. **Test async behavior**
   ```javascript
   it('fetches and updates customer data', async () => {
       const { result } = renderHook(() => useCustomerData());
       
       act(() => {
           result.current.fetchCustomers();
       });
       
       await waitFor(() => {
           expect(result.current.loading).toBe(false);
           expect(result.current.customers.length).toBeGreaterThan(0);
       });
   });
   ```

### Form Testing

When testing forms:

1. **Test form validation**
   ```javascript
   it('validates required fields', async () => {
       render(<CustomerForm />);
       const user = userEvent.setup();
       
       // Submit without filling required fields
       await user.click(screen.getByRole('button', { name: /submit/i }));
       
       expect(screen.getByText(/name is required/i)).toBeInTheDocument();
       expect(screen.getByText(/email is required/i)).toBeInTheDocument();
   });
   ```

2. **Test form submission**
   ```javascript
   it('submits form with valid data', async () => {
       const onSubmit = vi.fn();
       render(<CustomerForm onSubmit={onSubmit} />);
       const user = userEvent.setup();
       
       await user.type(screen.getByLabelText(/name/i), 'Test Company');
       await user.type(screen.getByLabelText(/email/i), 'test@example.com');
       await user.click(screen.getByRole('button', { name: /submit/i }));
       
       expect(onSubmit).toHaveBeenCalledWith({
           name: 'Test Company',
           email: 'test@example.com'
       });
   });
   ```

## E2E (Cypress) Test Patterns

### User Flow Testing

When testing complete user flows:

1. **Test critical paths**
   ```javascript
   it('completes the order checkout process', () => {
       // Login first
       cy.login('customer@example.com', 'password');
       
       // Visit products page
       cy.visit('/products');
       
       // Add items to cart
       cy.contains('Product A').click();
       cy.get('[data-testid=add-to-cart]').click();
       cy.contains('Added to cart').should('be.visible');
       
       // Go to cart and checkout
       cy.get('[data-testid=cart-icon]').click();
       cy.get('[data-testid=checkout-button]').click();
       
       // Fill shipping info
       cy.get('input[name=address]').type('123 Test St');
       cy.get('input[name=city]').type('Test City');
       cy.get('[data-testid=continue-button]').click();
       
       // Complete payment
       cy.get('[data-testid=payment-method-credit]').click();
       cy.get('input[name=card-number]').type('4242424242424242');
       cy.get('input[name=expiry]').type('1230');
       cy.get('input[name=cvv]').type('123');
       cy.get('[data-testid=place-order-button]').click();
       
       // Verify order confirmation
       cy.url().should('include', '/order-confirmation');
       cy.contains('Order Completed').should('be.visible');
   });
   ```

2. **Data-driven tests**
   ```javascript
   const testCases = [
       { username: 'admin', hasAccess: true },
       { username: 'regular', hasAccess: false }
   ];
   
   testCases.forEach(({ username, hasAccess }) => {
       it(`${username} ${hasAccess ? 'has' : 'does not have'} access to admin panel`, () => {
           cy.login(username, 'password');
           cy.visit('/dashboard');
           
           if (hasAccess) {
               cy.get('[data-testid=admin-panel]').should('be.visible');
           } else {
               cy.get('[data-testid=admin-panel]').should('not.exist');
           }
       });
   });
   ```

### API Interaction Testing

When testing frontend interactions with backend APIs:

1. **Test API responses**
   ```javascript
   it('shows error message when API fails', () => {
       // Intercept API call and force error
       cy.intercept('GET', '/api/customers', {
           statusCode: 500,
           body: { error: 'Server error' }
       }).as('getCustomers');
       
       cy.visit('/customers');
       
       // Wait for API call to complete
       cy.wait('@getCustomers');
       
       // Verify error message is shown
       cy.contains('Failed to load customers').should('be.visible');
   });
   ```

2. **Test loading states**
   ```javascript
   it('shows loading state while API request is in progress', () => {
       // Intercept API call with delay
       cy.intercept('GET', '/api/customers', {
           delay: 1000,
           fixture: 'customers.json'
       }).as('getCustomers');
       
       cy.visit('/customers');
       
       // Verify loading indicator is shown
       cy.get('[data-testid=loading-spinner]').should('be.visible');
       
       // Wait for API call to complete
       cy.wait('@getCustomers');
       
       // Verify loading indicator is hidden
       cy.get('[data-testid=loading-spinner]').should('not.exist');
   });
   ```

### Accessibility Testing

When testing for accessibility:

1. **Basic accessibility audits**
   ```javascript
   it('passes accessibility audit', () => {
       cy.visit('/customers');
       cy.injectAxe();
       cy.checkA11y();
   });
   ```

2. **Test keyboard navigation**
   ```javascript
   it('allows keyboard navigation through main menu', () => {
       cy.visit('/');
       cy.get('body').focus().tab(); // First tab focuses on the first menu item
       cy.focused().should('have.text', 'Dashboard');
       
       cy.focused().tab(); // Second tab focuses on the second menu item
       cy.focused().should('have.text', 'Customers');
       
       cy.focused().type('{enter}'); // Pressing enter should navigate
       cy.url().should('include', '/customers');
   });
   ```

## Contract Test Patterns

See [CONTRACT_TESTING.md](CONTRACT_TESTING.md) for detailed patterns, but here are the essentials:

1. **Define contracts from the consumer perspective**
   ```javascript
   // Example Pact consumer test
   await provider.addInteraction({
       state: 'customer exists',
       uponReceiving: 'a request for customer details',
       withRequest: {
           method: 'GET',
           path: '/api/customers/1',
       },
       willRespondWith: {
           status: 200,
           body: customerMatcher,
       },
   });
   ```

2. **Verify provider implementation**
   ```python
   # Provider state setup
   def setup_customer_exists(variables, **kwargs):
       CustomerFactory(id=1, name="Test Company")
   ```

## Test Naming and Organization

### Naming Conventions

- **Backend Tests**: `test_[feature]_[behavior].py`
- **Frontend Component Tests**: `[ComponentName].test.jsx`
- **E2E Tests**: `[feature].cy.js`

### Test Function Naming

- **Backend**: `test_[what_is_being_tested]_[expected_behavior]`
  - Example: `test_customer_creation_with_invalid_email_raises_error`

- **Frontend**: `it('[describes what the test is checking]', ...)`
  - Example: `it('validates email format when typing', ...)`

### Test Organization

Group related tests together:

```python
# Backend example
class TestCustomerModel:
    def test_creation(self):
        pass
        
    def test_validation(self):
        pass
    
    class TestAddressMethods:
        def test_get_full_address(self):
            pass
```

```javascript
// Frontend example
describe('CustomerForm', () => {
    describe('Rendering', () => {
        it('renders in create mode', () => {});
        it('renders in edit mode', () => {});
    });
    
    describe('Validation', () => {
        it('validates required fields', () => {});
        it('validates email format', () => {});
    });
    
    describe('Submission', () => {
        it('submits valid data', () => {});
        it('shows errors on failed submission', () => {});
    });
});
```

## Testing Anti-Patterns to Avoid

### Don't Test Implementation Details

❌ **Bad**: Tests that rely on implementation details
```javascript
// Testing implementation details (bad)
it('increments counter internally', () => {
    const { result } = renderHook(() => useCounter());
    act(() => {
        result.current.increment();
    });
    expect(result.current.count).toBe(1); // This tests the internal state
});
```

✅ **Good**: Tests that verify behavior
```javascript
// Testing behavior (good)
it('shows incremented value when increment button is clicked', () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });
    fireEvent.click(button);
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

### Avoid Test Duplication

❌ **Bad**: Duplicating tests across different layers
```python
# Testing the same thing in multiple places
def test_api_creates_customer(self):
    # This duplicates model validation tests
    data = {'company_name': '', 'email': 'invalid'}
    self.client.post('/api/customers/', data)
    # Assertions...
```

✅ **Good**: Test different aspects at each layer
```python
# Model layer: test validation rules
def test_customer_validation(self):
    customer = Customer(company_name='', email='invalid')
    with pytest.raises(ValidationError):
        customer.full_clean()

# API layer: test HTTP responses for invalid data
def test_api_returns_400_for_invalid_data(self):
    data = {'company_name': '', 'email': 'invalid'}
    response = self.client.post('/api/customers/', data)
    assert response.status_code == 400
```

### Avoid Brittle Tests

❌ **Bad**: Tests that break with minor changes
```javascript
// Brittle test with exact HTML structure dependence
it('renders customer card', () => {
    render(<CustomerCard customer={mockCustomer} />);
    expect(screen.getByTestId('customer-card').firstChild.textContent).toBe('Test Company');
});
```

✅ **Good**: Tests that are resilient to minor changes
```javascript
// Resilient test focusing on important content
it('renders customer card with name', () => {
    render(<CustomerCard customer={mockCustomer} />);
    expect(screen.getByText('Test Company')).toBeInTheDocument();
});
```

### Don't Use Excessive Mocks

❌ **Bad**: Over-mocking
```javascript
// Excessive mocking
it('fetches data', async () => {
    // Mocking every single dependency
    const apiMock = vi.fn();
    const loggerMock = vi.fn();
    const cacheMock = vi.fn();
    const formatterMock = vi.fn();
    // ... more mocks
    
    // Using all the mocks
    const result = await fetchData(apiMock, loggerMock, cacheMock, formatterMock);
    expect(result).toBe(expectedData);
});
```

✅ **Good**: Mock only what's necessary
```javascript
// Focused mocking
it('fetches data', async () => {
    // Just mock the external API call
    vi.mock('../api', () => ({
        fetchFromApi: vi.fn().mockResolvedValue(mockApiResponse)
    }));
    
    const result = await dataService.fetchData();
    expect(result).toEqual(expectedData);
});
```

### Don't Skip Error Cases

❌ **Bad**: Only testing the happy path
```javascript
// Only testing successful case
it('submits the form', async () => {
    // Only testing when everything works
    render(<Form />);
    // Fill form and submit...
    expect(screen.getByText('Success')).toBeInTheDocument();
});
```

✅ **Good**: Test both success and error paths
```javascript
// Testing both success and error paths
it('submits the form successfully', async () => {
    // Setup for success case
    // Test success case
});

it('shows validation errors when form has invalid data', async () => {
    // Test validation errors
});

it('handles API errors during submission', async () => {
    // Mock API to return error
    // Test error handling
});
```

By following these patterns and avoiding the anti-patterns, you'll write tests that are maintainable, reliable, and valuable for the LedgerLink project.