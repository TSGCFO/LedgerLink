import React from 'react';
import { mount } from 'cypress/react';
import { BrowserRouter } from 'react-router-dom';
import BillingForm from '../../src/components/billing/BillingForm';
import '../../src/index.css';

describe('BillingForm Visual Tests', () => {
  beforeEach(() => {
    // Mock localStorage for auth token
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'fake-token');
    });

    // Mock API calls
    cy.intercept('GET', '/api/v1/customers*', {
      statusCode: 200,
      body: { 
        results: [
          { id: 1, company_name: 'Test Company' },
          { id: 2, company_name: 'Another Company' }
        ]
      }
    }).as('getCustomers');
  });

  it('renders correctly in create mode', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Check key elements
    cy.contains('Generate Billing Report').should('be.visible');
    cy.contains('Customer').should('be.visible');
    cy.contains('Start Date').should('be.visible');
    cy.contains('End Date').should('be.visible');
    cy.contains('Export Format').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('billing-form-create-mode');
  });

  it('shows validation errors correctly', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Click submit without filling required fields
    cy.contains('button', 'Generate Report').click();

    // Check validation errors are displayed
    cy.contains('Customer is required').should('be.visible');
    cy.contains('Start date is required').should('be.visible');
    cy.contains('End date is required').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('billing-form-validation-errors');
  });

  it('renders form with filled data', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <BillingForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Fill form fields
    cy.get('[aria-labelledby*="customer"]').click();
    cy.contains('Test Company').click();

    // Set dates
    cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
    cy.get('input[placeholder*="MM/DD/YYYY"]').eq(1).type('02/01/2025');

    // Take a screenshot for visual comparison
    cy.screenshot('billing-form-filled');
  });
});