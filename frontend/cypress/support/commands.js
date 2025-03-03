// ***********************************************
// This file can be used to create custom commands and overwrite existing ones.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
import 'cypress-axe';

// Login command for authentication
Cypress.Commands.add('login', (username = 'admin', password = 'adminpassword') => {
  // First, check if already logged in by looking for token in localStorage
  cy.window().then((window) => {
    const token = window.localStorage.getItem('auth_token');
    if (token) {
      return;
    }
    
    // Otherwise perform login, mocking the API response
    cy.visit('/login');
    
    // Mock successful login
    cy.intercept('POST', '/api/v1/auth/token/', {
      statusCode: 200,
      body: {
        access: 'test-access-token',
        refresh: 'test-refresh-token'
      }
    }).as('loginRequest');
    
    // Fill and submit form
    cy.get('#username').type(username);
    cy.get('#password').type(password);
    cy.get('button[type="submit"]').click();
    
    // Wait for the login request to complete
    cy.wait('@loginRequest');
    
    // Wait for login to complete and redirect
    cy.url().should('not.include', '/login');
  });
});

// Logout command
Cypress.Commands.add('logout', () => {
  // For testing purposes, directly manipulate localStorage instead of UI interaction
  // since we don't know the exact UI structure for logout
  cy.window().then((window) => {
    window.localStorage.removeItem('auth_token');
    window.localStorage.removeItem('refresh_token');
  });
  
  // Force reload to see the effects
  cy.reload();
  
  // Should redirect to login
  cy.url().should('include', '/login');
});

// Create a customer for testing
Cypress.Commands.add('createCustomer', (customerData = {}) => {
  const defaultData = {
    company_name: `Test Company ${Date.now()}`,
    contact_name: 'Test Contact',
    email: `test${Date.now()}@example.com`,
    phone: '555-1234',
    address: '123 Test St',
    city: 'Test City',
    state: 'TS',
    zip_code: '12345',
    country: 'US',
    is_active: true
  };
  
  const data = { ...defaultData, ...customerData };
  
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/v1/customers/`,
    body: data,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    }
  });
});

// Clean up test data
Cypress.Commands.add('cleanupTestData', () => {
  // This is a hook to clean up any test data after tests
  // Implementation depends on what data needs cleaning
  // For example, to delete all test customers:
  /*
  cy.request({
    method: 'GET',
    url: `${Cypress.env('apiUrl')}/api/v1/customers/?company_name__startswith=Test%20Company`,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`
    }
  }).then(response => {
    response.body.results.forEach(customer => {
      cy.request({
        method: 'DELETE',
        url: `${Cypress.env('apiUrl')}/api/v1/customers/${customer.id}/`,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
    });
  });
  */
});

// Accessibility testing commands
Cypress.Commands.add('checkPageA11y', (context = null, options = null) => {
  cy.injectAxe();
  cy.checkA11y(context, options);
});

// Log accessibility violations to console
Cypress.Commands.add('logA11yViolations', (context = null, options = null) => {
  cy.injectAxe();
  cy.checkA11y(context, options, violations => {
    cy.task('log', `${violations.length} accessibility violation(s) detected`);
    
    // Organize violations by impact
    const violationsByImpact = violations.reduce((acc, violation) => {
      const impact = violation.impact || 'unknown';
      if (!acc[impact]) {
        acc[impact] = [];
      }
      acc[impact].push(violation);
      return acc;
    }, {});
    
    // Log violations by impact level
    Object.entries(violationsByImpact).forEach(([impact, violations]) => {
      cy.task('log', `Impact ${impact}: ${violations.length} violations`);
      violations.forEach(violation => {
        console.log(violation);
      });
    });
  });
});