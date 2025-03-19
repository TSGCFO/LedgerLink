/**
 * Utility functions for form validation in the rules app
 */

/**
 * Validates a rule value based on field type
 * @param {string} field - The field being validated
 * @param {string} operator - The operator selected
 * @param {string} value - The value entered
 * @returns {Object} - { isValid: boolean, message?: string }
 */
export const validateRuleValue = (field, operator, value) => {
  // Field categories
  const numericFields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages', 'sku_count'];
  const stringFields = ['reference_number', 'ship_to_name', 'ship_to_company', 'ship_to_city', 
                       'ship_to_state', 'ship_to_country', 'carrier', 'notes', 'sku_name'];
  const skuFields = ['sku_quantity'];
  
  // Operator categories
  const numericOperators = ['gt', 'lt', 'eq', 'ne', 'ge', 'le'];
  const stringOperators = ['eq', 'ne', 'contains', 'ncontains', 'startswith', 'endswith', 'in', 'ni'];
  const skuOperators = ['contains', 'ncontains', 'only_contains', 'in', 'ni'];

  // Basic validation
  if (!field || !operator || !value) {
    return { 
      isValid: false, 
      message: 'Field, operator, and value are all required' 
    };
  }

  // Numeric field validation
  if (numericFields.includes(field)) {
    if (!numericOperators.includes(operator)) {
      return { 
        isValid: false, 
        message: `Operator "${operator}" is not valid for numeric fields.` 
      };
    }
    
    // Check if all values are numeric
    const values = value.split(';').map(v => v.trim());
    const allNumeric = values.every(v => !isNaN(parseFloat(v)) && isFinite(v));
    
    if (!allNumeric) {
      return { 
        isValid: false, 
        message: 'All values must be numeric for numeric fields' 
      };
    }
  }
  
  // String field validation
  else if (stringFields.includes(field)) {
    if (!stringOperators.includes(operator)) {
      return { 
        isValid: false, 
        message: `Operator "${operator}" is not valid for string fields.` 
      };
    }
  }
  
  // SKU quantity validation
  else if (skuFields.includes(field)) {
    if (!skuOperators.includes(operator)) {
      return { 
        isValid: false, 
        message: `Operator "${operator}" is not valid for SKU quantity.` 
      };
    }
    
    // Check if value is provided
    if (!value.trim()) {
      return { 
        isValid: false, 
        message: 'At least one SKU must be specified' 
      };
    }
  }
  
  return { isValid: true };
};

/**
 * Validates a calculation configuration
 * @param {Object} calculation - The calculation to validate
 * @returns {Object} - { isValid: boolean, message?: string }
 */
export const validateCalculation = (calculation) => {
  const validTypes = [
    'flat_fee', 'percentage', 'per_unit', 'weight_based',
    'volume_based', 'tiered_percentage', 'product_specific', 
    'case_based_tier'
  ];
  
  if (!calculation.type || !validTypes.includes(calculation.type)) {
    return { 
      isValid: false, 
      message: `Invalid calculation type: ${calculation.type || 'none'}` 
    };
  }
  
  if (calculation.value === undefined || calculation.value === null || calculation.value === '') {
    return { 
      isValid: false, 
      message: 'Value is required for calculation' 
    };
  }
  
  const numValue = parseFloat(calculation.value);
  if (isNaN(numValue)) {
    return { 
      isValid: false, 
      message: 'Value must be a number' 
    };
  }
  
  // Special validation for case_based_tier
  if (calculation.type === 'case_based_tier') {
    // Check for tier_config
    if (!calculation.tier_config) {
      return { 
        isValid: false, 
        message: 'Tier configuration is required for case-based tier calculations' 
      };
    }
    
    // Check for ranges
    if (!calculation.tier_config.ranges || !Array.isArray(calculation.tier_config.ranges)) {
      return { 
        isValid: false, 
        message: 'Ranges must be specified in tier configuration' 
      };
    }
    
    // Validate each tier
    for (const tier of calculation.tier_config.ranges) {
      if (!tier.min || !tier.max || !tier.multiplier) {
        return { 
          isValid: false, 
          message: 'Each tier must specify min, max, and multiplier values' 
        };
      }
      
      const minVal = parseFloat(tier.min);
      const maxVal = parseFloat(tier.max);
      const multiplier = parseFloat(tier.multiplier);
      
      if (isNaN(minVal) || isNaN(maxVal) || isNaN(multiplier)) {
        return { 
          isValid: false, 
          message: 'Min, max, and multiplier values must be valid numbers' 
        };
      }
      
      if (minVal < 0 || maxVal < 0 || multiplier < 0) {
        return { 
          isValid: false, 
          message: 'Min, max, and multiplier values must be non-negative' 
        };
      }
      
      if (minVal > maxVal) {
        return { 
          isValid: false, 
          message: `Min value (${minVal}) cannot be greater than max value (${maxVal})` 
        };
      }
    }
    
    // Check for overlapping ranges
    const sortedRanges = [...calculation.tier_config.ranges].sort((a, b) => parseFloat(a.min) - parseFloat(b.min));
    for (let i = 0; i < sortedRanges.length - 1; i++) {
      const currentMax = parseFloat(sortedRanges[i].max);
      const nextMin = parseFloat(sortedRanges[i + 1].min);
      
      if (currentMax >= nextMin) {
        return {
          isValid: false,
          message: `Overlapping tiers detected: tier with max=${currentMax} overlaps with tier with min=${nextMin}`
        };
      }
      
      // Check for gaps between tiers
      if (currentMax + 1 < nextMin) {
        return {
          isValid: false,
          message: `Gap detected between tiers: tier with max=${currentMax} has gap before tier with min=${nextMin}`
        };
      }
    }
  }
  
  return { isValid: true };
};

/**
 * Validates condition format
 * @param {Object} conditions - The conditions object
 * @returns {Object} - { isValid: boolean, message?: string }
 */
export const validateConditions = (conditions) => {
  if (!conditions || typeof conditions !== 'object') {
    return { 
      isValid: false, 
      message: 'Conditions must be an object' 
    };
  }
  
  for (const [field, criteria] of Object.entries(conditions)) {
    if (!field) {
      return { 
        isValid: false, 
        message: 'Field name cannot be empty' 
      };
    }
    
    if (!criteria || typeof criteria !== 'object') {
      return { 
        isValid: false, 
        message: `Criteria for field ${field} must be an object` 
      };
    }
    
    const [operator, value] = Object.entries(criteria)[0] || ['', ''];
    
    if (!operator) {
      return { 
        isValid: false, 
        message: `Operator is required for field ${field}` 
      };
    }
    
    if (value === undefined || value === null || value === '') {
      return { 
        isValid: false, 
        message: `Value is required for field ${field}` 
      };
    }
  }
  
  return { isValid: true };
};