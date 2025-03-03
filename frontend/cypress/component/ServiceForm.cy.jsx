import React from 'react';
import { mount } from 'cypress/react';
import { BrowserRouter } from 'react-router-dom';
import ServiceForm from '../../src/components/services/ServiceForm';
import '../../src/index.css';

describe('ServiceForm Visual Tests', () => {
  beforeEach(() => {
    // Mock localStorage for auth token
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'fake-token');
    });

    // Mock charge types API
    cy.intercept('GET', '/api/v1/services/charge_types*', {
      statusCode: 200,
      body: { 
        success: true,
        data: [
          { value: 'quantity', label: 'Per Quantity' },
          { value: 'fixed', label: 'Fixed Fee' },
          { value: 'hourly', label: 'Hourly Rate' },
          { value: 'weight', label: 'Per Weight' }
        ]
      }
    }).as('getChargeTypes');
  });

  it('renders correctly in create mode', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <ServiceForm />
      </BrowserRouter>
    );

    cy.wait('@getChargeTypes');

    // Check key elements
    cy.contains('New Service').should('be.visible');
    cy.contains('Service Name').should('be.visible');
    cy.contains('Description').should('be.visible');
    cy.contains('Charge Type').should('be.visible');
    cy.contains('button', 'Create Service').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('service-form-create-mode');
  });

  it('shows validation errors correctly', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <ServiceForm />
      </BrowserRouter>
    );

    cy.wait('@getChargeTypes');

    // Click submit without filling required fields
    cy.contains('button', 'Create Service').click();

    // Check validation errors are displayed
    cy.contains('Service name is required').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('service-form-validation-errors');
  });

  it('renders form with filled data', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <ServiceForm />
      </BrowserRouter>
    );

    cy.wait('@getChargeTypes');

    // Fill form fields
    cy.get('input[name="service_name"]').type('Test Service');
    cy.get('textarea[name="description"]').type('This is a test service description with multiple lines of text.');

    // Select charge type
    cy.get('[aria-labelledby*="charge_type"]').click();
    cy.contains('Hourly Rate').click();

    // Take a screenshot for visual comparison
    cy.screenshot('service-form-filled');
  });
  
  it('renders in edit mode', () => {
    // Mock edit mode by intercepting service data
    cy.intercept('GET', '/api/v1/services/123*', {
      statusCode: 200,
      body: {
        id: 123,
        service_name: 'Existing Service',
        description: 'This is an existing service description.',
        charge_type: 'fixed'
      }
    }).as('getService');
    
    // Use custom window to create route params
    cy.window().then((win) => {
      // Create a fake router context for edit mode
      win.mockParams = { id: '123' };
      cy.stub(win.React, 'useParams').returns(win.mockParams);
    });
    
    // Mount with edit mode
    cy.mount(
      <BrowserRouter>
        <ServiceForm />
      </BrowserRouter>
    );
    
    cy.wait('@getChargeTypes');
    cy.wait('@getService');
    
    // Check edit mode elements
    cy.contains('Edit Service').should('be.visible');
    cy.get('input[name="service_name"]').should('have.value', 'Existing Service');
    cy.get('textarea[name="description"]').should('have.value', 'This is an existing service description.');
    cy.contains('button', 'Update Service').should('be.visible');
    
    // Take a screenshot for visual comparison
    cy.screenshot('service-form-edit-mode');
  });
});