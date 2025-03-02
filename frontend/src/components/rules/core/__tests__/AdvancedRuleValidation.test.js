import { validateCalculation } from '../../../../utils/validationUtils';

/**
 * Tests for validating that frontend validation for case-based tiers
 * is consistent with backend validation
 */
describe('Advanced Rule Case-Based Tier Validation', () => {
  // Test valid configuration
  test('Valid case-based tier config passes validation', () => {
    const calculation = {
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
    
    const { isValid } = validateCalculation(calculation);
    expect(isValid).toBe(true);
  });
  
  // Test missing ranges array
  test('Missing ranges array fails validation', () => {
    const calculation = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        excluded_skus: ['SKU3']
      }
    };
    
    const { isValid, message } = validateCalculation(calculation);
    expect(isValid).toBe(false);
    expect(message).toContain('Ranges must be specified');
  });
  
  // Test invalid min/max relationship
  test('Invalid min/max relationship fails validation', () => {
    const calculation = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 5, max: 3, multiplier: 1.0 }, // min > max
        ],
        excluded_skus: []
      }
    };
    
    const { isValid, message } = validateCalculation(calculation);
    expect(isValid).toBe(false);
    expect(message).toContain('Min value (5) cannot be greater than max value (3)');
  });
  
  // Test missing required fields
  test('Missing required fields fails validation', () => {
    const calculation = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 1, multiplier: 1.0 }, // missing max
        ]
      }
    };
    
    const { isValid, message } = validateCalculation(calculation);
    expect(isValid).toBe(false);
    expect(message).toContain('Each tier must specify min, max, and multiplier values');
  });
  
  // Test negative values
  test('Negative values fail validation', () => {
    const calculation = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: -1, max: 3, multiplier: 1.0 }, // negative min
        ],
        excluded_skus: []
      }
    };
    
    const { isValid, message } = validateCalculation(calculation);
    expect(isValid).toBe(false);
    expect(message).toContain('Min, max, and multiplier values must be non-negative');
  });
  
  // Test non-numeric values
  test('Non-numeric values fail validation', () => {
    const calculation = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 1, max: '3x', multiplier: 1.0 }, // invalid max
        ],
        excluded_skus: []
      }
    };
    
    const { isValid, message } = validateCalculation(calculation);
    expect(isValid).toBe(false);
    expect(message).toContain('Min, max, and multiplier values must be valid numbers');
  });
  
  // Test excluded_skus format
  test('Invalid excluded_skus format fails validation', () => {
    const calculation = {
      type: 'case_based_tier',
      value: 1.0,
      tier_config: {
        ranges: [
          { min: 1, max: 3, multiplier: 1.0 },
        ],
        excluded_skus: 'SKU1,SKU2' // should be array
      }
    };
    
    const { isValid, message } = validateCalculation(calculation);
    expect(isValid).toBe(false);
    expect(message).toContain('excluded_skus must be a list');
  });
});