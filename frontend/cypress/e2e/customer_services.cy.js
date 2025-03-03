/**
 * End-to-end tests for the Customer Services functionality
 */
describe('Customer Services Management', () => {
  beforeEach(() => {
    // Log in before each test
    cy.login();
    
    // Intercept API calls
    cy.intercept('GET', '/api/v1/customer-services/**').as('getCustomerServices');
    cy.intercept('POST', '/api/v1/customer-services/').as('createCustomerService');
    cy.intercept('PUT', '/api/v1/customer-services/*').as('updateCustomerService');
    cy.intercept('DELETE', '/api/v1/customer-services/*').as('deleteCustomerService');
    
    // Intercept related API calls
    cy.intercept('GET', '/api/v1/customers/**').as('getCustomers');
    cy.intercept('GET', '/api/v1/services/**').as('getServices');
  });
  
  it('displays the customer services list page', () => {
    // Visit the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Page should have the correct title
    cy.contains('h1', 'Customer Services').should('be.visible');
    
    // Customer service table should be visible
    cy.get('table').should('be.visible');
    
    // Should have specific columns
    cy.contains('th', 'Customer').should('be.visible');
    cy.contains('th', 'Service').should('be.visible');
    cy.contains('th', 'Status').should('be.visible');
    cy.contains('th', 'Created').should('be.visible');
  });
  
  it('navigates to add customer service form', () => {
    // Go to the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Click the add button
    cy.contains('button', 'Add Customer Service').click();
    
    // Should navigate to customer service form
    cy.url().should('include', '/customer-services/new');
    
    // Wait for related data to load
    cy.wait('@getCustomers');
    cy.wait('@getServices');
    
    // Form should be visible with expected fields
    cy.contains('h1', 'Create Customer Service').should('be.visible');
    cy.get('form').should('be.visible');
    cy.contains('label', 'Customer').should('be.visible');
    cy.contains('label', 'Service').should('be.visible');
    cy.contains('label', 'Active').should('be.visible');
  });
  
  it('creates a new customer service', () => {
    // Go to the customer service create page
    cy.visit('/customer-services/new');
    
    // Wait for related data to load
    cy.wait('@getCustomers');
    cy.wait('@getServices');
    
    // Select a customer
    cy.get('[data-testid="customer-select"]').click();
    cy.contains('li', 'Test Company').click();
    
    // Select a service
    cy.get('[data-testid="service-select"]').click();
    cy.contains('li', 'Standard Shipping').click();
    
    // Add notes
    cy.get('textarea[name="notes"]').type('This is a test customer service created through Cypress');
    
    // Leave active checkbox checked (default)
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for the API call to complete
    cy.wait('@createCustomerService');
    
    // Should navigate back to customer services list
    cy.url().should('include', '/customer-services');
    cy.url().should('not.include', '/new');
    
    // Should show success message
    cy.contains('Customer service created successfully').should('be.visible');
    
    // Wait for list to refresh
    cy.wait('@getCustomerServices');
    
    // New customer service should be in the list
    cy.contains('td', 'Test Company').should('be.visible');
    cy.contains('td', 'Standard Shipping').should('be.visible');
  });
  
  it('edits an existing customer service', () => {
    // Go to the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Click the edit button on the first customer service
    cy.get('button[aria-label="Edit"]').first().click();
    
    // Should navigate to edit form
    cy.url().should('include', '/customer-services/');
    cy.url().should('include', '/edit');
    
    // Wait for related data to load
    cy.wait('@getCustomers');
    cy.wait('@getServices');
    
    // Update notes
    cy.get('textarea[name="notes"]').clear().type('Updated notes from Cypress test');
    
    // Toggle active status
    cy.get('input[name="is_active"]').click();
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for the API call to complete
    cy.wait('@updateCustomerService');
    
    // Should navigate back to customer services list
    cy.url().should('include', '/customer-services');
    cy.url().should('not.include', '/edit');
    
    // Should show success message
    cy.contains('Customer service updated successfully').should('be.visible');
    
    // Wait for list to refresh
    cy.wait('@getCustomerServices');
    
    // Status should be updated (inactive)
    cy.contains('td', 'Inactive').should('be.visible');
  });
  
  it('deletes a customer service', () => {
    // Go to the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Store the total number of customer services before deletion
    cy.get('table tbody tr').then($rows => {
      const initialCount = $rows.length;
      
      // Click the delete button on the first customer service
      cy.get('button[aria-label="Delete"]').first().click();
      
      // Confirm the deletion in the dialog
      cy.contains('button', 'Confirm').click();
      
      // Wait for the API call to complete
      cy.wait('@deleteCustomerService');
      
      // Should show success message
      cy.contains('Customer service deleted successfully').should('be.visible');
      
      // Wait for list to refresh
      cy.wait('@getCustomerServices');
      
      // There should be one fewer customer service
      cy.get('table tbody tr').should('have.length', initialCount - 1);
    });
  });
  
  it('validates form inputs when creating a customer service', () => {
    // Go to the customer service create page
    cy.visit('/customer-services/new');
    
    // Wait for related data to load
    cy.wait('@getCustomers');
    cy.wait('@getServices');
    
    // Try to submit the form without filling required fields
    cy.get('button[type="submit"]').click();
    
    // Should show validation errors
    cy.contains('Customer is required').should('be.visible');
    cy.contains('Service is required').should('be.visible');
    
    // Customer service should not have been created
    cy.get('@createCustomerService.all').should('have.length', 0);
  });
  
  it('displays associated rules when viewing a customer service', () => {
    // Go to the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Click the view button on the first customer service
    cy.get('button[aria-label="View"]').first().click();
    
    // Should navigate to detail view
    cy.url().should('include', '/customer-services/');
    cy.url().should('include', '/view');
    
    // Wait for details to load
    cy.wait('@getCustomerServices');
    
    // Should see customer service details
    cy.contains('Customer Service Details').should('be.visible');
    cy.contains('Associated Rules').should('be.visible');
    
    // Check if associated rules section is present
    cy.get('[data-testid="associated-rules"]').should('exist');
    
    // Check if there's a link to create rules for this customer service
    cy.contains('a', 'Create Rule').should('be.visible');
  });
  
  it('filters customer services by customer', () => {
    // Go to the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Select a customer in the filter dropdown
    cy.get('[data-testid="customer-filter"]').click();
    cy.contains('li', 'Test Company').click();
    
    // Wait for filtered results
    cy.wait('@getCustomerServices');
    
    // Should only show customer services for the selected customer
    cy.get('table tbody tr').each($row => {
      cy.wrap($row).contains('td', 'Test Company').should('exist');
    });
    
    // Clear filter
    cy.get('[data-testid="clear-filters"]').click();
    
    // Wait for unfiltered results
    cy.wait('@getCustomerServices');
    
    // Should show all customer services again
    cy.get('table tbody tr').should('have.length.greaterThan', 0);
  });
  
  it('filters customer services by service', () => {
    // Go to the customer services page
    cy.visit('/customer-services');
    
    // Wait for the API call to complete
    cy.wait('@getCustomerServices');
    
    // Select a service in the filter dropdown
    cy.get('[data-testid="service-filter"]').click();
    cy.contains('li', 'Standard Shipping').click();
    
    // Wait for filtered results
    cy.wait('@getCustomerServices');
    
    // Should only show customer services for the selected service
    cy.get('table tbody tr').each($row => {
      cy.wrap($row).contains('td', 'Standard Shipping').should('exist');
    });
  });
});