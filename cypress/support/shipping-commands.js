// ***********************************************
// Custom shipping commands for LedgerLink application
// ***********************************************

// Command to create a CAD shipping record
Cypress.Commands.add('createCADShipping', (orderData = {}, shippingData = {}) => {
  // Create an order first if one wasn't provided
  const createOrderPromise = orderData.id 
    ? cy.wrap(orderData) 
    : cy.createOrder();

  return createOrderPromise.then(order => {
    // Default shipping data
    const defaultData = {
      transaction: order.id,
      customer: order.customer_id,
      ship_to_name: 'Test Recipient',
      ship_to_address_1: '123 Test St',
      ship_to_city: 'Test City',
      ship_to_state: 'TS',
      ship_to_postal_code: 'A1B 2C3',
      carrier: 'Canada Post',
      tracking_number: `CAD-TEST-${Date.now().toString()}`,
      pre_tax_shipping_charge: '15.99',
      tax1type: 'GST',
      tax1amount: '0.80'
    };
    
    const data = { ...defaultData, ...shippingData };
    
    // Create shipping record via API
    cy.request({
      method: 'POST',
      url: `${Cypress.env('apiUrl')}/shipping/cad/`,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data
    }).then((response) => {
      expect(response.status).to.eq(201);
      cy.log(`Created CAD shipping record ${response.body.data.transaction}`);
      return cy.wrap(response.body.data);
    });
  });
});

// Command to create a US shipping record
Cypress.Commands.add('createUSShipping', (orderData = {}, shippingData = {}) => {
  // Create an order first if one wasn't provided
  const createOrderPromise = orderData.id 
    ? cy.wrap(orderData) 
    : cy.createOrder();

  return createOrderPromise.then(order => {
    // Default shipping data
    const defaultData = {
      transaction: order.id,
      customer: order.customer_id,
      ship_to_name: 'US Test Recipient',
      ship_to_address_1: '456 Test Ave',
      ship_to_city: 'Test City',
      ship_to_state: 'NY',
      ship_to_zip: '12345',
      service_name: 'Express',
      tracking_number: `US-TEST-${Date.now().toString()}`,
      current_status: 'in_transit',
      delivery_status: 'pending',
      ship_date: new Date().toISOString().split('T')[0]
    };
    
    const data = { ...defaultData, ...shippingData };
    
    // Create shipping record via API
    cy.request({
      method: 'POST',
      url: `${Cypress.env('apiUrl')}/shipping/us/`,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data
    }).then((response) => {
      expect(response.status).to.eq(201);
      cy.log(`Created US shipping record ${response.body.data.transaction}`);
      return cy.wrap(response.body.data);
    });
  });
});

// Command to import shipping records
Cypress.Commands.add('importShippingRecords', (shippingType = 'cad_shipping', fileName = 'cad_shipping_sample.csv') => {
  cy.visit('/bulk-operations');
  
  // Select shipping template type
  cy.get('[data-testid="template-type"]').select(shippingType);
  
  // Upload CSV file
  cy.fixture(fileName).then(fileContent => {
    cy.get('[data-testid="file-upload"]').attachFile({
      fileContent: fileContent.toString(),
      fileName: fileName,
      mimeType: 'text/csv'
    });
  });
  
  // Submit import
  cy.get('[data-testid="import-button"]').click();
  
  // Wait for import to complete and return results
  cy.get('[data-testid="import-result"]', { timeout: 10000 }).should('exist');
  
  return cy.get('[data-testid="import-summary"]').then($summary => {
    const successfulCount = parseInt($summary.find('[data-testid="successful-count"]').text());
    const failedCount = parseInt($summary.find('[data-testid="failed-count"]').text());
    const totalCount = parseInt($summary.find('[data-testid="total-count"]').text());
    
    return cy.wrap({
      successful: successfulCount,
      failed: failedCount,
      total: totalCount
    });
  });
});

// Command to verify shipping analytics
Cypress.Commands.add('verifyShippingAnalytics', () => {
  cy.visit('/shipping/analytics');
  
  // Verify main components exist
  cy.get('[data-testid="shipping-analytics"]').should('exist');
  cy.get('[data-testid="delivery-time-chart"]').should('exist');
  cy.get('[data-testid="carrier-performance-chart"]').should('exist');
  
  // Set date range for last 3 months
  const endDate = new Date();
  const startDate = new Date();
  startDate.setMonth(startDate.getMonth() - 3);
  
  cy.get('[data-testid="start-date-input"]').type(startDate.toISOString().split('T')[0]);
  cy.get('[data-testid="end-date-input"]').type(endDate.toISOString().split('T')[0]);
  cy.get('[data-testid="apply-filter-button"]').click();
  
  // Wait for charts to update
  cy.get('[data-testid="analytics-loading"]').should('not.exist');
  
  // Return analytics data
  return cy.get('[data-testid="analytics-summary"]').then($summary => {
    const avgDeliveryDays = parseFloat($summary.find('[data-testid="avg-delivery-days"]').text());
    const onTimePercentage = parseFloat($summary.find('[data-testid="on-time-percentage"]').text());
    
    return cy.wrap({
      avgDeliveryDays,
      onTimePercentage
    });
  });
});