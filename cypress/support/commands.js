// ***********************************************
// Custom commands for LedgerLink application
// ***********************************************

// Authentication commands
Cypress.Commands.add('login', (username = 'testuser', password = 'password123') => {
  cy.visit('/login');
  cy.get('[data-testid="username-input"]').type(username);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="login-button"]').click();
  
  // Verify successful login - wait for the dashboard to load
  cy.url().should('not.include', '/login');
  cy.log(`Logged in as ${username}`);
});

Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click();
  cy.get('[data-testid="logout-button"]').click();
  cy.url().should('include', '/login');
  cy.log('Logged out successfully');
});

// Data management commands
Cypress.Commands.add('createCustomer', (customerData = {}) => {
  const defaultData = {
    company_name: `Test Company ${Date.now()}`,
    contact_name: 'Test Contact',
    contact_email: `test${Date.now()}@example.com`,
    contact_phone: '555-123-4567',
    address: '123 Test St',
    city: 'Test City',
    state: 'TS',
    postal_code: '12345',
    country: 'US'
  };
  
  const data = { ...defaultData, ...customerData };
  
  // Navigate to customer creation page
  cy.visit('/customers/new');
  
  // Fill out the form
  cy.get('[data-testid="company-name-input"]').type(data.company_name);
  cy.get('[data-testid="contact-name-input"]').type(data.contact_name);
  cy.get('[data-testid="contact-email-input"]').type(data.contact_email);
  cy.get('[data-testid="contact-phone-input"]').type(data.contact_phone);
  cy.get('[data-testid="address-input"]').type(data.address);
  cy.get('[data-testid="city-input"]').type(data.city);
  cy.get('[data-testid="state-input"]').type(data.state);
  cy.get('[data-testid="postal-code-input"]').type(data.postal_code);
  cy.get('[data-testid="country-input"]').type(data.country);
  
  // Submit the form
  cy.get('[data-testid="customer-form"]').submit();
  
  // Verify creation was successful
  cy.url().should('include', '/customers/');
  cy.url().should('not.include', '/new');
  
  return cy.wrap(data);
});

Cypress.Commands.add('cleanupTestData', () => {
  // This requires backend API access to clean up test data
  // Implementation depends on available API endpoints
  cy.log('Cleaning up test data via API');
  
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/test-cleanup/`,
    headers: {
      'Content-Type': 'application/json',
    },
    body: {
      cleanup_type: 'test_data',
      created_after: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // last 24 hours
    }
  }).then((response) => {
    cy.log(`Cleanup completed with status: ${response.status}`);
  });
});

// Accessibility testing commands
// Note: Requires the cypress-axe package to be installed
// npm install --save-dev cypress-axe axe-core
Cypress.Commands.add('checkA11y', (context, options) => {
  cy.log('Running accessibility checks');
  cy.injectAxe();
  cy.checkA11y(context, options);
});

Cypress.Commands.add('logA11yViolations', (violations) => {
  cy.task('log', `${violations.length} accessibility violation(s) detected`);
  
  // Log violation details to console
  const violationData = violations.map(
    ({ id, impact, description, nodes }) => ({
      id,
      impact,
      description,
      nodes: nodes.length
    })
  );
  
  cy.task('log', `Violations: ${JSON.stringify(violationData, null, 2)}`);
});