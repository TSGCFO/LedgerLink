/// <reference types="cypress" />
// This test file requires:
// npm install --save-dev cypress-axe axe-core

describe('Accessibility Tests', () => {
  beforeEach(() => {
    // Login before testing protected pages
    cy.login();
    
    // Load axe for accessibility testing
    cy.injectAxe();
  });
  
  it('Dashboard page meets accessibility standards', () => {
    // Visit dashboard
    cy.visit('/dashboard');
    cy.wait(1000); // Allow page to fully load
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa'] // WCAG 2.0 A and AA standards
      }
    }, logA11yViolations);
  });
  
  it('Customers listing page meets accessibility standards', () => {
    // Visit customers page
    cy.visit('/customers');
    cy.wait(1000); // Allow page to fully load
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    }, logA11yViolations);
  });
  
  it('Orders listing page meets accessibility standards', () => {
    // Visit orders page
    cy.visit('/orders');
    cy.wait(1000); // Allow page to fully load
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    }, logA11yViolations);
  });
  
  it('Products listing page meets accessibility standards', () => {
    // Visit products page
    cy.visit('/products');
    cy.wait(1000); // Allow page to fully load
    
    // Run accessibility tests
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    }, logA11yViolations);
  });
  
  it('Form pages meet accessibility standards', () => {
    // Test customer create form
    cy.visit('/customers/new');
    cy.wait(1000); // Allow page to fully load
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    }, logA11yViolations);
    
    // Test order create form
    cy.visit('/orders/new');
    cy.wait(1000); // Allow page to fully load
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    }, logA11yViolations);
  });
  
  it('Tests keyboard navigation', () => {
    // Visit dashboard
    cy.visit('/dashboard');
    
    // Test tab navigation
    cy.focused().tab().should('have.attr', 'data-testid');
    cy.focused().tab().should('have.attr', 'data-testid');
    cy.focused().tab().should('have.attr', 'data-testid');
    
    // Navigate to customers page with keyboard
    cy.get('body').type('{enter}');
    cy.url().should('include', '/customers');
  });
});

// Helper function to log accessibility violations
function logA11yViolations(violations) {
  cy.logA11yViolations(violations);
  
  // Ensure there are no critical violations
  const criticalViolations = violations.filter(v => v.impact === 'critical');
  expect(criticalViolations.length).to.equal(0, 'No critical accessibility violations');
}