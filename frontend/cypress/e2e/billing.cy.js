/// <reference types="cypress" />
import 'cypress-axe';
import { format } from 'date-fns';

/**
 * Comprehensive E2E tests for the Billing module
 * These tests cover the full billing workflow including report generation,
 * viewing saved reports, export functionality, error handling, and accessibility.
 */
describe('Billing Module - Full Workflow', () => {
  /** 
   * Common baseline mocks for authentication and data
   */
  beforeEach(() => {
    // Use the login command
    cy.login('admin', 'adminpassword');

    // Intercept and mock API requests
    setupApiInterceptions();
  });

  /**
   * Billing List Page Tests
   */
  describe('Billing List Page', () => {
    it('loads the billing list page with all elements', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      
      // Check page structure and elements
      cy.contains('h1', 'Billing Reports').should('be.visible');
      cy.contains('Generate Billing Report').should('be.visible');
      cy.contains('label', 'Customer').should('be.visible');
      cy.contains('label', 'Start Date').should('be.visible');
      cy.contains('label', 'End Date').should('be.visible');
      cy.get('button').contains('Calculate').should('be.visible');
      cy.contains('h2', 'Saved Reports').should('be.visible');
      
      // Visual check and accessibility check
      cy.screenshot('billing-list-page');
      cy.checkPageA11y();
    });
    
    it('validates form fields with appropriate error messages', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      
      // Empty form submission
      cy.get('button').contains('Calculate').click();
      cy.contains('Please select a customer and date range').should('be.visible');
      
      // Select customer but no dates
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      cy.get('button').contains('Calculate').click();
      cy.contains('Please select a date range').should('be.visible');
      
      // Select customer and start date only
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('button').contains('Calculate').click();
      cy.contains('Please select an end date').should('be.visible');
      
      // Select customer and end date only (clear start date first)
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().clear();
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      cy.get('button').contains('Calculate').click();
      cy.contains('Please select a start date').should('be.visible');
      
      // Invalid date range (end date before start date)
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('03/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().clear().type('02/01/2025');
      cy.get('button').contains('Calculate').click();
      cy.contains('End date must be after start date').should('be.visible');
      
      // Dates too far apart
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().clear().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().clear().type('01/01/2026'); // 1 year apart
      cy.get('button').contains('Calculate').click();
      cy.contains('Date range cannot exceed').should('be.visible');
      
      // Ensure validation errors don't impact accessibility
      cy.checkPageA11y();
    });
    
    it('successfully generates and displays a billing report', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      
      // Complete the form with valid data
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      
      const startDate = format(new Date(2025, 0, 1), 'MM/dd/yyyy'); // Jan 1, 2025
      const endDate = format(new Date(2025, 1, 1), 'MM/dd/yyyy');   // Feb 1, 2025
      
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type(startDate);
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type(endDate);
      
      // Submit the form
      cy.get('button').contains('Calculate').click();
      cy.wait('@generateReport');
      
      // Verify table is displayed with correct data
      cy.get('.MuiTable-root').should('be.visible');
      cy.contains('Order ID').should('be.visible');
      cy.contains('Total Amount').should('be.visible');
      cy.contains('Standard Shipping').should('be.visible');
      cy.contains('Packaging').should('be.visible');
      cy.contains('Pick Cost').should('be.visible');
      
      // Check data rows
      cy.contains('ORD-001').should('be.visible');
      cy.contains('$150.00').should('be.visible');
      cy.contains('$25.00').should('be.visible');
      
      // Check totals in footer
      cy.get('tfoot').should('contain', '$225.00');
      cy.get('tfoot').should('contain', '$40.00');
      
      // Ensure table is accessible
      cy.checkPageA11y();
    });
    
    it('displays and manages saved reports', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      cy.wait('@getBillingReports');
      
      // Verify saved reports section
      cy.contains('h2', 'Saved Reports').should('be.visible');
      cy.get('[data-testid="saved-reports-section"]').within(() => {
        cy.contains('Test Company').should('be.visible');
        cy.contains('Jan 1, 2025 - Feb 1, 2025').should('be.visible');
        cy.contains('$1,500.00').should('be.visible');
        cy.contains('button', 'View').should('be.visible');
        cy.contains('button', 'Delete').should('be.visible');
      });
      
      // Test viewing a saved report
      cy.contains('button', 'View').first().click();
      cy.wait('@getSavedReport');
      cy.wait('@generateReport');
      
      // Verify table displays with the loaded report data
      cy.get('.MuiTable-root').should('be.visible');
      cy.contains('ORD-001').should('be.visible');
      
      // Test deleting a report
      cy.contains('button', 'Delete').first().click();
      cy.contains('Are you sure you want to delete this report?').should('be.visible');
      
      // Cancel deletion
      cy.contains('button', 'Cancel').click();
      cy.contains('Are you sure').should('not.exist');
      
      // Confirm deletion
      cy.contains('button', 'Delete').first().click();
      cy.contains('button', 'Confirm').click();
      cy.wait('@deleteReport');
      
      // Verify success message
      cy.contains('Report deleted successfully').should('be.visible');
      
      // Verify reports list is refreshed
      cy.wait('@getBillingReports');
    });
    
    it('filters saved reports', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      cy.wait('@getBillingReports');
      
      // Test search functionality
      cy.get('input[placeholder*="Search reports"]').type('Test Company');
      cy.wait('@searchBillingReports');
      
      // Verify filtered results
      cy.contains('Test Company').should('be.visible');
      cy.contains('Another Company').should('not.exist');
      
      // Clear search
      cy.get('input[placeholder*="Search reports"]').clear();
      cy.wait('@getBillingReports');
      
      // Both companies should be visible now
      cy.contains('Test Company').should('be.visible');
      cy.contains('Another Company').should('be.visible');
    });
    
    it('handles API errors gracefully', () => {
      // Override the interceptors to return errors
      cy.intercept('POST', '/api/v1/billing/api/generate-report/', {
        statusCode: 500,
        body: {
          detail: 'Server error occurred while generating report'
        }
      }).as('generateReportError');
      
      cy.visit('/billing');
      cy.wait('@getCustomers');
      
      // Fill form and submit
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      cy.get('button').contains('Calculate').click();
      
      cy.wait('@generateReportError');
      
      // Verify error is displayed
      cy.contains('Server error occurred').should('be.visible');
      
      // Error message should be accessible
      cy.checkPageA11y();
    });
    
    it('displays correct message for empty report results', () => {
      // Override the report generator to return empty results
      cy.intercept('POST', '/api/v1/billing/api/generate-report/', {
        statusCode: 200,
        body: {
          customer_name: 'Test Company',
          start_date: '2025-01-01',
          end_date: '2025-02-01',
          total_amount: 0,
          preview_data: {
            orders: []
          },
          service_totals: {}
        }
      }).as('emptyReport');
      
      cy.visit('/billing');
      cy.wait('@getCustomers');
      
      // Fill form and submit
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      cy.get('button').contains('Calculate').click();
      
      cy.wait('@emptyReport');
      
      // Verify empty state message
      cy.contains('No billing data found for the selected criteria').should('be.visible');
    });
  });
  
  /**
   * Billing Form Page Tests
   */
  describe('Billing Form Page', () => {
    it('loads the billing form page with all elements', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Check page structure and elements
      cy.contains('h1', 'Generate Billing Report').should('be.visible');
      cy.contains('label', 'Customer').should('be.visible');
      cy.contains('label', 'Start Date').should('be.visible');
      cy.contains('label', 'End Date').should('be.visible');
      cy.contains('label', 'Export Format').should('be.visible');
      cy.get('button').contains('Generate Report').should('be.visible');
      
      // Visual check and accessibility check
      cy.screenshot('billing-form-page');
      cy.checkPageA11y();
    });
    
    it('validates form fields with appropriate error messages', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Empty form submission
      cy.get('button').contains('Generate Report').click();
      cy.contains('Customer is required').should('be.visible');
      cy.contains('Start date is required').should('be.visible');
      cy.contains('End date is required').should('be.visible');
      
      // Select customer but no dates
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      cy.get('button').contains('Generate Report').click();
      cy.contains('Start date is required').should('be.visible');
      cy.contains('End date is required').should('be.visible');
      
      // Invalid date range (end date before start date)
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('03/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      cy.get('button').contains('Generate Report').click();
      cy.contains('End date must be after start date').should('be.visible');
      
      // Ensure validation errors don't impact accessibility
      cy.checkPageA11y();
    });
    
    it('generates a preview report and shows the preview dialog', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Complete the form with valid data
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      
      // Select "Preview" format
      cy.get('[aria-labelledby*="export-format"]').click();
      cy.get('[role="option"]').contains('Preview').click();
      
      // Submit the form
      cy.get('button').contains('Generate Report').click();
      cy.wait('@generatePreviewReport');
      
      // Verify preview dialog is shown
      cy.contains('Report Preview').should('be.visible');
      cy.contains('Order ID').should('be.visible');
      cy.contains('ORD-001').should('be.visible');
      cy.contains('ORD-002').should('be.visible');
      cy.contains('Transaction Date').should('be.visible');
      cy.contains('Status').should('be.visible');
      cy.contains('Ship To').should('be.visible');
      cy.contains('Amount').should('be.visible');
      
      // Verify service summary section
      cy.contains('Service Summary').should('be.visible');
      cy.contains('Standard Shipping').should('be.visible');
      cy.contains('$40.00').should('be.visible');
      cy.contains('Packaging').should('be.visible');
      cy.contains('$25.00').should('be.visible');
      
      // Test dialog actions
      cy.contains('button', 'Export as Excel').should('be.visible');
      cy.contains('button', 'Export as PDF').should('be.visible');
      cy.contains('button', 'Close').should('be.visible');
      
      // Check accessibility of dialog
      cy.checkPageA11y();
      
      // Close the dialog
      cy.contains('button', 'Close').click();
      cy.contains('Report Preview').should('not.exist');
    });
    
    it('exports a report as Excel format', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Complete the form with valid data
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      
      // Select "Excel" format
      cy.get('[aria-labelledby*="export-format"]').click();
      cy.get('[role="option"]').contains('Excel').click();
      
      // Setup download interception
      cy.intercept('POST', '/api/v1/billing/api/generate-report/*', {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'Content-Disposition': 'attachment; filename="billing_report.xlsx"'
        },
        body: Cypress.Buffer.from('Mock Excel file content')
      }).as('downloadExcel');
      
      // Submit the form
      cy.get('button').contains('Generate Report').click();
      cy.wait('@downloadExcel');
      
      // Verify success message (since we can't verify the actual download in Cypress)
      cy.contains('Report generated successfully').should('be.visible');
    });
    
    it('exports a report as PDF format', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Complete the form with valid data
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      
      // Select "PDF" format
      cy.get('[aria-labelledby*="export-format"]').click();
      cy.get('[role="option"]').contains('PDF').click();
      
      // Setup download interception
      cy.intercept('POST', '/api/v1/billing/api/generate-report/*', {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': 'attachment; filename="billing_report.pdf"'
        },
        body: Cypress.Buffer.from('Mock PDF file content')
      }).as('downloadPDF');
      
      // Submit the form
      cy.get('button').contains('Generate Report').click();
      cy.wait('@downloadPDF');
      
      // Verify success message
      cy.contains('Report generated successfully').should('be.visible');
    });
    
    it('handles API errors during report generation', () => {
      // Override the report generator to return an error
      cy.intercept('POST', '/api/v1/billing/api/generate-report/*', {
        statusCode: 500,
        body: {
          detail: 'Failed to generate report: internal server error'
        }
      }).as('generateReportError');
      
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Complete the form with valid data
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      
      // Submit the form
      cy.get('button').contains('Generate Report').click();
      cy.wait('@generateReportError');
      
      // Verify error message
      cy.contains('Failed to generate report: internal server error').should('be.visible');
      
      // Verify error doesn't break accessibility
      cy.checkPageA11y();
    });
    
    it('edits an existing billing report', () => {
      // Visit the edit page for an existing report
      cy.visit('/billing/123/edit');
      cy.wait('@getCustomers');
      cy.wait('@getReportDetails');
      
      // Verify report details are loaded
      cy.contains('Report Summary').should('be.visible');
      cy.contains('Total Amount:').should('be.visible');
      cy.contains('$1,500.00').should('be.visible');
      cy.contains('Generated:').should('be.visible');
      
      // Verify form is pre-filled
      cy.get('[aria-labelledby*="customer"]').should('contain', 'Test Company');
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().should('have.value', '01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().should('have.value', '02/01/2025');
      
      // Change export format
      cy.get('[aria-labelledby*="export-format"]').click();
      cy.get('[role="option"]').contains('Excel').click();
      
      // Re-generate report
      cy.intercept('POST', '/api/v1/billing/api/generate-report/*', {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'Content-Disposition': 'attachment; filename="billing_report.xlsx"'
        },
        body: Cypress.Buffer.from('Mock Excel file content')
      }).as('regenerateReport');
      
      cy.get('button').contains('Regenerate Report').click();
      cy.wait('@regenerateReport');
      
      // Verify success message
      cy.contains('Report regenerated successfully').should('be.visible');
    });
    
    it('exports from the preview dialog', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      
      // Complete the form with valid data
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      
      // Select "Preview" format
      cy.get('[aria-labelledby*="export-format"]').click();
      cy.get('[role="option"]').contains('Preview').click();
      
      // Submit the form
      cy.get('button').contains('Generate Report').click();
      cy.wait('@generatePreviewReport');
      
      // Verify preview dialog is shown
      cy.contains('Report Preview').should('be.visible');
      
      // Setup download interception for PDF
      cy.intercept('POST', '/api/v1/billing/api/generate-report/*', {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': 'attachment; filename="billing_report.pdf"'
        },
        body: Cypress.Buffer.from('Mock PDF file content')
      }).as('downloadPDF');
      
      // Click the PDF export button
      cy.contains('button', 'Export as PDF').click();
      cy.wait('@downloadPDF');
      
      // Verify the dialog stays open
      cy.contains('Report Preview').should('be.visible');
      
      // Setup download interception for Excel
      cy.intercept('POST', '/api/v1/billing/api/generate-report/*', {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'Content-Disposition': 'attachment; filename="billing_report.xlsx"'
        },
        body: Cypress.Buffer.from('Mock Excel file content')
      }).as('downloadExcel');
      
      // Click the Excel export button
      cy.contains('button', 'Export as Excel').click();
      cy.wait('@downloadExcel');
      
      // Close the dialog
      cy.contains('button', 'Close').click();
      cy.contains('Report Preview').should('not.exist');
    });
  });
  
  /**
   * Nested Cypress A11y Tests for Billing Module
   */
  describe('Billing Module Accessibility Tests', () => {
    it('billing list page maintains accessibility standards', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      cy.injectAxe();
      
      // Test overall page
      cy.checkA11y();
      
      // Test with form filled
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      cy.checkA11y();
      
      // Test with data loaded
      cy.get('button').contains('Calculate').click();
      cy.wait('@generateReport');
      cy.checkA11y();
      
      // Test with error message
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().clear().type('03/01/2025');
      cy.get('button').contains('Calculate').click();
      cy.checkA11y();
    });
    
    it('billing form page maintains accessibility standards', () => {
      cy.visit('/billing/new');
      cy.wait('@getCustomers');
      cy.injectAxe();
      
      // Test overall page
      cy.checkA11y();
      
      // Test with validation errors
      cy.get('button').contains('Generate Report').click();
      cy.checkA11y();
      
      // Test with form filled
      cy.get('[aria-labelledby*="customer"]').click();
      cy.get('[role="option"]').contains('Test Company').click();
      cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
      cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
      cy.checkA11y();
      
      // Test dialog
      cy.get('[aria-labelledby*="export-format"]').click();
      cy.get('[role="option"]').contains('Preview').click();
      cy.get('button').contains('Generate Report').click();
      cy.wait('@generatePreviewReport');
      cy.checkA11y();
    });
    
    it('handles keyboard navigation correctly', () => {
      cy.visit('/billing');
      cy.wait('@getCustomers');
      
      // Tab through elements on the page and verify focus
      cy.get('body').tab();  // First focusable element
      cy.focused().should('exist');
      cy.focused().tab();    // Next element
      cy.focused().should('exist');
      
      // Tab to the customer dropdown
      let found = false;
      for (let i = 0; i < 10; i++) {
        cy.focused().then($el => {
          const label = $el.attr('aria-labelledby');
          if (label && label.includes('customer')) {
            found = true;
          }
          if (!found) {
            cy.focused().tab();
          }
        });
      }
      
      // Activate dropdown with keyboard
      cy.focused().type('{enter}');
      cy.get('[role="option"]').should('be.visible');
      
      // Use arrows to navigate options
      cy.focused().type('{downarrow}');
      cy.focused().type('{enter}');
      
      // Continue tabbing to date fields
      cy.focused().tab();
      cy.focused().should('have.attr', 'placeholder').and('include', 'MM/DD/YYYY');
      
      // Test date field keyboard usage
      cy.focused().type('01012025');
      
      // Tab to calculate button
      let buttonFound = false;
      for (let i = 0; i < 10; i++) {
        cy.focused().then($el => {
          if ($el.text().includes('Calculate')) {
            buttonFound = true;
          }
          if (!buttonFound && i < 9) {
            cy.focused().tab();
          }
        });
      }
      
      // Activate button with keyboard
      cy.focused().type('{enter}');
      cy.contains('Please select a date range').should('be.visible');
    });
  });
  
  /**
   * Billing Module Mobile Responsiveness Tests
   */
  describe('Billing Module Mobile Responsiveness', () => {
    const sizes = [
      {viewportWidth: 375, viewportHeight: 667, size: 'mobile'},    // iPhone SE
      {viewportWidth: 768, viewportHeight: 1024, size: 'tablet'},   // iPad
      {viewportWidth: 1280, viewportHeight: 800, size: 'desktop'}   // Desktop
    ];
    
    sizes.forEach((size) => {
      it(`displays correctly on ${size.size} screens`, () => {
        cy.viewport(size.viewportWidth, size.viewportHeight);
        
        // Test billing list page
        cy.visit('/billing');
        cy.wait('@getCustomers');
        cy.screenshot(`billing-list-${size.size}`);
        
        // Fill and submit form
        cy.get('[aria-labelledby*="customer"]').click();
        cy.get('[role="option"]').contains('Test Company').click();
        cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
        cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
        cy.get('button').contains('Calculate').click();
        cy.wait('@generateReport');
        
        // Verify table is visible and properly formatted
        cy.get('.MuiTable-root').should('be.visible');
        cy.screenshot(`billing-table-${size.size}`);
        
        // Test billing form page
        cy.visit('/billing/new');
        cy.wait('@getCustomers');
        cy.screenshot(`billing-form-${size.size}`);
        
        // Test preview dialog
        cy.get('[aria-labelledby*="customer"]').click();
        cy.get('[role="option"]').contains('Test Company').click();
        cy.get('input[placeholder*="MM/DD/YYYY"]').first().type('01/01/2025');
        cy.get('input[placeholder*="MM/DD/YYYY"]').last().type('02/01/2025');
        cy.get('[aria-labelledby*="export-format"]').click();
        cy.get('[role="option"]').contains('Preview').click();
        cy.get('button').contains('Generate Report').click();
        cy.wait('@generatePreviewReport');
        
        cy.contains('Report Preview').should('be.visible');
        cy.screenshot(`billing-preview-${size.size}`);
      });
    });
  });
});

/**
 * This function sets up all the API interceptions needed for the billing tests
 */
function setupApiInterceptions() {
  // Intercept customer API
  cy.intercept('GET', '/api/v1/customers*', {
    statusCode: 200,
    body: {
      results: [
        { id: 1, company_name: 'Test Company' },
        { id: 2, company_name: 'Another Company' }
      ]
    }
  }).as('getCustomers');
  
  // Saved reports listing
  cy.intercept('GET', '/api/v1/billing/reports*', {
    statusCode: 200,
    body: {
      results: [
        {
          id: '123',
          customer: 1,
          customer_name: 'Test Company',
          start_date: '2025-01-01',
          end_date: '2025-02-01',
          total_amount: 1500.00,
          generated_at: '2025-01-15T10:30:00Z'
        },
        {
          id: '456',
          customer: 2,
          customer_name: 'Another Company',
          start_date: '2025-02-01',
          end_date: '2025-03-01',
          total_amount: 2500.00,
          generated_at: '2025-02-15T10:30:00Z'
        }
      ]
    }
  }).as('getBillingReports');
  
  // Search reports
  cy.intercept('GET', '/api/v1/billing/reports*search=*', {
    statusCode: 200,
    body: {
      results: [
        {
          id: '123',
          customer: 1,
          customer_name: 'Test Company',
          start_date: '2025-01-01',
          end_date: '2025-02-01',
          total_amount: 1500.00,
          generated_at: '2025-01-15T10:30:00Z'
        }
      ]
    }
  }).as('searchBillingReports');
  
  // Get single report details
  cy.intercept('GET', '/api/v1/billing/reports/*', {
    statusCode: 200,
    body: {
      id: '123',
      customer: 1,
      customer_name: 'Test Company',
      start_date: '2025-01-01',
      end_date: '2025-02-01',
      total_amount: 1500.00,
      generated_at: '2025-01-15T10:30:00Z'
    }
  }).as('getReportDetails');
  
  // Mock normal billing report data
  cy.intercept('POST', '/api/v1/billing/reports/generate*', {
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
              { service_id: 1, service_name: 'Standard Shipping', amount: 25.00 },
              { service_id: 2, service_name: 'Packaging', amount: 15.00 },
              { service_id: 3, service_name: 'Pick Cost', amount: 10.00 }
            ],
            total_amount: 150.00
          },
          {
            order_id: 'ORD-002',
            transaction_date: '2025-01-20',
            status: 'Completed',
            ship_to_name: 'Jane Smith',
            ship_to_address: '456 Test Ave',
            total_items: 3,
            line_items: 1,
            weight_lb: 5,
            services: [
              { service_id: 1, service_name: 'Standard Shipping', amount: 15.00 },
              { service_id: 2, service_name: 'Packaging', amount: 10.00 },
              { service_id: 3, service_name: 'Pick Cost', amount: 5.00 }
            ],
            total_amount: 75.00
          }
        ]
      },
      service_totals: {
        1: { name: 'Standard Shipping', amount: 40.00, order_count: 2 },
        2: { name: 'Packaging', amount: 25.00, order_count: 2 },
        3: { name: 'Pick Cost', amount: 15.00, order_count: 2 }
      }
    }
  }).as('generateReport');
  
  // Mock preview billing report data (more detailed for preview)
  cy.intercept('POST', '/api/v1/billing/reports/generate*preview*', {
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
              { service_id: 1, service_name: 'Standard Shipping', amount: 25.00 },
              { service_id: 2, service_name: 'Packaging', amount: 15.00 },
              { service_id: 3, service_name: 'Pick Cost', amount: 10.00 }
            ],
            total_amount: 150.00
          },
          {
            order_id: 'ORD-002',
            transaction_date: '2025-01-20',
            status: 'Completed',
            ship_to_name: 'Jane Smith',
            ship_to_address: '456 Test Ave',
            total_items: 3,
            line_items: 1,
            weight_lb: 5,
            services: [
              { service_id: 1, service_name: 'Standard Shipping', amount: 15.00 },
              { service_id: 2, service_name: 'Packaging', amount: 10.00 },
              { service_id: 3, service_name: 'Pick Cost', amount: 5.00 }
            ],
            total_amount: 75.00
          }
        ]
      },
      service_totals: {
        1: { name: 'Standard Shipping', amount: 40.00, order_count: 2 },
        2: { name: 'Packaging', amount: 25.00, order_count: 2 },
        3: { name: 'Pick Cost', amount: 15.00, order_count: 2 }
      }
    }
  }).as('generatePreviewReport');
  
  // Delete billing report
  cy.intercept('DELETE', '/api/v1/billing/reports/*', {
    statusCode: 204
  }).as('deleteReport');
  
  // Get saved report for viewing
  cy.intercept('GET', '/api/v1/billing/reports/*/view', {
    statusCode: 200,
    body: {
      id: '123',
      customer: 1,
      customer_name: 'Test Company',
      start_date: '2025-01-01',
      end_date: '2025-02-01',
      report_id: 'REP-123'
    }
  }).as('getSavedReport');
}

// Add the cypress-plugin-tab command to help with keyboard navigation testing
Cypress.Commands.add('tab', { prevSubject: 'optional' }, (subject) => {
  const tabKey = { keyCode: 9, which: 9, code: 'Tab', key: 'Tab' };
  
  if (subject) {
    cy.wrap(subject).trigger('keydown', tabKey);
  } else {
    cy.focused().trigger('keydown', tabKey);
  }
  
  return cy.document().trigger('keydown', tabKey);
});