/**
 * End-to-end tests for customer management functionality
 */
describe('Customer Management', () => {
  beforeEach(() => {
    // Log in before each test
    cy.login();
    
    // Intercept API calls to customers
    cy.intercept('GET', '/api/v1/customers/**').as('getCustomers');
    cy.intercept('POST', '/api/v1/customers/').as('createCustomer');
    cy.intercept('PUT', '/api/v1/customers/*').as('updateCustomer');
    cy.intercept('DELETE', '/api/v1/customers/*').as('deleteCustomer');
  });
  
  it('displays the customer list page', () => {
    // Go to the customers page
    cy.visit('/customers');
    
    // Wait for API response
    cy.wait('@getCustomers');
    
    // Page should have the correct title
    cy.contains('h1', 'Customers').should('be.visible');
    
    // Customer table should be visible
    cy.get('table').should('be.visible');
    
    // Table should have headers
    cy.contains('th', 'Company Name').should('be.visible');
    cy.contains('th', 'Contact').should('be.visible');
    cy.contains('th', 'Email').should('be.visible');
  });
  
  it('allows filtering and searching customers', () => {
    // Go to the customers page
    cy.visit('/customers');
    
    // Wait for API response
    cy.wait('@getCustomers');
    
    // Use the search box
    cy.get('input[placeholder*="Search"]').type('Acme');
    cy.get('button').contains('Search').click();
    
    // Wait for filtered results
    cy.wait('@getCustomers');
    
    // Results should be filtered
    cy.contains('td', 'Acme').should('be.visible');
    
    // Reset search
    cy.get('input[placeholder*="Search"]').clear();
    cy.get('button').contains('Search').click();
    cy.wait('@getCustomers');
    
    // Filter by active status
    cy.get('select').select('Active');
    cy.wait('@getCustomers');
    
    // Should only show active customers
    cy.contains('td', 'Inactive').should('not.exist');
  });
  
  it('can navigate to add customer form', () => {
    // Go to the customers page
    cy.visit('/customers');
    
    // Wait for API response
    cy.wait('@getCustomers');
    
    // Click the add button
    cy.contains('button', 'Add Customer').click();
    
    // Should navigate to customer form
    cy.url().should('include', '/customers/new');
    
    // Form should be visible
    cy.contains('h1', 'Create Customer').should('be.visible');
    cy.get('form').should('be.visible');
  });
  
  it('can create a new customer', () => {
    // Go to the customer create page
    cy.visit('/customers/new');
    
    // Fill out the form
    const timestamp = new Date().getTime();
    const companyName = `Test Company ${timestamp}`;
    
    cy.get('input[name="company_name"]').type(companyName);
    cy.get('input[name="contact_name"]').type('Test Contact');
    cy.get('input[name="email"]').type(`test${timestamp}@example.com`);
    cy.get('input[name="phone"]').type('555-1234');
    cy.get('input[name="address"]').type('123 Test St');
    cy.get('input[name="city"]').type('Test City');
    cy.get('input[name="state"]').type('TS');
    cy.get('input[name="zip_code"]').type('12345');
    cy.get('input[name="country"]').type('US');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for API response
    cy.wait('@createCustomer');
    
    // Should navigate back to customers list
    cy.url().should('include', '/customers');
    
    // Should show success message
    cy.contains('Customer created successfully').should('be.visible');
    
    // Wait for customers to load
    cy.wait('@getCustomers');
    
    // New customer should be in the list
    cy.contains('td', companyName).should('be.visible');
  });
  
  it('can edit an existing customer', () => {
    // Go to the customers page
    cy.visit('/customers');
    
    // Wait for API response
    cy.wait('@getCustomers');
    
    // Click the edit button for the first customer
    cy.get('button[aria-label="Edit"]').first().click();
    
    // Should navigate to edit form
    cy.url().should('include', '/customers/');
    cy.url().should('include', '/edit');
    
    // Wait for customer data to load
    cy.wait('@getCustomers');
    
    // Update the company name
    const timestamp = new Date().getTime();
    const updatedName = `Updated Company ${timestamp}`;
    
    cy.get('input[name="company_name"]').clear().type(updatedName);
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for API response
    cy.wait('@updateCustomer');
    
    // Should navigate back to customers list
    cy.url().should('include', '/customers');
    cy.url().should('not.include', '/edit');
    
    // Should show success message
    cy.contains('Customer updated successfully').should('be.visible');
    
    // Wait for customers to load
    cy.wait('@getCustomers');
    
    // Updated customer should be in the list
    cy.contains('td', updatedName).should('be.visible');
  });
  
  it('can delete a customer', () => {
    // Go to the customers page
    cy.visit('/customers');
    
    // Wait for API response
    cy.wait('@getCustomers');
    
    // Store the total number of customers before deletion
    cy.get('table tbody tr').then($rows => {
      const initialCount = $rows.length;
      
      // Click the delete button for the first customer
      cy.get('button[aria-label="Delete"]').first().click();
      
      // Confirm the deletion in the dialog
      cy.contains('button', 'Confirm').click();
      
      // Wait for API response
      cy.wait('@deleteCustomer');
      
      // Should show success message
      cy.contains('Customer deleted successfully').should('be.visible');
      
      // Wait for updated list
      cy.wait('@getCustomers');
      
      // There should be one fewer customer
      cy.get('table tbody tr').should('have.length', initialCount - 1);
    });
  });
  
  it('validates form inputs when creating a customer', () => {
    // Go to the customer create page
    cy.visit('/customers/new');
    
    // Submit the form without filling required fields
    cy.get('button[type="submit"]').click();
    
    // Should show validation errors
    cy.contains('Company name is required').should('be.visible');
    
    // Fill company name but with invalid email
    cy.get('input[name="company_name"]').type('Test Company');
    cy.get('input[name="email"]').type('invalid-email');
    
    // Submit again
    cy.get('button[type="submit"]').click();
    
    // Should show email validation error
    cy.contains('Invalid email format').should('be.visible');
    
    // Form should not have been submitted
    cy.get('@createCustomer.all').should('have.length', 0);
  });
});