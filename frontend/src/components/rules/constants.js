// Field Types
export const FIELD_TYPES = {
  STRING: 'string',
  NUMBER: 'number',
  SKU: 'sku'
};

// Operators
export const OPERATORS = {
  // Equality
  EQUALS: 'eq',
  NOT_EQUALS: 'ne',
  // Comparison
  GREATER_THAN: 'gt',
  LESS_THAN: 'lt',
  GREATER_EQUAL: 'ge',
  LESS_EQUAL: 'le',
  // List inclusion
  IN: 'in',
  NOT_IN: 'ni',
  // String contains
  CONTAINS: 'contains',
  NOT_CONTAINS: 'ncontains',
  // String position
  STARTS_WITH: 'startswith',
  ENDS_WITH: 'endswith',
  // SKU specific
  ONLY_CONTAINS: 'only_contains'
};

// Logic Operators
export const LOGIC_OPERATORS = {
  AND: 'AND',
  OR: 'OR',
  NOT: 'NOT',
  XOR: 'XOR',
  NAND: 'NAND',
  NOR: 'NOR'
};

// Calculation Types
export const CALCULATION_TYPES = {
  FLAT_FEE: 'flat_fee',
  PERCENTAGE: 'percentage',
  PER_UNIT: 'per_unit',
  WEIGHT_BASED: 'weight_based',
  VOLUME_BASED: 'volume_based',
  TIERED_PERCENTAGE: 'tiered_percentage',
  PRODUCT_SPECIFIC: 'product_specific'
};

// Field Options
export const FIELD_OPTIONS = [
  { value: 'reference_number', label: 'Reference Number', type: FIELD_TYPES.STRING },
  { value: 'ship_to_name', label: 'Ship To Name', type: FIELD_TYPES.STRING },
  { value: 'ship_to_company', label: 'Ship To Company', type: FIELD_TYPES.STRING },
  { value: 'ship_to_city', label: 'Ship To City', type: FIELD_TYPES.STRING },
  { value: 'ship_to_state', label: 'Ship To State', type: FIELD_TYPES.STRING },
  { value: 'ship_to_country', label: 'Ship To Country', type: FIELD_TYPES.STRING },
  { value: 'weight_lb', label: 'Weight (lb)', type: FIELD_TYPES.NUMBER },
  { value: 'line_items', label: 'Line Items', type: FIELD_TYPES.NUMBER },
  { value: 'sku_quantity', label: 'SKU Quantity', type: FIELD_TYPES.SKU },
  { value: 'total_item_qty', label: 'Total Item Quantity', type: FIELD_TYPES.NUMBER },
  { value: 'packages', label: 'Packages', type: FIELD_TYPES.NUMBER },
  { value: 'notes', label: 'Notes', type: FIELD_TYPES.STRING },
  { value: 'carrier', label: 'Carrier', type: FIELD_TYPES.STRING },
  { value: 'volume_cuft', label: 'Volume (cu ft)', type: FIELD_TYPES.NUMBER }
];

// Operator Options
export const STRING_OPERATORS = [
  { value: OPERATORS.EQUALS, label: 'Equals' },
  { value: OPERATORS.NOT_EQUALS, label: 'Not Equals' },
  { value: OPERATORS.CONTAINS, label: 'Contains' },
  { value: OPERATORS.NOT_CONTAINS, label: 'Does Not Contain' },
  { value: OPERATORS.STARTS_WITH, label: 'Starts With' },
  { value: OPERATORS.ENDS_WITH, label: 'Ends With' },
  { value: OPERATORS.IN, label: 'In List' },
  { value: OPERATORS.NOT_IN, label: 'Not In List' }
];

export const NUMBER_OPERATORS = [
  { value: OPERATORS.EQUALS, label: 'Equals' },
  { value: OPERATORS.NOT_EQUALS, label: 'Not Equals' },
  { value: OPERATORS.GREATER_THAN, label: 'Greater Than' },
  { value: OPERATORS.LESS_THAN, label: 'Less Than' },
  { value: OPERATORS.GREATER_EQUAL, label: 'Greater Than or Equal' },
  { value: OPERATORS.LESS_EQUAL, label: 'Less Than or Equal' }
];

export const SKU_OPERATORS = [
  { value: OPERATORS.CONTAINS, label: 'Contains SKU' },
  { value: OPERATORS.NOT_CONTAINS, label: 'Does Not Contain SKU' },
  { value: OPERATORS.ONLY_CONTAINS, label: 'Only Contains SKUs' }
];

// Logic Operator Options
export const LOGIC_OPERATOR_OPTIONS = [
  { value: LOGIC_OPERATORS.AND, label: 'All conditions must be true (AND)' },
  { value: LOGIC_OPERATORS.OR, label: 'Any condition can be true (OR)' },
  { value: LOGIC_OPERATORS.NOT, label: 'Condition must not be true (NOT)' },
  { value: LOGIC_OPERATORS.XOR, label: 'Only one condition must be true (XOR)' },
  { value: LOGIC_OPERATORS.NAND, label: 'At least one condition must be false (NAND)' },
  { value: LOGIC_OPERATORS.NOR, label: 'None of the conditions must be true (NOR)' }
];

// Calculation Type Options
export const CALCULATION_TYPE_OPTIONS = [
  { value: CALCULATION_TYPES.FLAT_FEE, label: 'Flat Fee', description: 'Add a fixed amount' },
  { value: CALCULATION_TYPES.PERCENTAGE, label: 'Percentage', description: 'Add a percentage of the base price' },
  { value: CALCULATION_TYPES.PER_UNIT, label: 'Per Unit', description: 'Multiply by quantity' },
  { value: CALCULATION_TYPES.WEIGHT_BASED, label: 'Weight Based', description: 'Multiply by weight' },
  { value: CALCULATION_TYPES.VOLUME_BASED, label: 'Volume Based', description: 'Multiply by volume' },
  { value: CALCULATION_TYPES.TIERED_PERCENTAGE, label: 'Tiered Percentage', description: 'Apply percentage based on value tiers' },
  { value: CALCULATION_TYPES.PRODUCT_SPECIFIC, label: 'Product Specific', description: 'Apply specific rates per product' }
];