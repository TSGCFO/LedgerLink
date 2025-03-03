/// <reference types="cypress" />

describe('Customer Management', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Navigate to customers page
    cy.visit('/customers');
    
    // Intercept API calls
    cy.intercept('GET', '**/customers/**').as('getCustomers');
    cy.intercept('POST', '**/customers/**').as('createCustomer');
    cy.intercept('PUT', '**/customers/**').as('updateCustomer');
    cy.intercept('DELETE', '**/customers/**').as('deleteCustomer');
    
    // Wait for the customer list to load
    cy.wait('@getCustomers');
  });
  
  it('displays customer listing page correctly', () => {
    // Check page elements
    cy.get('[data-testid="customers-list"]').should('exist');
    cy.get('[data-testid="add-customer-button"]').should('exist');
    cy.get('[data-testid="customer-filter"]').should('exist');
  });
  
  it('filters customers correctly', () => {
    // Type into filter field
    cy.get('[data-testid="customer-filter"]').type('Test');
    
    // Wait for filtered results
    cy.wait('@getCustomers');
    
    // Verify only filtered results appear
    cy.get('[data-testid="customer-item"]').each(($item) => {
      cy.wrap($item).should('contain', 'Test');
    });
  });
  
  it('creates a new customer with validation', () => {
    // Click add customer button
    cy.get('[data-testid="add-customer-button"]').click();
    
    // Verify navigation to create page
    cy.url().should('include', '/customers/new');
    
    // Submit empty form to trigger validation
    cy.get('[data-testid="customer-form"]').submit();
    
    // Check validation errors
    cy.get('[data-testid="company-name-error"]').should('be.visible');
    cy.get('[data-testid="contact-email-error"]').should('be.visible');
    
    // Fill out form with valid data
    const timestamp = Date.now();
    const companyName = `Test Company ${timestamp}`;
    cy.get('[data-testid="company-name-input"]').type(companyName);
    cy.get('[data-testid="contact-name-input"]').type('John Doe');
    cy.get('[data-testid="contact-email-input"]').type(`test${timestamp}@example.com`);
    cy.get('[data-testid="contact-phone-input"]').type('555-123-4567');
    cy.get('[data-testid="address-input"]').type('123 Test St');
    cy.get('[data-testid="city-input"]').type('Test City');
    cy.get('[data-testid="state-input"]').type('TS');
    cy.get('[data-testid="postal-code-input"]').type('12345');
    cy.get('[data-testid="country-input"]').type('US');
    
    // Submit form
    cy.get('[data-testid="customer-form"]').submit();
    
    // Wait for API call
    cy.wait('@createCustomer');
    
    // Verify redirect to customer detail page
    cy.url().should('match', /\/customers\/\d+/);
    
    // Verify customer data is displayed
    cy.get('[data-testid="customer-detail"]').should('contain', companyName);
  });
  
  it('edits an existing customer', () => {
    // Click on first customer in list
    cy.get('[data-testid="customer-item"]').first().click();
    
    // Verify navigation to detail page
    cy.url().should('match', /\/customers\/\d+/);
    
    // Click edit button
    cy.get('[data-testid="edit-customer-button"]').click();
    
    // Verify navigation to edit page
    cy.url().should('include', '/edit');
    
    // Update company name
    const updatedName = `Updated Company ${Date.now()}`;
    cy.get('[data-testid="company-name-input"]').clear().type(updatedName);
    
    // Submit form
    cy.get('[data-testid="customer-form"]').submit();
    
    // Wait for API call
    cy.wait('@updateCustomer');
    
    // Verify redirect to detail page
    cy.url().should('match', /\/customers\/\d+/);
    cy.url().should('not.include', '/edit');
    
    // Verify updated data is displayed
    cy.get('[data-testid="customer-detail"]').should('contain', updatedName);
  });
  
  it('deletes a customer', () => {
    // Get count of customers before delete
    cy.get('[data-testid="customer-item"]').then($items => {
      const initialCount = $items.length;
      
      // Click on first customer in list
      cy.get('[data-testid="customer-item"]').first().click();
      
      // Click delete button
      cy.get('[data-testid="delete-customer-button"]').click();
      
      // Confirm deletion in modal
      cy.get('[data-testid="confirm-delete-button"]').click();
      
      // Wait for API call
      cy.wait('@deleteCustomer');
      
      // Verify redirect to customer list
      cy.url().should('include', '/customers');
      cy.url().should('not.match', /\/customers\/\d+/);
      
      // Verify customer count decreased
      cy.get('[data-testid="customer-item"]').should('have.length', initialCount - 1);
    });
  });
  
  it('uses the createCustomer command', () => {
    // Use custom command to create a customer
    cy.createCustomer({
      company_name: `Command Test ${Date.now()}`,
      contact_email: `command${Date.now()}@example.com`
    });
    
    // Verify creation was successful
    cy.url().should('match', /\/customers\/\d+/);
  });
});