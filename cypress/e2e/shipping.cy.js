/// <reference types="cypress" />

describe('Shipping Management', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Intercept API calls
    cy.intercept('GET', '**/shipping/cad/**').as('getCadShipping');
    cy.intercept('POST', '**/shipping/cad/**').as('createCadShipping');
    cy.intercept('PUT', '**/shipping/cad/**').as('updateCadShipping');
    cy.intercept('DELETE', '**/shipping/cad/**').as('deleteCadShipping');
    
    cy.intercept('GET', '**/shipping/us/**').as('getUsShipping');
    cy.intercept('POST', '**/shipping/us/**').as('createUsShipping');
    cy.intercept('PUT', '**/shipping/us/**').as('updateUsShipping');
    cy.intercept('DELETE', '**/shipping/us/**').as('deleteUsShipping');
  });
  
  describe('CAD Shipping', () => {
    beforeEach(() => {
      // Navigate to CAD shipping page
      cy.visit('/shipping/cad');
      
      // Wait for the shipping list to load
      cy.wait('@getCadShipping');
    });
    
    it('displays CAD shipping listing page correctly', () => {
      // Check page elements
      cy.get('[data-testid="shipping-list"]').should('exist');
      cy.get('[data-testid="add-shipping-button"]').should('exist');
      cy.get('[data-testid="shipping-filter"]').should('exist');
      
      // Verify table columns
      cy.get('[data-testid="shipping-table"]').within(() => {
        cy.contains('th', 'Order #').should('be.visible');
        cy.contains('th', 'Customer').should('be.visible');
        cy.contains('th', 'Tracking #').should('be.visible');
        cy.contains('th', 'Carrier').should('be.visible');
        cy.contains('th', 'Ship Date').should('be.visible');
        cy.contains('th', 'Status').should('be.visible');
      });
    });
    
    it('filters CAD shipping records', () => {
      // Type into carrier filter
      cy.get('[data-testid="carrier-filter"]').select('Canada Post');
      
      // Wait for filtered results
      cy.wait('@getCadShipping');
      
      // Verify filtered results
      cy.get('[data-testid="shipping-item"]').each(($item) => {
        cy.wrap($item).should('contain', 'Canada Post');
      });
      
      // Search by tracking number
      cy.get('[data-testid="tracking-search"]').type('CAD');
      cy.wait('@getCadShipping');
      
      // Verify search results
      cy.get('[data-testid="shipping-item"]').should('have.length.gt', 0);
    });
    
    it('creates a new CAD shipping record', () => {
      // Create an order first if needed
      cy.createOrder().then(order => {
        // Click add shipping button
        cy.get('[data-testid="add-shipping-button"]').click();
        
        // Verify navigation to create page
        cy.url().should('include', '/shipping/cad/new');
        
        // Fill out form with valid data
        cy.get('[data-testid="transaction-select"]').select(order.id.toString());
        cy.get('[data-testid="ship-to-name-input"]').type('Test Recipient');
        cy.get('[data-testid="ship-to-address-1-input"]').type('123 Maple St');
        cy.get('[data-testid="ship-to-city-input"]').type('Toronto');
        cy.get('[data-testid="ship-to-state-input"]').type('ON');
        cy.get('[data-testid="ship-to-postal-code-input"]').type('M5V 2L7');
        cy.get('[data-testid="carrier-select"]').select('Canada Post');
        cy.get('[data-testid="tracking-number-input"]').type(`CAD-${Date.now().toString()}`);
        cy.get('[data-testid="pre-tax-shipping-charge-input"]').type('25.99');
        
        // Submit form
        cy.get('[data-testid="shipping-form"]').submit();
        
        // Wait for API call
        cy.wait('@createCadShipping');
        
        // Verify redirect to shipping detail page
        cy.url().should('match', /\/shipping\/cad\/\d+/);
        
        // Verify shipping data is displayed
        cy.get('[data-testid="shipping-detail"]').should('contain', 'Test Recipient');
        cy.get('[data-testid="shipping-detail"]').should('contain', 'Canada Post');
      });
    });
    
    it('edits an existing CAD shipping record', () => {
      // Click on first shipping record in list
      cy.get('[data-testid="shipping-item"]').first().click();
      
      // Verify navigation to detail page
      cy.url().should('match', /\/shipping\/cad\/\d+/);
      
      // Click edit button
      cy.get('[data-testid="edit-shipping-button"]').click();
      
      // Verify navigation to edit page
      cy.url().should('include', '/edit');
      
      // Update tracking number
      const updatedTracking = `CAD-UPD-${Date.now().toString()}`;
      cy.get('[data-testid="tracking-number-input"]').clear().type(updatedTracking);
      
      // Submit form
      cy.get('[data-testid="shipping-form"]').submit();
      
      // Wait for API call
      cy.wait('@updateCadShipping');
      
      // Verify redirect to detail page
      cy.url().should('match', /\/shipping\/cad\/\d+/);
      cy.url().should('not.include', '/edit');
      
      // Verify updated data is displayed
      cy.get('[data-testid="shipping-detail"]').should('contain', updatedTracking);
    });
    
    it('deletes a CAD shipping record', () => {
      // Get count of shipping records before delete
      cy.get('[data-testid="shipping-item"]').then($items => {
        const initialCount = $items.length;
        
        // Click on first shipping record in list
        cy.get('[data-testid="shipping-item"]').first().click();
        
        // Click delete button
        cy.get('[data-testid="delete-shipping-button"]').click();
        
        // Confirm deletion in modal
        cy.get('[data-testid="confirm-delete-button"]').click();
        
        // Wait for API call
        cy.wait('@deleteCadShipping');
        
        // Verify redirect to shipping list
        cy.url().should('include', '/shipping/cad');
        cy.url().should('not.match', /\/shipping\/cad\/\d+/);
        
        // Verify shipping record count decreased
        cy.get('[data-testid="shipping-item"]').should('have.length', initialCount - 1);
      });
    });
    
    it('displays calculated tax and charges', () => {
      // Click on a shipping record with charges
      cy.get('[data-testid="shipping-item"]').first().click();
      
      // Verify calculated fields are displayed
      cy.get('[data-testid="shipping-detail"]').within(() => {
        cy.contains('Pre-tax Shipping').should('exist');
        cy.contains('Taxes').should('exist');
        cy.contains('Total Charges').should('exist');
      });
      
      // Verify calculation is correct when editing
      cy.get('[data-testid="edit-shipping-button"]').click();
      
      // Update charges
      cy.get('[data-testid="pre-tax-shipping-charge-input"]').clear().type('50.00');
      cy.get('[data-testid="tax1type-input"]').select('GST');
      cy.get('[data-testid="tax1amount-input"]').clear().type('2.50');
      
      // Check calculated total gets updated
      cy.get('[data-testid="total-charges"]').should('contain', '52.50');
    });
  });
  
  describe('US Shipping', () => {
    beforeEach(() => {
      // Navigate to US shipping page
      cy.visit('/shipping/us');
      
      // Wait for the shipping list to load
      cy.wait('@getUsShipping');
    });
    
    it('displays US shipping listing page correctly', () => {
      // Check page elements
      cy.get('[data-testid="shipping-list"]').should('exist');
      cy.get('[data-testid="add-shipping-button"]').should('exist');
      cy.get('[data-testid="shipping-filter"]').should('exist');
      
      // Verify table columns
      cy.get('[data-testid="shipping-table"]').within(() => {
        cy.contains('th', 'Order #').should('be.visible');
        cy.contains('th', 'Customer').should('be.visible');
        cy.contains('th', 'Tracking #').should('be.visible');
        cy.contains('th', 'Service').should('be.visible');
        cy.contains('th', 'Ship Date').should('be.visible');
        cy.contains('th', 'Status').should('be.visible');
      });
    });
    
    it('filters US shipping by current status', () => {
      // Select status filter
      cy.get('[data-testid="status-filter"]').select('in_transit');
      
      // Wait for filtered results
      cy.wait('@getUsShipping');
      
      // Verify filtered results
      cy.get('[data-testid="shipping-item"]').each(($item) => {
        cy.wrap($item).should('contain', 'In Transit');
      });
    });
    
    it('creates a new US shipping record', () => {
      // Create an order first if needed
      cy.createOrder().then(order => {
        // Click add shipping button
        cy.get('[data-testid="add-shipping-button"]').click();
        
        // Verify navigation to create page
        cy.url().should('include', '/shipping/us/new');
        
        // Fill out form with valid data
        cy.get('[data-testid="transaction-select"]').select(order.id.toString());
        cy.get('[data-testid="ship-to-name-input"]').type('US Recipient');
        cy.get('[data-testid="ship-to-address-1-input"]').type('456 Oak Ave');
        cy.get('[data-testid="ship-to-city-input"]').type('New York');
        cy.get('[data-testid="ship-to-state-input"]').type('NY');
        cy.get('[data-testid="ship-to-zip-input"]').type('10001');
        cy.get('[data-testid="service-name-select"]').select('Express');
        cy.get('[data-testid="tracking-number-input"]').type(`US-${Date.now().toString()}`);
        cy.get('[data-testid="current-status-select"]').select('in_transit');
        cy.get('[data-testid="delivery-status-select"]').select('pending');
        cy.get('[data-testid="ship-date-input"]').type(new Date().toISOString().split('T')[0]);
        
        // Submit form
        cy.get('[data-testid="shipping-form"]').submit();
        
        // Wait for API call
        cy.wait('@createUsShipping');
        
        // Verify redirect to shipping detail page
        cy.url().should('match', /\/shipping\/us\/\d+/);
        
        // Verify shipping data is displayed
        cy.get('[data-testid="shipping-detail"]').should('contain', 'US Recipient');
        cy.get('[data-testid="shipping-detail"]').should('contain', 'Express');
        cy.get('[data-testid="shipping-detail"]').should('contain', 'In Transit');
      });
    });
    
    it('updates shipping status to delivered', () => {
      // Click on first shipping record in list
      cy.get('[data-testid="shipping-item"]').first().click();
      
      // Click edit button
      cy.get('[data-testid="edit-shipping-button"]').click();
      
      // Update status
      cy.get('[data-testid="current-status-select"]').select('delivered');
      cy.get('[data-testid="delivery-status-select"]').select('delivered');
      
      // Add delivery date
      cy.get('[data-testid="delivery-date-input"]').type(new Date().toISOString().split('T')[0]);
      
      // Submit form
      cy.get('[data-testid="shipping-form"]').submit();
      
      // Wait for API call
      cy.wait('@updateUsShipping');
      
      // Verify status is updated
      cy.get('[data-testid="shipping-detail"]').should('contain', 'Delivered');
      
      // Verify delivery days are calculated
      cy.get('[data-testid="delivery-days"]').should('exist');
    });
    
    it('displays delivery metrics and analytics', () => {
      // Navigate to shipping analytics page
      cy.visit('/shipping/analytics');
      
      // Check for analytics components
      cy.get('[data-testid="shipping-analytics"]').should('exist');
      cy.get('[data-testid="delivery-time-chart"]').should('exist');
      cy.get('[data-testid="carrier-performance-chart"]').should('exist');
      cy.get('[data-testid="status-distribution-chart"]').should('exist');
      
      // Check filter controls
      cy.get('[data-testid="date-range-filter"]').should('exist');
      cy.get('[data-testid="carrier-filter"]').should('exist');
      
      // Test date range filter
      const startDate = new Date();
      startDate.setMonth(startDate.getMonth() - 1);
      const endDate = new Date();
      
      cy.get('[data-testid="start-date-input"]').type(startDate.toISOString().split('T')[0]);
      cy.get('[data-testid="end-date-input"]').type(endDate.toISOString().split('T')[0]);
      cy.get('[data-testid="apply-filter-button"]').click();
      
      // Verify charts update
      cy.get('[data-testid="delivery-time-chart"]').should('be.visible');
      cy.get('[data-testid="carrier-performance-chart"]').should('be.visible');
    });
  });
  
  describe('Bulk Shipping Operations', () => {
    it('imports shipping records from CSV', () => {
      // Navigate to bulk operations page
      cy.visit('/bulk-operations');
      
      // Select shipping template
      cy.get('[data-testid="template-type"]').select('cad_shipping');
      
      // Download template for reference
      cy.get('[data-testid="download-template-button"]').click();
      
      // Upload CSV file
      cy.fixture('cad_shipping_sample.csv').then(fileContent => {
        cy.get('[data-testid="file-upload"]').attachFile({
          fileContent: fileContent.toString(),
          fileName: 'cad_shipping_import.csv',
          mimeType: 'text/csv'
        });
      });
      
      // Submit import
      cy.get('[data-testid="import-button"]').click();
      
      // Verify success message
      cy.get('[data-testid="import-result"]').should('contain', 'Import completed');
      cy.get('[data-testid="import-summary"]').should('contain', 'successful');
      
      // Navigate to shipping list to verify imported records
      cy.visit('/shipping/cad');
      cy.wait('@getCadShipping');
      
      // Should show imported records
      cy.get('[data-testid="shipping-item"]').should('have.length.gt', 0);
    });
  });
});