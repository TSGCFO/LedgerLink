/**
 * End-to-end tests for the Orders functionality
 */
describe('Orders Management', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Clear any cached data
    cy.clearLocalStorage('orderFilters');
  });
  
  it('displays the orders list', () => {
    // Visit the orders page
    cy.visit('/orders');
    
    // Page should load with title
    cy.get('h1').should('contain', 'Orders');
    
    // Table should be visible with headers
    cy.get('[data-testid="orders-table"]').should('be.visible');
    cy.contains('Order Number').should('be.visible');
    cy.contains('Customer').should('be.visible');
    cy.contains('Date').should('be.visible');
    cy.contains('Status').should('be.visible');
    
    // At least one order should be in the table (from test fixtures)
    cy.contains('TEST-ORDER-001').should('be.visible');
  });
  
  it('filters orders by status', () => {
    cy.visit('/orders');
    
    // Load the initial orders
    cy.get('[data-testid="orders-table"]').should('be.visible');
    
    // Select the pending status filter
    cy.get('[data-testid="status-filter"]').click();
    cy.get('li[data-value="pending"]').click();
    
    // Verify the filter works
    cy.get('[data-testid="orders-table"]').contains('pending').should('be.visible');
    cy.get('[data-testid="orders-table"]').contains('completed').should('not.exist');
  });
  
  it('searches for orders by order number', () => {
    cy.visit('/orders');
    
    // Type in the search box
    cy.get('[data-testid="search-field"]').type('TEST-ORDER-001');
    cy.get('[data-testid="search-button"]').click();
    
    // Should find our test order
    cy.contains('TEST-ORDER-001').should('be.visible');
    
    // Clear search and try a non-existent order
    cy.get('[data-testid="search-field"]').clear().type('NON-EXISTENT');
    cy.get('[data-testid="search-button"]').click();
    
    // Should show no results message
    cy.contains('No matching records found').should('be.visible');
  });
  
  it('navigates to order creation form', () => {
    cy.visit('/orders');
    
    // Click the add order button
    cy.get('[data-testid="add-order-button"]').click();
    
    // Should navigate to the order form
    cy.url().should('include', '/orders/new');
    
    // Form should be visible with required fields
    cy.get('form').should('be.visible');
    cy.get('[data-testid="customer-field"]').should('be.visible');
    cy.get('[data-testid="order-number-field"]').should('be.visible');
    cy.get('[data-testid="shipping-address-field"]').should('be.visible');
  });
  
  it('creates a new order', () => {
    cy.visit('/orders/new');
    
    // Fill out the form
    const orderNumber = `TEST-ORDER-${Date.now()}`;
    
    // Select customer from dropdown
    cy.get('[data-testid="customer-field"]').click();
    cy.get('li').contains('Test Company').click();
    
    // Fill other required fields
    cy.get('[data-testid="order-number-field"]').type(orderNumber);
    cy.get('[data-testid="shipping-address-field"]').type('456 Test Avenue, Testtown, TX 54321');
    cy.get('[data-testid="shipping-method-field"]').type('Express');
    
    // Select a shipping priority
    cy.get('[data-testid="priority-field"]').click();
    cy.get('li[data-value="high"]').click();
    
    // Add notes
    cy.get('[data-testid="notes-field"]').type('This is a test order created by Cypress');
    
    // Submit the form
    cy.get('[data-testid="submit-button"]').click();
    
    // Should redirect to order list
    cy.url().should('include', '/orders');
    
    // New order should be in the list
    cy.contains(orderNumber).should('be.visible');
  });
  
  it('views order details', () => {
    cy.visit('/orders');
    
    // Click on an order to view details
    cy.contains('TEST-ORDER-001').click();
    
    // Should navigate to order details
    cy.url().should('include', '/orders/');
    
    // Details page should show order information
    cy.get('[data-testid="order-details"]').should('be.visible');
    cy.contains('Order: TEST-ORDER-001').should('be.visible');
    cy.contains('Test Company').should('be.visible');
    cy.contains('123 Test Street, Testville, TS 12345').should('be.visible');
    cy.contains('Status: pending').should('be.visible');
  });
  
  it('updates order status', () => {
    // Find the existing test order
    cy.visit('/orders');
    cy.contains('TEST-ORDER-001').click();
    
    // Update status to in progress
    cy.get('[data-testid="status-select"]').click();
    cy.get('li[data-value="in_progress"]').click();
    cy.get('[data-testid="update-status-button"]').click();
    
    // Verify status updated
    cy.contains('Status: in_progress').should('be.visible');
    
    // Check toast message
    cy.contains('Order status updated successfully').should('be.visible');
  });
  
  it('handles form validation', () => {
    cy.visit('/orders/new');
    
    // Try to submit the form without filling required fields
    cy.get('[data-testid="submit-button"]').click();
    
    // Should display validation errors
    cy.contains('Customer is required').should('be.visible');
    cy.contains('Order number is required').should('be.visible');
    cy.contains('Shipping address is required').should('be.visible');
    
    // Form should not submit
    cy.url().should('include', '/orders/new');
  });
});