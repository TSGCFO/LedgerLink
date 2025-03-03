/**
 * End-to-end accessibility tests
 */
describe('Accessibility Tests', () => {
  beforeEach(() => {
    // Log in before each test
    cy.login();
  });
  
  it('should not have accessibility violations on dashboard', () => {
    cy.visit('/dashboard');
    cy.injectAxe();
    
    // Run accessibility tests
    cy.checkA11y(null, {
      // Options for axe-core
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
  });
  
  it('should not have accessibility violations on customer list', () => {
    cy.visit('/customers');
    cy.injectAxe();
    
    // Wait for the page to load
    cy.get('table').should('be.visible');
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
  });
  
  it('should not have accessibility violations on customer form', () => {
    cy.visit('/customers/new');
    cy.injectAxe();
    
    // Wait for the form to load
    cy.get('form').should('be.visible');
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
    
    // Fill in a field and test again
    cy.get('input[name="company_name"]').type('Test Company');
    cy.checkA11y();
  });
  
  it('should not have accessibility violations on orders list', () => {
    cy.visit('/orders');
    cy.injectAxe();
    
    // Wait for the page to load
    cy.contains('h1', 'Orders').should('be.visible');
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
  });
  
  it('should not have accessibility violations on products list', () => {
    cy.visit('/products');
    cy.injectAxe();
    
    // Wait for the page to load
    cy.contains('h1', 'Products').should('be.visible');
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
  });
  
  it('should not have accessibility violations on error pages', () => {
    // Visit a non-existent page to generate a 404
    cy.visit('/this-page-does-not-exist', { failOnStatusCode: false });
    cy.injectAxe();
    
    // Wait for the error page to load
    cy.contains(/not found|404/i).should('be.visible');
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
  });
});