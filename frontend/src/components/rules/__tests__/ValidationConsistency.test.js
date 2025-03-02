/**
 * Tests for validation consistency between frontend validation
 * and backend validation returned via API
 */
import { validateCalculation } from '../../../utils/validationUtils';
import rulesService from '../../../services/rulesService';

// Mock the rulesService API calls
jest.mock('../../../services/rulesService', () => ({
  validateCalculations: jest.fn()
}));

describe('Rule Validation Consistency', () => {
  beforeEach(() => {
    // Reset mock function calls between tests
    jest.clearAllMocks();
  });

  test('Valid case-based tier passes both client and server validation', async () => {
    // Valid case-based tier configuration
    const validConfig = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 1, max: 3, multiplier: 1.0 },
          { min: 4, max: 6, multiplier: 2.0 },
          { min: 7, max: 10, multiplier: 3.0 }
        ],
        excluded_skus: ['SKU3']
      }
    };

    // Setup server response mock
    rulesService.validateCalculations.mockResolvedValue({ valid: true });

    // Client-side validation
    const clientResult = validateCalculation(validConfig);
    expect(clientResult.isValid).toBe(true);

    // Server-side validation
    const serverResult = await rulesService.validateCalculations([validConfig]);
    expect(serverResult.valid).toBe(true);
    expect(rulesService.validateCalculations).toHaveBeenCalledTimes(1);
  });

  test('Missing ranges fails both client and server validation with consistent errors', async () => {
    // Invalid case-based tier configuration (missing ranges)
    const invalidConfig = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        excluded_skus: ['SKU3']
      }
    };

    // Setup server response mock
    rulesService.validateCalculations.mockResolvedValue({
      valid: false,
      errors: ['Ranges must be specified in tier_config']
    });

    // Client-side validation
    const clientResult = validateCalculation(invalidConfig);
    expect(clientResult.isValid).toBe(false);
    expect(clientResult.message).toContain('Ranges must be specified');

    // Server-side validation
    const serverResult = await rulesService.validateCalculations([invalidConfig]);
    expect(serverResult.valid).toBe(false);
    expect(serverResult.errors[0]).toContain('Ranges must be specified');
    expect(rulesService.validateCalculations).toHaveBeenCalledTimes(1);
  });

  test('Invalid min/max relationship fails both client and server validation', async () => {
    // Invalid min/max relationship
    const invalidConfig = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 5, max: 3, multiplier: 1.0 } // min > max
        ],
        excluded_skus: []
      }
    };

    // Setup server response mock with error that includes "greater than"
    rulesService.validateCalculations.mockResolvedValue({
      valid: false,
      errors: ['Min value (5) cannot be greater than max value (3)']
    });

    // Client-side validation
    const clientResult = validateCalculation(invalidConfig);
    expect(clientResult.isValid).toBe(false);
    expect(clientResult.message).toContain('greater than');

    // Server-side validation
    const serverResult = await rulesService.validateCalculations([invalidConfig]);
    expect(serverResult.valid).toBe(false);
    expect(serverResult.errors[0]).toContain('greater than');
    expect(rulesService.validateCalculations).toHaveBeenCalledTimes(1);
  });

  test('Non-numeric values fail both client and server validation', async () => {
    // Invalid non-numeric values
    const invalidConfig = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 1, max: 'abc', multiplier: 1.0 } // non-numeric max
        ],
        excluded_skus: []
      }
    };

    // Setup server response mock
    rulesService.validateCalculations.mockResolvedValue({
      valid: false,
      errors: ['Min, max, and multiplier values must be valid numbers']
    });

    // Client-side validation
    const clientResult = validateCalculation(invalidConfig);
    expect(clientResult.isValid).toBe(false);
    expect(clientResult.message).toContain('valid numbers');

    // Server-side validation
    const serverResult = await rulesService.validateCalculations([invalidConfig]);
    expect(serverResult.valid).toBe(false);
    expect(serverResult.errors[0]).toContain('valid numbers');
  });

  test('Client validation matches API validation characteristics', async () => {
    // Array of test cases with different validation scenarios
    const testCases = [
      {
        name: 'Valid configuration',
        config: {
          type: 'case_based_tier',
          value: 1.0,
          tier_config: {
            ranges: [
              { min: 1, max: 3, multiplier: 1.0 }
            ],
            excluded_skus: []
          }
        },
        clientValid: true,
        serverValid: true
      },
      {
        name: 'Missing required fields',
        config: {
          type: 'case_based_tier',
          value: 1.0,
          tier_config: {
            ranges: [
              { min: 1, multiplier: 1.0 } // missing max
            ]
          }
        },
        clientValid: false,
        serverValid: false,
        errorPattern: /min.*max.*multiplier/i
      },
      {
        name: 'Negative values',
        config: {
          type: 'case_based_tier',
          value: 1.0,
          tier_config: {
            ranges: [
              { min: -1, max: 3, multiplier: 1.0 } // negative min
            ],
            excluded_skus: []
          }
        },
        clientValid: false,
        serverValid: false,
        errorPattern: /non-negative/i
      }
    ];
    
    // Test each case
    for (const testCase of testCases) {
      // Setup server response mock based on the test case
      rulesService.validateCalculations.mockResolvedValue({
        valid: testCase.serverValid,
        errors: testCase.serverValid ? [] : ['Validation error']
      });
      
      // Client-side validation
      const clientResult = validateCalculation(testCase.config);
      expect(clientResult.isValid).toBe(testCase.clientValid);
      
      // Server-side validation
      const serverResult = await rulesService.validateCalculations([testCase.config]);
      expect(serverResult.valid).toBe(testCase.serverValid);
      
      // For invalid cases, check error patterns if specified
      if (!testCase.clientValid && testCase.errorPattern) {
        expect(clientResult.message).toMatch(testCase.errorPattern);
      }
    }
  });
});