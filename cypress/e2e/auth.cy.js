/// <reference types="cypress" />

describe('Authentication', () => {
  beforeEach(() => {
    // Clear cookies and local storage before each test
    cy.clearCookies();
    cy.clearLocalStorage();
    
    // Visit the home page
    cy.visit('/');
  });
  
  it('redirects to login when not authenticated', () => {
    // Should be redirected to login page
    cy.url().should('include', '/login');
    cy.get('[data-testid="login-form"]').should('be.visible');
  });
  
  it('shows error message for invalid credentials', () => {
    // Try to login with invalid credentials
    cy.get('[data-testid="username-input"]').type('wronguser');
    cy.get('[data-testid="password-input"]').type('wrongpass');
    cy.get('[data-testid="login-button"]').click();
    
    // Should show error message
    cy.get('[data-testid="login-error"]').should('be.visible');
    cy.get('[data-testid="login-error"]').should('contain', 'Invalid credentials');
    
    // Should still be on login page
    cy.url().should('include', '/login');
  });
  
  it('successfully logs in with valid credentials', () => {
    // Login with valid credentials
    cy.get('[data-testid="username-input"]').type('testuser');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    // Should be redirected to dashboard
    cy.url().should('include', '/dashboard');
    
    // Navbar should show logged in user
    cy.get('[data-testid="user-menu"]').should('contain', 'testuser');
  });
  
  it('successfully logs out', () => {
    // Login first
    cy.get('[data-testid="username-input"]').type('testuser');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for login to complete
    cy.url().should('include', '/dashboard');
    
    // Click logout button
    cy.get('[data-testid="user-menu"]').click();
    cy.get('[data-testid="logout-button"]').click();
    
    // Should be redirected to login page
    cy.url().should('include', '/login');
    
    // Try to access protected page
    cy.visit('/dashboard');
    
    // Should be redirected to login again
    cy.url().should('include', '/login');
  });
  
  it('uses the custom login command', () => {
    // Use custom command
    cy.login('testuser', 'password123');
    
    // Verify logged in state
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-menu"]').should('contain', 'testuser');
    
    // Logout
    cy.logout();
    
    // Verify logged out
    cy.url().should('include', '/login');
  });
});