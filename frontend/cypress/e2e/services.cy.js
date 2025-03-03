/**
 * End-to-end tests for the Services functionality
 */
describe('Services Management', () => {
  beforeEach(() => {
    // Log in before each test
    cy.login();
    
    // Intercept API calls
    cy.intercept('GET', '/api/v1/services/**').as('getServices');
    cy.intercept('POST', '/api/v1/services/').as('createService');
    cy.intercept('PUT', '/api/v1/services/*').as('updateService');
    cy.intercept('DELETE', '/api/v1/services/*').as('deleteService');
  });
  
  it('displays the services list page', () => {
    // Visit the services page
    cy.visit('/services');
    
    // Wait for the API call to complete
    cy.wait('@getServices');
    
    // Page should have the correct title
    cy.contains('h1', 'Services').should('be.visible');
    
    // Service table should be visible
    cy.get('table').should('be.visible');
    
    // Should have specific columns
    cy.contains('th', 'Service Name').should('be.visible');
    cy.contains('th', 'Description').should('be.visible');
    cy.contains('th', 'Base Rate').should('be.visible');
    cy.contains('th', 'Charge Type').should('be.visible');
  });
  
  it('navigates to add service form', () => {
    // Go to the services page
    cy.visit('/services');
    
    // Wait for the API call to complete
    cy.wait('@getServices');
    
    // Click the add button
    cy.contains('button', 'Add Service').click();
    
    // Should navigate to service form
    cy.url().should('include', '/services/new');
    
    // Form should be visible with expected fields
    cy.contains('h1', 'Create Service').should('be.visible');
    cy.get('form').should('be.visible');
    cy.get('input[name="name"]').should('be.visible');
    cy.get('textarea[name="description"]').should('be.visible');
    cy.get('input[name="base_rate"]').should('be.visible');
    cy.get('select[name="charge_type"]').should('be.visible');
  });
  
  it('creates a new service', () => {
    // Go to the service create page
    cy.visit('/services/new');
    
    // Fill out the form
    const timestamp = new Date().getTime();
    const serviceName = `Test Service ${timestamp}`;
    
    cy.get('input[name="name"]').type(serviceName);
    cy.get('textarea[name="description"]').type('This is a test service created through Cypress');
    cy.get('input[name="base_rate"]').type('25.50');
    cy.get('select[name="charge_type"]').select('Flat Rate');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for the API call to complete
    cy.wait('@createService');
    
    // Should navigate back to services list
    cy.url().should('include', '/services');
    cy.url().should('not.include', '/new');
    
    // Should show success message
    cy.contains('Service created successfully').should('be.visible');
    
    // New service should be in the list
    cy.wait('@getServices');
    cy.contains('td', serviceName).should('be.visible');
  });
  
  it('edits an existing service', () => {
    // Go to the services page
    cy.visit('/services');
    
    // Wait for the API call to complete
    cy.wait('@getServices');
    
    // Click the edit button on the first service
    cy.get('button[aria-label="Edit"]').first().click();
    
    // Should navigate to edit form
    cy.url().should('include', '/services/');
    cy.url().should('include', '/edit');
    
    // Update the service name
    const timestamp = new Date().getTime();
    const updatedName = `Updated Service ${timestamp}`;
    
    cy.get('input[name="name"]').clear().type(updatedName);
    cy.get('input[name="base_rate"]').clear().type('35.75');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for the API call to complete
    cy.wait('@updateService');
    
    // Should navigate back to services list
    cy.url().should('include', '/services');
    cy.url().should('not.include', '/edit');
    
    // Should show success message
    cy.contains('Service updated successfully').should('be.visible');
    
    // Wait for updated list
    cy.wait('@getServices');
    
    // Updated service should be in the list
    cy.contains('td', updatedName).should('be.visible');
    cy.contains('td', '$35.75').should('be.visible');
  });
  
  it('deletes a service', () => {
    // Go to the services page
    cy.visit('/services');
    
    // Wait for the API call to complete
    cy.wait('@getServices');
    
    // Store the total number of services before deletion
    cy.get('table tbody tr').then($rows => {
      const initialCount = $rows.length;
      
      // Click the delete button on the first service
      cy.get('button[aria-label="Delete"]').first().click();
      
      // Confirm the deletion in the dialog
      cy.contains('button', 'Confirm').click();
      
      // Wait for the API call to complete
      cy.wait('@deleteService');
      
      // Should show success message
      cy.contains('Service deleted successfully').should('be.visible');
      
      // Wait for updated list
      cy.wait('@getServices');
      
      // There should be one fewer service
      cy.get('table tbody tr').should('have.length', initialCount - 1);
    });
  });
  
  it('validates form inputs when creating a service', () => {
    // Go to the service create page
    cy.visit('/services/new');
    
    // Try to submit the form without filling required fields
    cy.get('button[type="submit"]').click();
    
    // Should show validation errors
    cy.contains('Service name is required').should('be.visible');
    cy.contains('Base rate is required').should('be.visible');
    
    // Fill name but with invalid base rate
    cy.get('input[name="name"]').type('Test Service');
    cy.get('input[name="base_rate"]').type('-10');
    
    // Submit again
    cy.get('button[type="submit"]').click();
    
    // Should show validation error for negative rate
    cy.contains('Base rate must be greater than 0').should('be.visible');
    
    // Service should not have been created
    cy.get('@createService.all').should('have.length', 0);
  });
});