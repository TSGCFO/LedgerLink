/// <reference types="cypress" />

describe('Billing Module', () => {
  beforeEach(() => {
    // Mock authentication
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'fake-token');
    });
    
    // Intercept and mock customer API
    cy.intercept('GET', '/api/v1/customers*', {
      statusCode: 200,
      body: {
        results: [
          { id: 1, company_name: 'Test Company' },
          { id: 2, company_name: 'Another Company' }
        ]
      }
    }).as('getCustomers');
    
    // Mock billing report data
    cy.intercept('POST', '/api/v1/billing/api/generate-report/', {
      statusCode: 200,
      body: {
        customer_name: 'Test Company',
        start_date: '2025-01-01',
        end_date: '2025-02-01',
        total_amount: 1500.00,
        preview_data: {
          orders: [
            {
              order_id: 'ORD-001',
              transaction_date: '2025-01-15',
              status: 'Completed',
              ship_to_name: 'John Smith',
              ship_to_address: '123 Test St',
              total_items: 5,
              line_items: 2,
              weight_lb: 10,
              services: [
                { service_id: 1, service_name: 'Standard Shipping', amount: 25.00 }
              ],
              total_amount: 150.00
            }
          ]
        },
        service_totals: {
          1: { name: 'Standard Shipping', amount: 25.00, order_count: 1 }
        }
      }
    }).as('generateReport');
  });
  
  it('should load the billing list page', () => {
    cy.visit('/billing');
    cy.wait('@getCustomers');
    
    cy.contains('Generate Billing Report').should('be.visible');
    cy.get('label').contains('Customer').should('be.visible');
    cy.get('label').contains('Start Date').should('be.visible');
    cy.get('label').contains('End Date').should('be.visible');
    cy.get('button').contains('Calculate').should('be.visible');
  });
  
  it('should validate form fields', () => {
    cy.visit('/billing');
    cy.wait('@getCustomers');
    
    // Click calculate without filling any fields
    cy.get('button').contains('Calculate').click();
    
    // Should display validation error
    cy.contains('Please select a customer and date range').should('be.visible');
  });
  
  it('should generate a billing report', () => {
    cy.visit('/billing');
    cy.wait('@getCustomers');
    
    // Select customer
    cy.get('label').contains('Customer').parent().click();
    cy.get('[role="option"]').contains('Test Company').click();
    
    // Enter dates (may need adjustments based on your date picker implementation)
    cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
    cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
    
    // Click calculate
    cy.get('button').contains('Calculate').click();
    cy.wait('@generateReport');
    
    // Verify table appears with data
    cy.contains('ORD-001').should('be.visible');
    cy.contains('$150.00').should('be.visible');
    cy.contains('Standard Shipping').should('be.visible');
  });
  
  it('should navigate to the billing form page', () => {
    cy.visit('/billing/new');
    cy.wait('@getCustomers');
    
    cy.contains('Generate Billing Report').should('be.visible');
    cy.get('label').contains('Customer').should('be.visible');
    cy.get('label').contains('Start Date').should('be.visible');
    cy.get('label').contains('End Date').should('be.visible');
    cy.get('label').contains('Export Format').should('be.visible');
    cy.get('button').contains('Generate Report').should('be.visible');
  });
});