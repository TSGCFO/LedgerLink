class RuleEngine {
  /**
   * Evaluates a single rule against provided context
   */
  evaluateRule(rule, context) {
    try {
      const { field, operator, value } = rule;
      const contextValue = context[field];

      switch (operator) {
        case 'eq':
          return { success: contextValue === value, reason: 'equality check' };
        case 'ne':
          return { success: contextValue !== value, reason: 'inequality check' };
        case 'gt':
          return { success: Number(contextValue) > Number(value), reason: 'greater than check' };
        case 'lt':
          return { success: Number(contextValue) < Number(value), reason: 'less than check' };
        case 'ge':
          return { success: Number(contextValue) >= Number(value), reason: 'greater or equal check' };
        case 'le':
          return { success: Number(contextValue) <= Number(value), reason: 'less or equal check' };
        case 'contains':
          return { success: String(contextValue).includes(String(value)), reason: 'contains check' };
        case 'ncontains':
          return { success: !String(contextValue).includes(String(value)), reason: 'not contains check' };
        case 'startswith':
          return { success: String(contextValue).startsWith(String(value)), reason: 'starts with check' };
        case 'endswith':
          return { success: String(contextValue).endsWith(String(value)), reason: 'ends with check' };
        case 'in':
          return { success: value.split(';').includes(String(contextValue)), reason: 'in check' };
        case 'ni':
          return { success: !value.split(';').includes(String(contextValue)), reason: 'not in check' };
        default:
          return { success: false, reason: `Unknown operator: ${operator}` };
      }
    } catch (error) {
      return { success: false, reason: `Evaluation error: ${error.message}` };
    }
  }

  /**
   * Evaluates a rule group using its logical operator
   */
  evaluateGroup(group, context) {
    try {
      const results = group.rules.map(rule => this.evaluateRule(rule, context));

      switch (group.logic_operator) {
        case 'AND':
          return {
            success: results.every(r => r.success),
            reason: 'All conditions must be true'
          };
        case 'OR':
          return {
            success: results.some(r => r.success),
            reason: 'Any condition can be true'
          };
        case 'NOT':
          return {
            success: !results.some(r => r.success),
            reason: 'No conditions should be true'
          };
        case 'XOR':
          return {
            success: results.filter(r => r.success).length === 1,
            reason: 'Exactly one condition must be true'
          };
        case 'NAND':
          return {
            success: !results.every(r => r.success),
            reason: 'Not all conditions should be true'
          };
        case 'NOR':
          return {
            success: !results.some(r => r.success),
            reason: 'None of the conditions should be true'
          };
        default:
          return { success: false, reason: `Unknown logical operator: ${group.logic_operator}` };
      }
    } catch (error) {
      return { success: false, reason: `Group evaluation error: ${error.message}` };
    }
  }

  /**
   * Calculates adjustments based on rule evaluation
   */
  calculateAdjustments(rule, baseAmount) {
    if (!rule.adjustment_amount) return baseAmount;

    const amount = Number(rule.adjustment_amount);
    if (isNaN(amount)) return baseAmount;

    return baseAmount + amount;
  }
}

export default new RuleEngine();