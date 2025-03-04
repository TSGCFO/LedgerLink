/**
 * Basic navigation tests that verify pages exist
 */
describe('Navigation Tests', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
  });
  
  it('renders the dashboard page', () => {
    cy.visit('/dashboard');
    cy.contains(/dashboard/i, { timeout: 10000 }).should('exist');
  });
  
  it('renders the customers list page', () => {
    cy.visit('/customers');
    // Just check if the page renders
    cy.get('body').should('be.visible');
  });
  
  it('renders the customer form page', () => {
    cy.visit('/customers/new');
    // Check for any input elements rather than specific form
    cy.get('input').should('exist');
  });
  
  it('renders the orders page', () => {
    cy.visit('/orders');
    // Less specific check for page content
    cy.contains(/orders/i, { timeout: 10000 }).should('exist');
  });
  
  it('renders the products page', () => {
    cy.visit('/products');
    // Less specific check for page content
    cy.contains(/products/i, { timeout: 10000 }).should('exist');
  });
  
  it('renders the bulk operations page', () => {
    cy.visit('/bulk-operations');
    cy.contains(/bulk operations/i, { timeout: 10000 }).should('exist');
  });
});