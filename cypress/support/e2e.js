// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';
import './shipping-commands';

// Cypress-specific global behavior
beforeEach(() => {
  // Clear localStorage before each test to ensure clean state
  cy.clearLocalStorage();
  
  // Preserve cookie access across multiple tests and domains
  Cypress.Cookies.preserveOnce('sessionid', 'csrftoken');
});

// Add better error reporting
Cypress.on('uncaught:exception', (err, runnable) => {
  // Log the error to the console for debugging
  console.error('Uncaught Exception:', err.message);
  
  // Returning false here prevents Cypress from failing the test
  // You may want to remove this in production to catch real errors
  return false;
});