/**
 * @module operators
 * @description Constants for rule operators and logic operators
 */

/**
 * Available operators for different field types
 * @type {Object}
 */
export const FIELD_OPERATORS = {
    text: [
        { value: 'contains', label: 'Contains' },
        { value: 'not_contains', label: 'Does not contain' },
        { value: 'equals', label: 'Equals' },
        { value: 'not_equals', label: 'Does not equal' },
        { value: 'starts_with', label: 'Starts with' },
        { value: 'ends_with', label: 'Ends with' },
        { value: 'is_empty', label: 'Is empty' },
        { value: 'is_not_empty', label: 'Is not empty' }
    ],
    number: [
        { value: 'equals', label: 'Equals' },
        { value: 'not_equals', label: 'Does not equal' },
        { value: 'greater_than', label: 'Greater than' },
        { value: 'less_than', label: 'Less than' },
        { value: 'greater_equal', label: 'Greater than or equal' },
        { value: 'less_equal', label: 'Less than or equal' },
        { value: 'between', label: 'Between' }
    ],
    datetime: [
        { value: 'equals', label: 'Equals' },
        { value: 'not_equals', label: 'Does not equal' },
        { value: 'before', label: 'Before' },
        { value: 'after', label: 'After' },
        { value: 'between', label: 'Between' }
    ]
};

/**
 * Logic operators for rule groups
 * @type {Array}
 */
export const LOGIC_OPERATORS = [
    { value: 'AND', label: 'All conditions must be true (AND)' },
    { value: 'OR', label: 'Any condition can be true (OR)' },
    { value: 'NOT', label: 'Condition must not be true (NOT)' },
    { value: 'XOR', label: 'Only one condition must be true (XOR)' },
    { value: 'NAND', label: 'At least one condition must be false (NAND)' },
    { value: 'NOR', label: 'None of the conditions must be true (NOR)' }
];

/**
 * Get operators for a specific field type
 * @param {string} fieldType - Type of field
 * @returns {Array} Array of operators
 */
export function getOperatorsForFieldType(fieldType) {
    return FIELD_OPERATORS[fieldType] || [];
}