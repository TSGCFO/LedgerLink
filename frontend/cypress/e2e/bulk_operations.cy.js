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

  it('navigates through bulk import workflow', () => {
    cy.wait('@getTemplates');
    
    // Step 1: Select a template
    cy.contains('Orders Import').click();
    cy.wait('@getTemplateInfo');
    
    // Check that Next button appears
    cy.contains('Next: Upload File').should('be.visible');
    cy.contains('Next: Upload File').click();
    
    // Step 2: File upload screen
    cy.contains('Upload Orders Import File').should('be.visible');
    
    // Verify field requirements table
    cy.contains('Field Requirements').should('be.visible');
    cy.contains('Field Name').should('be.visible');
    cy.contains('Required').should('be.visible');
    cy.contains('id').should('be.visible');
    cy.contains('name').should('be.visible');
    cy.contains('quantity').should('be.visible');
    
    // Upload a test file
    cy.get('input[type="file"]').selectFile({
      contents: Cypress.Buffer.from('id,name,quantity,price,date\n1,Test Product,5,10.99,2023-01-01'),
      fileName: 'test_import.csv',
      mimeType: 'text/csv'
    }, { force: true });
    
    // Should move to validation step
    cy.wait('@importValidation');
    
    // Step 3: Validation progress
    cy.contains('File Validation').should('be.visible');
    
    // Validation should complete and show results 
    cy.contains('Import Results', { timeout: 10000 }).should('be.visible');
    
    // Step 4: Results
    cy.contains('Import Completed with Errors').should('be.visible');
    cy.contains('Total Rows').should('be.visible');
    cy.contains('10').should('be.visible');
    cy.contains('Successful').should('be.visible');
    cy.contains('8').should('be.visible');
    cy.contains('Failed').should('be.visible');
    cy.contains('2').should('be.visible');
    
    // Check error details
    cy.contains('Row 3').should('be.visible');
    cy.contains('price: Must be a positive number').should('be.visible');
    
    // Should have retry button
    cy.contains('Upload Another File').should('be.visible');
  });

  it('handles validation failures', () => {
    // Override the import validation response for this test
    cy.intercept('POST', '/api/v1/bulk-operations/import/orders/', {
      statusCode: 400,
      body: {
        success: false,
        error: 'Invalid file format',
        errors: ['The file format is not supported. Please use CSV or Excel files.']
      }
    }).as('failedValidation');
    
    cy.wait('@getTemplates');
    
    // Select template
    cy.contains('Orders Import').click();
    cy.wait('@getTemplateInfo');
    cy.contains('Next: Upload File').click();
    
    // Upload an invalid file
    cy.get('input[type="file"]').selectFile({
      contents: Cypress.Buffer.from('Invalid content'),
      fileName: 'invalid.txt',
      mimeType: 'text/plain'
    }, { force: true });
    
    // Wait for validation to fail
    cy.wait('@failedValidation');
    
    // Should show error message
    cy.contains('Invalid file format').should('be.visible');
    cy.contains('The file format is not supported').should('be.visible');
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
  
  it('checks accessibility on all workflow steps', () => {
    // Check initial page accessibility
    cy.injectAxe();
    cy.checkA11y();
    
    cy.wait('@getTemplates');
    
    // Step 1: Select template and check accessibility
    cy.contains('Orders Import').click();
    cy.wait('@getTemplateInfo');
    cy.checkA11y();
    
    // Step 2: Check file upload screen accessibility
    cy.contains('Next: Upload File').click();
    cy.checkA11y();
    
    // Step 3-4: Check validation and results accessibility
    cy.get('input[type="file"]').selectFile({
      contents: Cypress.Buffer.from('id,name,quantity,price,date\n1,Test Product,5,10.99,2023-01-01'),
      fileName: 'test_import.csv',
      mimeType: 'text/csv'
    }, { force: true });
    
    cy.wait('@importValidation');
    cy.contains('Import Results', { timeout: 10000 }).should('be.visible');
    cy.checkA11y();
  });
});