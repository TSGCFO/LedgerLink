/**
 * End-to-end tests for the Rules Management functionality
 */
describe('Rules Management', () => {
  beforeEach(() => {
    // Login before running tests
    cy.login();
    
    // Intercept API calls for rules
    cy.intercept('GET', '/api/v1/rules/api/groups/**').as('getRuleGroups');
    cy.intercept('GET', '/api/v1/rules/fields/').as('getFields');
    cy.intercept('GET', '/api/v1/rules/operators/').as('getOperators');
    cy.intercept('GET', '/api/v1/rules/calculation-types/').as('getCalculationTypes');
    cy.intercept('POST', '/api/v1/rules/**').as('createRule');
    cy.intercept('PUT', '/api/v1/rules/**').as('updateRule');
    cy.intercept('DELETE', '/api/v1/rules/**').as('deleteRule');
  });
  
  it('should display the rules dashboard', () => {
    cy.visit('/rules');
    cy.wait('@getRuleGroups');
    
    // Verify page elements
    cy.contains('h1', 'Rules Management').should('be.visible');
    cy.contains('Basic Rules').should('be.visible');
    cy.contains('Advanced Rules').should('be.visible');
    cy.contains('button', 'Create Rule Group').should('be.visible');
  });
  
  it('should navigate to rule groups management', () => {
    cy.visit('/rules');
    cy.wait('@getRuleGroups');
    
    // Click on the rule groups tab
    cy.contains('Rule Groups').click();
    
    // Verify rule groups content is visible
    cy.contains('Rule Groups List').should('be.visible');
    cy.contains('button', 'Create Rule Group').should('be.visible');
    cy.get('table').should('be.visible');
  });
  
  it('should create a new rule group', () => {
    cy.visit('/rules/groups');
    cy.wait('@getRuleGroups');
    
    // Click create button
    cy.contains('button', 'Create Rule Group').click();
    
    // Form should appear
    cy.get('form').should('be.visible');
    
    // Fill in form
    cy.get('select[name="customer_service"]').select('1'); // Assuming option exists
    cy.get('select[name="logic_operator"]').select('AND');
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Wait for API and check success message
    cy.contains('Rule group created successfully').should('be.visible');
  });
  
  it('should navigate to basic rules list', () => {
    cy.visit('/rules/basic');
    cy.wait('@getRuleGroups');
    
    // Verify basic rules content
    cy.contains('Basic Rules List').should('be.visible');
    cy.contains('button', 'Create Basic Rule').should('be.visible');
  });
  
  it('should create a basic rule', () => {
    cy.visit('/rules/basic/new');
    cy.wait('@getRuleGroups');
    cy.wait('@getFields');
    cy.wait('@getOperators');
    
    // Fill out form
    cy.get('select[name="rule_group"]').select('1'); // Assuming option exists
    cy.get('select[name="field"]').select('weight_lb');
    
    // Wait for operators to load based on field
    cy.wait('@getOperators');
    
    cy.get('select[name="operator"]').select('gt');
    cy.get('input[name="value"]').type('10');
    cy.get('input[name="adjustment_amount"]').type('5.00');
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Wait for API and check success message
    cy.wait('@createRule');
    cy.contains('Rule created successfully').should('be.visible');
  });
  
  it('should navigate to advanced rules list', () => {
    cy.visit('/rules/advanced');
    cy.wait('@getRuleGroups');
    
    // Verify advanced rules content
    cy.contains('Advanced Rules List').should('be.visible');
    cy.contains('button', 'Create Advanced Rule').should('be.visible');
  });
  
  it('should build an advanced rule with conditions', () => {
    cy.visit('/rules/advanced/new');
    cy.wait('@getRuleGroups');
    cy.wait('@getFields');
    cy.wait('@getCalculationTypes');
    
    // Select rule group
    cy.get('select[name="rule_group"]').select('1'); // Assuming option exists
    
    // Add conditions
    cy.contains('button', 'Add Condition').click();
    cy.get('select[name="conditions[0].field"]').select('weight_lb');
    cy.get('select[name="conditions[0].operator"]').select('gt');
    cy.get('input[name="conditions[0].value"]').type('15');
    
    // Add another condition
    cy.contains('button', 'Add Condition').click();
    cy.get('select[name="conditions[1].field"]').select('order_priority');
    cy.get('select[name="conditions[1].operator"]').select('eq');
    cy.get('input[name="conditions[1].value"]').type('High');
    
    // Add calculations
    cy.contains('button', 'Add Calculation').click();
    cy.get('select[name="calculations[0].type"]').select('flat_fee');
    cy.get('input[name="calculations[0].value"]').type('5.00');
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Wait for API and check success message
    cy.wait('@createRule');
    cy.contains('Advanced rule created successfully').should('be.visible');
  });
  
  it('should test a rule with the rule tester', () => {
    cy.visit('/rules/tester');
    cy.wait('@getFields');
    
    // Build test rule
    cy.get('select[name="field"]').select('weight_lb');
    cy.get('select[name="operator"]').select('gt');
    cy.get('input[name="value"]').type('10');
    
    // Add test data
    cy.get('input[name="test_data.weight_lb"]').type('15');
    
    // Run test
    cy.contains('button', 'Test Rule').click();
    
    // Check results
    cy.contains('Rule applies: Yes').should('be.visible');
  });
  
  it('should validate rule form inputs', () => {
    cy.visit('/rules/basic/new');
    cy.wait('@getRuleGroups');
    cy.wait('@getFields');
    
    // Try to submit without filling required fields
    cy.get('button[type="submit"]').click();
    
    // Should show validation errors
    cy.contains('Rule group is required').should('be.visible');
    cy.contains('Field is required').should('be.visible');
    cy.contains('Operator is required').should('be.visible');
    cy.contains('Value is required').should('be.visible');
    
    // Form should not be submitted
    cy.get('@createRule.all').should('have.length', 0);
  });
  
  it('should delete a rule after confirmation', () => {
    cy.visit('/rules/basic');
    cy.wait('@getRuleGroups');
    
    // Mock the confirmation dialog to return true
    cy.on('window:confirm', () => true);
    
    // Click delete button on first rule
    cy.get('button[aria-label="Delete Rule"]').first().click();
    
    // Wait for delete API call
    cy.wait('@deleteRule');
    
    // Should show success message
    cy.contains('Rule deleted successfully').should('be.visible');
  });
  
  it('should cancel rule deletion when confirmation is declined', () => {
    cy.visit('/rules/basic');
    cy.wait('@getRuleGroups');
    
    // Mock the confirmation dialog to return false (cancel)
    cy.on('window:confirm', () => false);
    
    // Click delete button on first rule
    cy.get('button[aria-label="Delete Rule"]').first().click();
    
    // Delete API should not be called
    cy.get('@deleteRule.all').should('have.length', 0);
  });
  
  it('should create a case-based tier advanced rule', () => {
    cy.visit('/rules/advanced/new');
    cy.wait('@getRuleGroups');
    cy.wait('@getFields');
    cy.wait('@getCalculationTypes');
    
    // Select rule group
    cy.get('select[name="rule_group"]').select('1'); // Assuming option exists
    
    // Add condition
    cy.contains('button', 'Add Condition').click();
    cy.get('select[name="conditions[0].field"]').select('quantity');
    cy.get('select[name="conditions[0].operator"]').select('gt');
    cy.get('input[name="conditions[0].value"]').type('0');
    
    // Add case-based tier calculation
    cy.contains('button', 'Add Calculation').click();
    cy.get('select[name="calculations[0].type"]').select('case_based_tier');
    
    // Open tier configuration
    cy.contains('Configure Tiers').click();
    
    // Add first tier
    cy.get('input[name="tier_config.ranges[0].min"]').type('0');
    cy.get('input[name="tier_config.ranges[0].max"]').type('10');
    cy.get('input[name="tier_config.ranges[0].multiplier"]').type('1.0');
    
    // Add second tier
    cy.contains('Add Tier').click();
    cy.get('input[name="tier_config.ranges[1].min"]').type('11');
    cy.get('input[name="tier_config.ranges[1].max"]').type('20');
    cy.get('input[name="tier_config.ranges[1].multiplier"]').type('0.9');
    
    // Save tier configuration
    cy.contains('Save Tiers').click();
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Wait for API and check success message
    cy.wait('@createRule');
    cy.contains('Advanced rule created successfully').should('be.visible');
  });
});