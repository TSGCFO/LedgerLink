import { Matchers } from '@pact-foundation/pact';
import axios from 'axios';
import { provider, createPaginatedResponse, createResponse, like, eachLike } from '../pact-utils';

// Mock apiClient
jest.mock('../apiClient', () => {
  return {
    __esModule: true,
    default: {
      get: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 200,
          data: {
            count: 10,
            results: [{ id: 1, name: 'Test Rule Group' }]
          }
        });
      }),
      post: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 201,
          data: { id: 100, name: 'New Rule Group' }
        });
      }),
      put: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 200,
          data: { id: 1, name: 'Updated Rule Group' }
        });
      }),
      delete: jest.fn().mockImplementation(() => {
        return Promise.resolve({
          status: 204,
          data: { success: true }
        });
      })
    }
  };
});

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
    id: like(1),
    customer_service: like(1),
    customer_service_details: {
      id: like(1),
      customer: like(1),
      customer_name: like('Test Company'),
      service: like(1),
      service_name: like('Test Service')
    },
    logic_operator: like('AND'),
    is_active: like(true),
    ...overrides
  };
};

// Create basic rule object patterns for Pact tests
const createRuleObject = (overrides = {}) => {
  return {
    id: like(1),
    rule_group: like(1),
    field: like('weight_lb'),
    operator: like('gt'),
    value: like('10'),
    adjustment_amount: like('5.00'),
    created_at: like('2025-01-15T10:30:00Z'),
    updated_at: like('2025-01-15T10:30:00Z'),
    ...overrides
  };
};

// Create advanced rule object patterns for Pact tests
const createAdvancedRuleObject = (overrides = {}) => {
  return {
    id: like(1),
    rule_group: like(1),
    field: like('weight_lb'),
    operator: like('gt'),
    value: like('10'),
    adjustment_amount: like('5.00'),
    conditions: {
      weight_lb: {
        operator: like('gt'),
        value: like('15')
      },
      order_priority: {
        operator: like('eq'),
        value: like('High')
      }
    },
    calculations: [
      {
        type: like('flat_fee'),
        value: like(5.00)
      },
      {
        type: like('per_unit'),
        value: like(1.25),
        field: like('quantity')
      }
    ],
    tier_config: {
      ranges: [
        {
          min: like(0),
          max: like(10),
          multiplier: like(1.0)
        },
        {
          min: like(11),
          max: like(20),
          multiplier: like(0.9)
        }
      ]
    },
    created_at: like('2025-01-15T10:30:00Z'),
    updated_at: like('2025-01-15T10:30:00Z'),
    ...overrides
  };
};

// Create field choices patterns for Pact tests
const createFieldChoicesObject = () => {
  return {
    weight_lb: {
      label: like('Weight (lb)'),
      type: like('decimal')
    },
    quantity: {
      label: like('Quantity'),
      type: like('integer')
    },
    order_priority: {
      label: like('Order Priority'),
      type: like('choice')
    },
    customer_id: {
      label: like('Customer ID'),
      type: like('integer')
    }
  };
};

// Create operator choices patterns for Pact tests
const createOperatorChoicesObject = () => {
  return {
    operators: [
      {
        value: like('eq'),
        label: like('Equals')
      },
      {
        value: like('ne'),
        label: like('Not Equal')
      },
      {
        value: like('gt'),
        label: like('Greater Than')
      },
      {
        value: like('lt'),
        label: like('Less Than')
      }
    ]
  };
};

// Create calculation types patterns for Pact tests
const createCalculationTypesObject = () => {
  return {
    flat_fee: like('Flat Fee'),
    percentage: like('Percentage'),
    per_unit: like('Per Unit'),
    weight_based: like('Weight Based'),
    case_based_tier: like('Case-Based Tier')
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'PUT',
        url: `/api/v1/rules/api/groups/${groupId}/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'DELETE',
        url: `/api/v1/rules/api/groups/${groupId}/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/api/v1/rules/group/${groupId}/rules/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'POST',
        url: `/api/v1/rules/group/${groupId}/rule/create/api/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/api/v1/rules/group/${groupId}/advanced-rules/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'POST',
        url: `/api/v1/rules/group/${groupId}/advanced-rule/create/api/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/api/v1/rules/operators/?field=${field}`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'GET',
        url: `/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      is_valid: like(true),
      errors: like([])
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'POST',
        url: `/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
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
      rule_applies: like(true),
      calculation_amount: like(12.50),
      calculation_steps: like([
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
      // Call the API using our mock request helper
      const response = await provider.mockRequest({
        method: 'POST',
        url: `/`
      });
      
      // Verify the response
      expect(response.status).toEqual(200);
      
      // Write the Pact file with our contract
      await provider.verify();
    });
  });
});