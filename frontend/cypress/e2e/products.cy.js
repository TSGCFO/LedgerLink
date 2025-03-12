/// <reference types="cypress" />

describe('Products Module', () => {
  beforeEach(() => {
    // Mock authentication
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'fake-token');
    });
    
    // Intercept and mock API calls
    cy.intercept('GET', '/api/v1/products*', {
      statusCode: 200,
      body: {
        success: true,
        data: [
          {
            id: 1,
            sku: 'SKU-001',
            customer: 1,
            customer_details: { company_name: 'Test Company' },
            labeling_unit_1: 'Box',
            labeling_quantity_1: 10,
            labeling_unit_2: 'Case',
            labeling_quantity_2: 5,
            created_at: '2025-03-01T10:00:00Z',
            updated_at: '2025-03-01T10:00:00Z'
          },
          {
            id: 2,
            sku: 'SKU-002',
            customer: 2,
            customer_details: { company_name: 'Another Company' },
            labeling_unit_1: 'Pallet',
            labeling_quantity_1: 1,
            created_at: '2025-03-02T10:00:00Z',
            updated_at: '2025-03-02T10:00:00Z'
          }
        ]
      }
    }).as('getProducts');
    
    cy.intercept('GET', '/api/v1/products/stats*', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          total_products: 2,
          products_by_customer: [
            { customer__company_name: 'Test Company', count: 1 },
            { customer__company_name: 'Another Company', count: 1 }
          ]
        }
      }
    }).as('getStats');
    
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
    
    cy.intercept('POST', '/api/v1/products*', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          id: 3,
          sku: 'NEW-SKU',
          customer: 1
        }
      }
    }).as('createProduct');
    
    cy.intercept('DELETE', '/api/v1/products/*', {
      statusCode: 200,
      body: {
        success: true
      }
    }).as('deleteProduct');
  });
  
  it('should load the products list page', () => {
    cy.visit('/products');
    cy.wait('@getProducts');
    cy.wait('@getStats');
    
    // Check page title/elements
    cy.contains('Total Products: 2').should('be.visible');
    cy.contains('Test Company: 1').should('be.visible');
    cy.contains('Another Company: 1').should('be.visible');
    
    // Check table headers
    cy.contains('SKU').should('be.visible');
    cy.contains('Customer').should('be.visible');
    cy.contains('Unit 1').should('be.visible');
    cy.contains('Qty 1').should('be.visible');
    
    // Check data rows
    cy.contains('SKU-001').should('be.visible');
    cy.contains('SKU-002').should('be.visible');
    cy.contains('Box').should('be.visible');
    cy.contains('Pallet').should('be.visible');
    
    // Check actions
    cy.contains('button', 'New Product').should('be.visible');
  });
  
  it('should navigate to the new product form', () => {
    cy.visit('/products');
    cy.wait('@getProducts');
    
    cy.contains('button', 'New Product').click();
    cy.url().should('include', '/products/new');
    
    cy.wait('@getCustomers');
    
    // Check form is loaded
    cy.contains('New Product').should('be.visible');
    cy.contains('label', 'SKU').should('be.visible');
    cy.contains('label', 'Customer').should('be.visible');
    cy.contains('button', 'Create Product').should('be.visible');
  });
  
  it('should validate the product form', () => {
    cy.visit('/products/new');
    cy.wait('@getCustomers');
    
    // Try to submit empty form
    cy.contains('button', 'Create Product').click();
    
    // Check validation errors
    cy.contains('SKU is required').should('be.visible');
    cy.contains('Customer is required').should('be.visible');
    
    // Fill SKU only
    cy.get('input[name="sku"]').type('NEW-SKU');
    cy.contains('button', 'Create Product').click();
    
    // Should still show customer error
    cy.contains('Customer is required').should('be.visible');
    
    // Fill unit but not quantity (to test paired validation)
    cy.get('input[name="labeling_unit_1"]').type('Box');
    cy.contains('button', 'Create Product').click();
    
    // Should show quantity error
    cy.contains('Quantity is required when unit is provided').should('be.visible');
  });
  
  it('should create a new product successfully', () => {
    cy.visit('/products/new');
    cy.wait('@getCustomers');
    
    // Fill required fields
    cy.get('input[name="sku"]').type('NEW-SKU');
    
    // Select customer
    cy.get('[aria-labelledby*="customer"]').click();
    cy.contains('Test Company').click();
    
    // Fill unit and quantity
    cy.get('input[name="labeling_unit_1"]').type('Box');
    cy.get('input[name="labeling_quantity_1"]').type('10');
    
    // Submit form
    cy.contains('button', 'Create Product').click();
    cy.wait('@createProduct');
    
    // Check success message
    cy.contains('Product created successfully').should('be.visible');
    
    // Should redirect back to list
    cy.url().should('include', '/products');
  });
  
  it('should delete a product after confirmation', () => {
    // Mock window.confirm to return true
    cy.on('window:confirm', () => true);
    
    cy.visit('/products');
    cy.wait('@getProducts');
    
    // Find and click delete button for first product
    cy.get('button[aria-label="Delete"]').first().click();
    
    // Wait for deletion API call
    cy.wait('@deleteProduct');
    
    // Check success message
    cy.contains('Product deleted successfully').should('be.visible');
    
    // Should reload the product list
    cy.wait('@getProducts');
  });
  
  it('should cancel product deletion when user confirms no', () => {
    // Mock window.confirm to return false
    cy.on('window:confirm', () => false);
    
    cy.visit('/products');
    cy.wait('@getProducts');
    
    // Find and click delete button for first product
    cy.get('button[aria-label="Delete"]').first().click();
    
    // Delete API should not be called
    cy.get('@deleteProduct.all').should('have.length', 0);
  });
});