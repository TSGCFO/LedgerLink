const FIELD_TYPES = {
  reference_number: 'string',
  ship_to_name: 'string',
  ship_to_company: 'string',
  ship_to_city: 'string',
  ship_to_state: 'string',
  ship_to_country: 'string',
  weight_lb: 'number',
  line_items: 'number',
  sku_quantity: 'sku',
  total_item_qty: 'number',
  packages: 'number',
  notes: 'string',
  carrier: 'string',
  volume_cuft: 'number'
};

const STRING_OPERATORS = [
  'eq', 'ne', 'in', 'ni', 'contains', 
  'ncontains', 'startswith', 'endswith'
];

const NUMBER_OPERATORS = [
  'eq', 'ne', 'gt', 'lt', 'ge', 'le'
];

const SKU_OPERATORS = [
  'contains', 'ncontains', 'only_contains'
];

class RuleValidator {
  /**
   * Validates a complete rule
   */
  validateRule(rule) {
    const errors = [];
    const warnings = [];

    // Check required fields
    if (!rule.field) {
      errors.push({
        field: 'field',
        message: 'Field is required',
        code: 'REQUIRED'
      });
    }

    if (!rule.operator) {
      errors.push({
        field: 'operator',
        message: 'Operator is required',
        code: 'REQUIRED'
      });
    }

    if (!rule.value && rule.value !== '0') {
      errors.push({
        field: 'value',
        message: 'Value is required',
        code: 'REQUIRED'
      });
    }

    // If we have basic validation errors, return early
    if (errors.length > 0) {
      return { isValid: false, errors, warnings };
    }

    // Validate field and operator combination
    const fieldType = FIELD_TYPES[rule.field];
    if (!fieldType) {
      errors.push({
        field: 'field',
        message: `Unknown field: ${rule.field}`,
        code: 'INVALID_FIELD'
      });
    } else {
      const validOperators = this.getValidOperatorsForType(fieldType);
      if (!validOperators.includes(rule.operator)) {
        errors.push({
          field: 'operator',
          message: `Invalid operator '${rule.operator}' for field type '${fieldType}'`,
          code: 'INVALID_OPERATOR'
        });
      }
    }

    // Validate value format
    const valueValidation = this.validateValue(rule.value, fieldType, rule.operator);
    errors.push(...valueValidation.errors);
    warnings.push(...valueValidation.warnings);

    // Validate adjustment amount if present
    if (rule.adjustment_amount !== undefined) {
      if (isNaN(Number(rule.adjustment_amount))) {
        errors.push({
          field: 'adjustment_amount',
          message: 'Adjustment amount must be a number',
          code: 'INVALID_ADJUSTMENT'
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Gets valid operators for a field type
   */
  getValidOperatorsForType(type) {
    switch (type) {
      case 'string':
        return STRING_OPERATORS;
      case 'number':
        return NUMBER_OPERATORS;
      case 'sku':
        return SKU_OPERATORS;
      default:
        return [];
    }
  }

  /**
   * Validates the value based on field type and operator
   */
  validateValue(value, fieldType, operator) {
    const errors = [];
    const warnings = [];

    switch (fieldType) {
      case 'number':
        if (operator !== 'in' && operator !== 'ni') {
          if (isNaN(Number(value))) {
            errors.push({
              field: 'value',
              message: 'Value must be a number',
              code: 'INVALID_NUMBER'
            });
          }
        } else {
          // Check each value in the list
          const values = value.split(';');
          values.forEach((v, index) => {
            if (isNaN(Number(v.trim()))) {
              errors.push({
                field: 'value',
                message: `Invalid number at position ${index + 1}`,
                code: 'INVALID_NUMBER_IN_LIST'
              });
            }
          });
        }
        break;

      case 'sku':
        if (operator === 'only_contains' && !value.includes(';')) {
          warnings.push({
            field: 'value',
            message: 'Consider adding multiple SKUs for only_contains operator',
            code: 'SINGLE_SKU_WARNING'
          });
        }
        break;

      case 'string':
        if ((operator === 'in' || operator === 'ni') && !value.includes(';')) {
          warnings.push({
            field: 'value',
            message: 'Consider adding multiple values for in/not in operators',
            code: 'SINGLE_VALUE_WARNING'
          });
        }
        break;
    }

    return { errors, warnings };
  }

  /**
   * Validates a semicolon-separated list of values
   */
  validateValueList(value) {
    return value
      .split(';')
      .map(v => v.trim())
      .filter(v => v.length > 0);
  }
}

export default new RuleValidator();