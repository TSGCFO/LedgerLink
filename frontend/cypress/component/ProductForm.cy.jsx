import React from 'react';
import { mount } from 'cypress/react';
import { BrowserRouter } from 'react-router-dom';
import ProductForm from '../../src/components/products/ProductForm';
import '../../src/index.css';

describe('ProductForm Visual Tests', () => {
  beforeEach(() => {
    // Mock localStorage for auth token
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'fake-token');
    });

    // Mock API calls
    cy.intercept('GET', '/api/v1/customers*', {
      statusCode: 200,
      body: { 
        success: true,
        data: [
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
        <ProductForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Check key elements
    cy.contains('New Product').should('be.visible');
    cy.contains('SKU').should('be.visible');
    cy.contains('Customer').should('be.visible');
    cy.contains('Labeling Unit 1').should('be.visible');
    cy.contains('Labeling Quantity 1').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('product-form-create-mode');
  });

  it('shows validation errors correctly', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <ProductForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Click submit without filling required fields
    cy.contains('button', 'Create Product').click();

    // Check validation errors are displayed
    cy.contains('SKU is required').should('be.visible');
    cy.contains('Customer is required').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('product-form-validation-errors');
  });

  it('renders with unit-quantity validation errors', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <ProductForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Fill SKU
    cy.get('input[name="sku"]').type('TEST-SKU');

    // Select customer
    cy.get('[aria-labelledby*="customer"]').click();
    cy.contains('Test Company').click();

    // Add a unit but no quantity
    cy.get('input[name="labeling_unit_1"]').type('Box');

    // Submit form
    cy.contains('button', 'Create Product').click();

    // Check unit-quantity validation error
    cy.contains('Quantity is required when unit is provided').should('be.visible');

    // Take a screenshot for visual comparison
    cy.screenshot('product-form-unit-quantity-validation');
  });

  it('renders form with filled data', () => {
    // Mount the component
    cy.mount(
      <BrowserRouter>
        <ProductForm />
      </BrowserRouter>
    );

    cy.wait('@getCustomers');

    // Fill form fields
    cy.get('input[name="sku"]').type('TEST-SKU');

    // Select customer
    cy.get('[aria-labelledby*="customer"]').click();
    cy.contains('Test Company').click();

    // Fill unit and quantity pairs
    cy.get('input[name="labeling_unit_1"]').type('Box');
    cy.get('input[name="labeling_quantity_1"]').type('10');
    cy.get('input[name="labeling_unit_2"]').type('Case');
    cy.get('input[name="labeling_quantity_2"]').type('5');

    // Take a screenshot for visual comparison
    cy.screenshot('product-form-filled');
  });
});