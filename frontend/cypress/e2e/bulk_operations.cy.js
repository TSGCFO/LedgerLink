// Bulk Operations Workflow E2E Tests
describe('Bulk Operations', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Mock API responses for consistent testing
    // Templates response
    cy.intercept('GET', '/api/v1/bulk-operations/templates/', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          templates: [
            {
              type: 'orders',
              name: 'Orders Import',
              description: 'Import order data with customer and product information',
              fieldCount: 8
            },
            {
              type: 'products',
              name: 'Products Import',
              description: 'Import product catalog data',
              fieldCount: 5
            },
            {
              type: 'customers',
              name: 'Customers Import',
              description: 'Import customer information in bulk',
              fieldCount: 10
            }
          ]
        }
      }
    }).as('getTemplates');

    // Template info response
    cy.intercept('GET', '/api/v1/bulk-operations/templates/template-info/*', {
      statusCode: 200,
      body: {
        success: true,
        data: {
          fields: {
            id: { description: 'Unique identifier' },
            name: { description: 'Name of the item' },
            quantity: { description: 'Order quantity' },
            price: { description: 'Unit price' },
            date: { description: 'Order date' }
          },
          requiredFields: ['id', 'name', 'quantity'],
          fieldTypes: { 
            id: 'integer', 
            name: 'string', 
            quantity: 'integer', 
            price: 'decimal', 
            date: 'date' 
          }
        }
      }
    }).as('getTemplateInfo');

    // Template download response
    cy.intercept('GET', '/api/v1/bulk-operations/templates/*/download/', req => {
      req.reply({
        statusCode: 200,
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': 'attachment; filename="template.csv"'
        },
        body: 'id,name,quantity,price,date\n'
      });
    }).as('downloadTemplate');

    // Import validation response - success
    cy.intercept('POST', '/api/v1/bulk-operations/import/orders/', {
      statusCode: 200,
      body: {
        success: true,
        import_summary: {
          total_rows: 10,
          successful: 8,
          failed: 2
        },
        errors: [
          { row: 3, errors: { 'price': ['Must be a positive number'] } },
          { row: 7, errors: { 'date': ['Invalid date format'] } }
        ]
      }
    }).as('importValidation');
    
    // Make sure the POST endpoint is properly intercepted for validation failures
    cy.intercept('POST', '/api/v1/bulk-operations/import/*', {
      statusCode: 400,
      body: {
        success: false,
        error: 'Invalid file format',
        errors: ['The file format is not supported. Please use CSV or Excel files.']
      }
    }).as('failedValidation');

    // Visit bulk operations page
    cy.visit('/bulk-operations');
  });

  it('displays the bulk operations page with stepper and templates', () => {
    // Check the main title
    cy.contains('Bulk Operations').should('be.visible');
    
    // Check stepper is visible
    cy.contains('Select Template').should('be.visible');
    cy.contains('Upload File').should('be.visible');
    cy.contains('Validation').should('be.visible');
    cy.contains('Results').should('be.visible');
    
    // Wait for templates to load
    cy.wait('@getTemplates');
    
    // Check templates are displayed
    cy.contains('Orders Import').should('be.visible');
    cy.contains('Products Import').should('be.visible');
    cy.contains('Customers Import').should('be.visible');
    
    // Verify template descriptions
    cy.contains('Import order data with customer and product information').should('be.visible');
    cy.contains('Import product catalog data').should('be.visible');
    cy.contains('Import customer information in bulk').should('be.visible');
  });

  it('allows downloading a template file', () => {
    cy.wait('@getTemplates');
    
    // Find and click download button for Orders template
    cy.contains('Orders Import')
      .parent()
      .find('button')
      .contains('Template')
      .click();
    
    // Verify download request was made
    cy.wait('@downloadTemplate');
  });

  it('navigates through basic workflow steps', () => {
    cy.wait('@getTemplates');
    
    // Verify templates page shows
    cy.contains('Select Template').should('be.visible');
    
    // Step 1: Select a template
    cy.contains('Orders Import').click();
    cy.wait('@getTemplateInfo');
    
    // Check that Next button appears and we can go to next step
    cy.contains('Next: Upload File').should('be.visible');
    cy.contains('Next: Upload File').click();
    
    // Step 2: Verify file upload screen
    cy.contains('Upload Orders Import File').should('be.visible');
  });

  it('handles file selection', () => {
    cy.wait('@getTemplates');
    
    // Select template
    cy.contains('Orders Import').click();
    cy.wait('@getTemplateInfo');
    cy.contains('Next: Upload File').click();
    
    // Verify file upload screen shows
    cy.contains('Upload Orders Import File').should('be.visible');
    
    // Simply check that the file input exists and is functional
    cy.get('input[type="file"]').should('exist');
  });

  it('handles server errors gracefully', () => {
    // Mock server error
    cy.intercept('GET', '/api/v1/bulk-operations/templates/', {
      statusCode: 500,
      body: {
        success: false,
        error: 'Internal Server Error'
      }
    }).as('serverError');
    
    // Reload page to trigger the error
    cy.reload();
    
    // Wait for error response
    cy.wait('@serverError');
    
    // Should display error message
    cy.contains('Internal Server Error').should('be.visible');
  });
  
  it('verifies basic page structure exists', () => {
    cy.wait('@getTemplates');
    
    // Verify that the main components of the page are present
    cy.contains('Bulk Operations').should('be.visible');
    cy.contains('Select Template').should('be.visible');
    
    // Check that templates are displayed
    cy.contains('Orders Import').should('be.visible');
    cy.contains('Products Import').should('be.visible');
    
    // Check Step component exists
    cy.get('.MuiStepper-root').should('exist');
    cy.get('.MuiStep-root').should('have.length', 4);
  });
});