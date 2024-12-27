/**
 * Validation utilities for rules and rule groups
 * @module validation
 */

/**
 * Rule validation schema
 * @type {Object}
 */
export const RULE_SCHEMA = {
    field: {
        required: true,
        type: 'string',
        validate: value => value.length > 0
    },
    operator: {
        required: true,
        type: 'string',
        validate: value => value.length > 0
    },
    value: {
        required: true,
        type: 'string',
        validate: value => value.length > 0
    }
};

/**
 * Validates a rule object against the schema
 * @param {Object} rule - Rule object to validate
 * @returns {Object} Validation result with errors if any
 */
export function validateRule(rule) {
    const errors = {};

    Object.entries(RULE_SCHEMA).forEach(([field, schema]) => {
        if (schema.required && !rule[field]) {
            errors[field] = `${field} is required`;
            return;
        }

        if (rule[field] && typeof rule[field] !== schema.type) {
            errors[field] = `${field} must be a ${schema.type}`;
            return;
        }

        if (schema.validate && !schema.validate(rule[field])) {
            errors[field] = `${field} is invalid`;
        }
    });

    return {
        isValid: Object.keys(errors).length === 0,
        errors
    };
}

/**
 * Validates a rule group object
 * @param {Object} ruleGroup - Rule group object to validate
 * @returns {Object} Validation result with errors if any
 */
export function validateRuleGroup(ruleGroup) {
    const errors = {};

    if (!ruleGroup.customer) {
        errors.customer = 'Customer is required';
    }

    if (!ruleGroup.service) {
        errors.service = 'Service is required';
    }

    if (!ruleGroup.logicOperator) {
        errors.logicOperator = 'Logic operator is required';
    }

    if (!ruleGroup.rules || !Array.isArray(ruleGroup.rules)) {
        errors.rules = 'Rules must be an array';
    } else if (ruleGroup.rules.length === 0) {
        errors.rules = 'At least one rule is required';
    } else {
        const ruleErrors = ruleGroup.rules.map(validateRule);
        if (ruleErrors.some(result => !result.isValid)) {
            errors.rules = ruleErrors;
        }
    }

    return {
        isValid: Object.keys(errors).length === 0,
        errors
    };
}