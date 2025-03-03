/**
 * End-to-end tests for authentication
 */
describe('Authentication', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    cy.clearLocalStorage();
    cy.visit('/login');
  });
  
  it('should display login form', () => {
    cy.get('#username').should('be.visible');
    cy.get('#password').should('be.visible');
    cy.get('button[type="submit"]').contains('Sign In').should('be.visible');
  });
  
  it('should show error for invalid credentials', () => {
    // Intercept the login request and mock a failure
    cy.intercept('POST', '/api/v1/auth/token/', {
      statusCode: 401,
      body: { detail: 'Invalid credentials' }
    }).as('loginFailure');
    
    cy.get('#username').type('invalid');
    cy.get('#password').type('invalid');
    cy.get('button[type="submit"]').click();
    
    // Wait for the request to fail
    cy.wait('@loginFailure');
    
    // Error message should appear
    cy.get('.MuiAlert-root').should('be.visible');
    cy.get('.MuiAlert-root').should('contain', 'Invalid username or password');
  });
  
  it('should log in successfully with valid credentials', () => {
    // Intercept the login request with mock response
    cy.intercept('POST', '/api/v1/auth/token/', {
      statusCode: 200,
      body: {
        access: 'fake-access-token',
        refresh: 'fake-refresh-token'
      }
    }).as('loginSuccess');
    
    // Fill out the form
    cy.get('#username').type('admin');
    cy.get('#password').type('adminpassword');
    cy.get('button[type="submit"]').click();
    
    // Wait for the request to complete
    cy.wait('@loginSuccess');
    
    // Should redirect to home page (mock this behavior)
    cy.url().should('eq', Cypress.config().baseUrl + '/');
    
    // Check that tokens were saved
    cy.window().then((window) => {
      expect(window.localStorage.getItem('auth_token')).to.equal('fake-access-token');
      expect(window.localStorage.getItem('refresh_token')).to.equal('fake-refresh-token');
    });
  });
  
  it('should redirect unauthenticated users to login when accessing protected route', () => {
    // With no auth token, attempting to access protected route
    cy.visit('/customers');
    
    // Should redirect to login
    cy.url().should('include', '/login');
  });
  
  it('should allow access to protected routes when authenticated', () => {
    // Set fake tokens directly
    cy.window().then((window) => {
      window.localStorage.setItem('auth_token', 'fake-auth-token');
      window.localStorage.setItem('refresh_token', 'fake-refresh-token');
    });
    
    // Visit protected route
    cy.visit('/customers');
    
    // Should not redirect to login
    cy.url().should('include', '/customers');
  });
  
  it('should log out successfully', () => {
    // Set fake tokens first
    cy.window().then((window) => {
      window.localStorage.setItem('auth_token', 'fake-auth-token');
      window.localStorage.setItem('refresh_token', 'fake-refresh-token');
    });
    
    // Visit home page
    cy.visit('/');
    
    // Then log out (assuming logout button is in header)
    cy.get('[data-testid="logout-button"]').click();
    
    // Should be on login page
    cy.url().should('include', '/login');
    
    // Local storage should be cleared
    cy.window().then((window) => {
      expect(window.localStorage.getItem('auth_token')).to.be.null;
      expect(window.localStorage.getItem('refresh_token')).to.be.null;
    });
  });
  
  it('should maintain accessibility standards', () => {
    // First load the page
    cy.injectAxe();
    
    // Check accessibility of login page
    cy.checkPageA11y(null, {
      rules: {
        // Customize rules as needed
        'color-contrast': { enabled: true },
        'label': { enabled: true },
        'aria-required-attr': { enabled: true }
      }
    });
    
    // Check login form with filled values
    cy.get('#username').type('admin');
    cy.get('#password').type('password');
    cy.checkPageA11y();
    
    // Check login form with error state
    cy.intercept('POST', '/api/v1/auth/token/', {
      statusCode: 401,
      body: { detail: 'Invalid credentials' }
    });
    cy.get('button[type="submit"]').click();
    cy.get('.MuiAlert-root').should('be.visible');
    cy.checkPageA11y();
    
    // Log accessibility violations to console for debugging
    cy.logA11yViolations();
  });
});