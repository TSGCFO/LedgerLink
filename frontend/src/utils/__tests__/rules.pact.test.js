import { Pact } from '@pact-foundation/pact';
import axios from 'axios';
import { provider, createPaginatedResponse, createResponse } from '../pact-utils';
import apiClient from '../apiClient';

/**
 * @fileoverview API Contract tests for LedgerLink Rules API
 * 
 * These tests verify the contract between the frontend consumer (React) and 
 * backend provider (Django) for the Rules API. They define the expected
 * interaction patterns for:
 * - Rule Groups management (CRUD)
 * - Basic Rules operations
 * - Advanced Rules with complex conditions and calculations
 * - Utility endpoints (fields, operators, etc.)
 * 
 * Each test follows the pattern of:
 * 1. Setting up the expected interaction
 * 2. Making the API call
 * 3. Verifying the response format
 * 4. Confirming contract compliance
 */

// Mock axios for controlled request/response testing
jest.mock('axios');

// Create rule group object patterns for Pact tests
const createRuleGroupObject = (overrides = {}) => {
  return {
    id: Pact.like(1),
    customer_service: Pact.like(1),
    customer_service_details: {
      id: Pact.like(1),
      customer: Pact.like(1),
      customer_name: Pact.like('Test Company'),
      service: Pact.like(1),
      service_name: Pact.like('Test Service')
    },
    logic_operator: Pact.like('AND'),
    is_active: Pact.like(true),
    ...overrides
  };
};

// Create basic rule object patterns for Pact tests
const createRuleObject = (overrides = {}) => {
  return {
    id: Pact.like(1),
    rule_group: Pact.like(1),
    field: Pact.like('weight_lb'),
    operator: Pact.like('gt'),
    value: Pact.like('10'),
    adjustment_amount: Pact.like('5.00'),
    created_at: Pact.like('2025-01-15T10:30:00Z'),
    updated_at: Pact.like('2025-01-15T10:30:00Z'),
    ...overrides
  };
};

// Create advanced rule object patterns for Pact tests
const createAdvancedRuleObject = (overrides = {}) => {
  return {
    id: Pact.like(1),
    rule_group: Pact.like(1),
    field: Pact.like('weight_lb'),
    operator: Pact.like('gt'),
    value: Pact.like('10'),
    adjustment_amount: Pact.like('5.00'),
    conditions: {
      weight_lb: {
        operator: Pact.like('gt'),
        value: Pact.like('15')
      },
      order_priority: {
        operator: Pact.like('eq'),
        value: Pact.like('High')
      }
    },
    calculations: [
      {
        type: Pact.like('flat_fee'),
        value: Pact.like(5.00)
      },
      {
        type: Pact.like('per_unit'),
        value: Pact.like(1.25),
        field: Pact.like('quantity')
      }
    ],
    tier_config: {
      ranges: [
        {
          min: Pact.like(0),
          max: Pact.like(10),
          multiplier: Pact.like(1.0)
        },
        {
          min: Pact.like(11),
          max: Pact.like(20),
          multiplier: Pact.like(0.9)
        }
      ]
    },
    created_at: Pact.like('2025-01-15T10:30:00Z'),
    updated_at: Pact.like('2025-01-15T10:30:00Z'),
    ...overrides
  };
};

// Create field choices patterns for Pact tests
const createFieldChoicesObject = () => {
  return {
    weight_lb: {
      label: Pact.like('Weight (lb)'),
      type: Pact.like('decimal')
    },
    quantity: {
      label: Pact.like('Quantity'),
      type: Pact.like('integer')
    },
    order_priority: {
      label: Pact.like('Order Priority'),
      type: Pact.like('choice')
    },
    customer_id: {
      label: Pact.like('Customer ID'),
      type: Pact.like('integer')
    }
  };
};

// Create operator choices patterns for Pact tests
const createOperatorChoicesObject = () => {
  return {
    operators: [
      {
        value: Pact.like('eq'),
        label: Pact.like('Equals')
      },
      {
        value: Pact.like('ne'),
        label: Pact.like('Not Equal')
      },
      {
        value: Pact.like('gt'),
        label: Pact.like('Greater Than')
      },
      {
        value: Pact.like('lt'),
        label: Pact.like('Less Than')
      }
    ]
  };
};

// Create calculation types patterns for Pact tests
const createCalculationTypesObject = () => {
  return {
    flat_fee: Pact.like('Flat Fee'),
    percentage: Pact.like('Percentage'),
    per_unit: Pact.like('Per Unit'),
    weight_based: Pact.like('Weight Based'),
    case_based_tier: Pact.like('Case-Based Tier')
  };
};

describe('Rules API Contract Tests', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  
  // RULE GROUPS TESTS
  describe('GET /api/v1/rules/api/groups/', () => {
    beforeEach(() => {
      const ruleGroupExample = createRuleGroupObject();
      
      return provider.addInteraction({
        state: 'rule groups exist',
        uponReceiving: 'a request for all rule groups',
        withRequest: {
          method: 'GET',
          path: '/api/v1/rules/api/groups/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          [ruleGroupExample, createRuleGroupObject({ id: 2 })]
        )
      });
    });
    
    test('can retrieve a list of rule groups', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get('/api/v1/rules/api/groups/', {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
      expect(response.data[0].id).toBeDefined();
      expect(response.data[0].customer_service).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('GET /api/v1/rules/api/groups/:id/', () => {
    const groupId = 1;
    const ruleGroupExample = createRuleGroupObject({ id: groupId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `rule group with ID ${groupId} exists`,
        uponReceiving: 'a request for a specific rule group',
        withRequest: {
          method: 'GET',
          path: `/api/v1/rules/api/groups/${groupId}/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          ruleGroupExample
        )
      });
    });
    
    test('can retrieve a specific rule group', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/rules/api/groups/${groupId}/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.id).toEqual(groupId);
      expect(response.data.customer_service).toBeDefined();
      expect(response.data.logic_operator).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('POST /api/v1/rules/api/groups/', () => {
    const newRuleGroup = {
      customer_service: 1,
      logic_operator: 'AND'
    };
    
    const createdRuleGroup = createRuleGroupObject({
      ...newRuleGroup,
      id: 3
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'can create a rule group',
        uponReceiving: 'a request to create a rule group',
        withRequest: {
          method: 'POST',
          path: '/api/v1/rules/api/groups/',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: newRuleGroup
        },
        willRespondWith: createResponse(
          201, 
          { 'Content-Type': 'application/json' },
          createdRuleGroup
        )
      });
    });
    
    test('can create a rule group', async () => {
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post('/api/v1/rules/api/groups/', newRuleGroup, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(201);
      expect(response.data.id).toBeDefined();
      expect(response.data.customer_service).toEqual(newRuleGroup.customer_service);
      expect(response.data.logic_operator).toEqual(newRuleGroup.logic_operator);
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('PUT /api/v1/rules/api/groups/:id/', () => {
    const groupId = 1;
    const updatedRuleGroup = {
      customer_service: 1,
      logic_operator: 'OR'
    };
    
    const responseRuleGroup = createRuleGroupObject({
      id: groupId,
      ...updatedRuleGroup
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `rule group with ID ${groupId} exists`,
        uponReceiving: 'a request to update a rule group',
        withRequest: {
          method: 'PUT',
          path: `/api/v1/rules/api/groups/${groupId}/`,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: updatedRuleGroup
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          responseRuleGroup
        )
      });
    });
    
    test('can update a rule group', async () => {
      // Set up axios to use the mock provider's URL
      axios.put.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.put(`/api/v1/rules/api/groups/${groupId}/`, updatedRuleGroup, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.id).toEqual(groupId);
      expect(response.data.logic_operator).toEqual(updatedRuleGroup.logic_operator);
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('DELETE /api/v1/rules/api/groups/:id/', () => {
    const groupId = 1;
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `rule group with ID ${groupId} exists`,
        uponReceiving: 'a request to delete a rule group',
        withRequest: {
          method: 'DELETE',
          path: `/api/v1/rules/api/groups/${groupId}/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          204, 
          { 'Content-Type': 'application/json' },
          { success: true }
        )
      });
    });
    
    test('can delete a rule group', async () => {
      // Set up axios to use the mock provider's URL
      axios.delete.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.delete(`/api/v1/rules/api/groups/${groupId}/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(204);
      expect(response.data.success).toBe(true);
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  // BASIC RULES TESTS
  describe('GET /api/v1/rules/group/:groupId/rules/', () => {
    const groupId = 1;
    const ruleExample = createRuleObject({ rule_group: groupId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `rules exist for group ${groupId}`,
        uponReceiving: 'a request for rules in a specific group',
        withRequest: {
          method: 'GET',
          path: `/api/v1/rules/group/${groupId}/rules/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          [ruleExample, createRuleObject({ id: 2, rule_group: groupId })]
        )
      });
    });
    
    test('can retrieve rules for a specific group', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/rules/group/${groupId}/rules/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
      expect(response.data[0].rule_group).toEqual(groupId);
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('POST /api/v1/rules/group/:groupId/rule/create/api/', () => {
    const groupId = 1;
    const newRule = {
      field: 'weight_lb',
      operator: 'gt',
      value: '20',
      adjustment_amount: '7.50'
    };
    
    const createdRule = createRuleObject({
      ...newRule,
      id: 3,
      rule_group: groupId
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `can create rule for group ${groupId}`,
        uponReceiving: 'a request to create a rule',
        withRequest: {
          method: 'POST',
          path: `/api/v1/rules/group/${groupId}/rule/create/api/`,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: newRule
        },
        willRespondWith: createResponse(
          201, 
          { 'Content-Type': 'application/json' },
          createdRule
        )
      });
    });
    
    test('can create a rule', async () => {
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post(`/api/v1/rules/group/${groupId}/rule/create/api/`, newRule, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(201);
      expect(response.data.id).toBeDefined();
      expect(response.data.field).toEqual(newRule.field);
      expect(response.data.operator).toEqual(newRule.operator);
      expect(response.data.value).toEqual(newRule.value);
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  // ADVANCED RULES TESTS
  describe('GET /api/v1/rules/group/:groupId/advanced-rules/', () => {
    const groupId = 1;
    const advancedRuleExample = createAdvancedRuleObject({ rule_group: groupId });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `advanced rules exist for group ${groupId}`,
        uponReceiving: 'a request for advanced rules in a specific group',
        withRequest: {
          method: 'GET',
          path: `/api/v1/rules/group/${groupId}/advanced-rules/`,
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          [advancedRuleExample, createAdvancedRuleObject({ id: 2, rule_group: groupId })]
        )
      });
    });
    
    test('can retrieve advanced rules for a specific group', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/rules/group/${groupId}/advanced-rules/`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
      expect(response.data[0].rule_group).toEqual(groupId);
      expect(response.data[0].conditions).toBeDefined();
      expect(response.data[0].calculations).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('POST /api/v1/rules/group/:groupId/advanced-rule/create/api/', () => {
    const groupId = 1;
    const newAdvancedRule = {
      field: 'weight_lb',
      operator: 'gt',
      value: '20',
      adjustment_amount: '7.50',
      conditions: {
        quantity: {
          operator: 'gt',
          value: '5'
        }
      },
      calculations: [
        {
          type: 'flat_fee',
          value: 7.50
        }
      ],
      tier_config: {
        ranges: [
          {
            min: 0,
            max: 10,
            multiplier: 1.0
          }
        ]
      }
    };
    
    const createdAdvancedRule = createAdvancedRuleObject({
      ...newAdvancedRule,
      id: 3,
      rule_group: groupId
    });
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `can create advanced rule for group ${groupId}`,
        uponReceiving: 'a request to create an advanced rule',
        withRequest: {
          method: 'POST',
          path: `/api/v1/rules/group/${groupId}/advanced-rule/create/api/`,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: newAdvancedRule
        },
        willRespondWith: createResponse(
          201, 
          { 'Content-Type': 'application/json' },
          createdAdvancedRule
        )
      });
    });
    
    test('can create an advanced rule', async () => {
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post(`/api/v1/rules/group/${groupId}/advanced-rule/create/api/`, newAdvancedRule, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(201);
      expect(response.data.id).toBeDefined();
      expect(response.data.field).toEqual(newAdvancedRule.field);
      expect(response.data.conditions).toBeDefined();
      expect(response.data.calculations).toBeDefined();
      expect(response.data.tier_config).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  // UTILITY ENDPOINTS TESTS
  describe('GET /api/v1/rules/fields/', () => {
    const fieldsExample = createFieldChoicesObject();
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'available fields exist',
        uponReceiving: 'a request for available fields',
        withRequest: {
          method: 'GET',
          path: '/api/v1/rules/fields/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          fieldsExample
        )
      });
    });
    
    test('can retrieve available fields', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get('/api/v1/rules/fields/', {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data).toBeDefined();
      expect(response.data.weight_lb).toBeDefined();
      expect(response.data.weight_lb.label).toBeDefined();
      expect(response.data.weight_lb.type).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('GET /api/v1/rules/operators/', () => {
    const field = 'weight_lb';
    const operatorsExample = createOperatorChoicesObject();
    
    beforeEach(() => {
      return provider.addInteraction({
        state: `operators exist for field ${field}`,
        uponReceiving: 'a request for operators for a specific field',
        withRequest: {
          method: 'GET',
          path: '/api/v1/rules/operators/',
          query: { field },
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          operatorsExample
        )
      });
    });
    
    test('can retrieve operators for a field', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get(`/api/v1/rules/operators/?field=${field}`, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data).toBeDefined();
      expect(response.data.operators).toBeDefined();
      expect(Array.isArray(response.data.operators)).toBe(true);
      expect(response.data.operators.length).toBeGreaterThan(0);
      expect(response.data.operators[0].value).toBeDefined();
      expect(response.data.operators[0].label).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('GET /api/v1/rules/calculation-types/', () => {
    const calculationTypesExample = createCalculationTypesObject();
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'calculation types exist',
        uponReceiving: 'a request for calculation types',
        withRequest: {
          method: 'GET',
          path: '/api/v1/rules/calculation-types/',
          headers: {
            Accept: 'application/json',
            Authorization: 'Bearer test-token'
          }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          calculationTypesExample
        )
      });
    });
    
    test('can retrieve calculation types', async () => {
      // Set up axios to use the mock provider's URL
      axios.get.mockImplementation((url, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, config);
      });
      
      // Call the API
      const response = await apiClient.get('/api/v1/rules/calculation-types/', {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data).toBeDefined();
      expect(response.data.flat_fee).toBeDefined();
      expect(response.data.percentage).toBeDefined();
      expect(response.data.per_unit).toBeDefined();
      expect(response.data.case_based_tier).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('POST /api/v1/rules/validate-conditions/', () => {
    const conditions = {
      weight_lb: {
        operator: 'gt',
        value: '15'
      },
      order_priority: {
        operator: 'eq',
        value: 'High'
      }
    };
    
    const validationResult = {
      is_valid: Pact.like(true),
      errors: Pact.like([])
    };
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'can validate conditions',
        uponReceiving: 'a request to validate conditions',
        withRequest: {
          method: 'POST',
          path: '/api/v1/rules/validate-conditions/',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: { conditions }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          validationResult
        )
      });
    });
    
    test('can validate conditions', async () => {
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post('/api/v1/rules/validate-conditions/', { conditions }, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.is_valid).toBeDefined();
      expect(response.data.errors).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
  
  describe('POST /api/v1/rules/test-rule/', () => {
    const ruleData = createAdvancedRuleObject();
    const sampleOrderData = {
      id: 'ORD-001',
      weight_lb: 25,
      quantity: 10,
      order_priority: 'High'
    };
    
    const testResult = {
      rule_applies: Pact.like(true),
      calculation_amount: Pact.like(12.50),
      calculation_steps: Pact.like([
        { description: 'Applied flat fee', amount: 5.00 },
        { description: 'Applied per-unit charge', amount: 7.50 }
      ])
    };
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'can test rule',
        uponReceiving: 'a request to test a rule',
        withRequest: {
          method: 'POST',
          path: '/api/v1/rules/test-rule/',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token'
          },
          body: { rule: ruleData, order: sampleOrderData }
        },
        willRespondWith: createResponse(
          200, 
          { 'Content-Type': 'application/json' },
          testResult
        )
      });
    });
    
    test('can test a rule', async () => {
      // Set up axios to use the mock provider's URL
      axios.post.mockImplementation((url, data, config) => {
        const baseURL = provider.mockService.baseUrl;
        return axios.create({ baseURL })(url, { data, ...config });
      });
      
      // Call the API
      const response = await apiClient.post('/api/v1/rules/test-rule/', { rule: ruleData, order: sampleOrderData }, {
        headers: { Authorization: 'Bearer test-token' }
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      expect(response.data.rule_applies).toBeDefined();
      expect(response.data.calculation_amount).toBeDefined();
      expect(response.data.calculation_steps).toBeDefined();
      
      // Verify against the contract
      return provider.verify();
    });
  });
});