import { rulesApi, customerServiceApi, handleApiError } from '../utils/apiClient';

const logDebug = (context, message, data) => {
  if (data === undefined) {
    console.log(`[DEBUG][${context}] ${message}`);
  } else {
    try {
      const stringifiedData = JSON.stringify(data, null, 2);
      console.log(`[DEBUG][${context}] ${message}`, stringifiedData);
    } catch (err) {
      console.log(`[DEBUG][${context}] ${message} (unstringifiable data):`, data);
    }
  }
};

const logError = (context, message, error) => {
  console.error(`[ERROR][${context}] ${message}`);
  if (error?.response) {
    try {
      console.error(`[ERROR][${context}] Response status:`, error.response.status);
      console.error(`[ERROR][${context}] Response data:`, JSON.stringify(error.response.data, null, 2));
    } catch (err) {
      console.error(`[ERROR][${context}] Response data (unstringifiable):`, error.response.data);
    }
  }
  if (error?.stack) {
    console.error(`[ERROR][${context}] Stack trace:`, error.stack);
  }
};

const transformChoices = (data, context = 'unknown') => {
  logDebug('transformChoices', `Transforming choices for ${context}, input data:`, data);
  logDebug('transformChoices', `Input data type: ${typeof data}, isArray: ${Array.isArray(data)}`);
  
  // If data is already an array of { value, label } objects, return it
  if (Array.isArray(data) && data.length > 0 && 'value' in data[0] && 'label' in data[0]) {
    logDebug('transformChoices', 'Data is already in correct format:', data);
    return data;
  }
  
  // If data is an array of [value, label] tuples
  if (Array.isArray(data) && Array.isArray(data[0])) {
    logDebug('transformChoices', 'Data is array of tuples, transforming...');
    const transformed = data.map(([value, label], index) => {
      const result = { 
        value: String(value), 
        label: String(label) 
      };
      logDebug('transformChoices', `Transformed tuple ${index}:`, {
        original: [value, label],
        transformed: result
      });
      return result;
    });
    logDebug('transformChoices', 'Final transformed array result:', transformed);
    return transformed;
  }
  
  // If data is an object with key-value pairs
  if (typeof data === 'object' && data !== null) {
    logDebug('transformChoices', 'Data is object, transforming...');
    
    // Special case for operator choices which come as { operators: [{value, label}, ...] }
    if ('operators' in data && Array.isArray(data.operators)) {
      logDebug('transformChoices', 'Found operators array, returning directly:', data.operators);
      return data.operators;
    }

    // Handle regular object with nested label/type properties
    const entries = Object.entries(data);
    logDebug('transformChoices', 'Object entries:', entries);
    const transformed = entries.map(([key, value], index) => {
      // Handle nested objects with label property
      const label = typeof value === 'object' && value !== null && 'label' in value
        ? value.label
        : String(value);
        
      const result = { 
        value: String(key), 
        label: String(label)
      };
      logDebug('transformChoices', `Transformed entry ${index}:`, {
        original: { key, value },
        transformed: result
      });
      return result;
    });
    logDebug('transformChoices', 'Final transformed object result:', transformed);
    return transformed;
  }
  
  // Default to empty array if data is in an unexpected format
  logError('transformChoices', 'Unexpected data format:', data);
  return [];
};

const rulesService = {
  // Rule Groups
  getRuleGroups: async () => {
    try {
      logDebug('getRuleGroups', 'Fetching rule groups...');
      const data = await rulesApi.listGroups();
      logDebug('getRuleGroups', 'Rule groups data:', data);
      const result = Array.isArray(data) ? data : [];
      logDebug('getRuleGroups', 'Processed result:', result);
      return result;
    } catch (error) {
      logError('getRuleGroups', 'Error fetching rule groups:', error);
      throw handleApiError(error);
    }
  },

  getRuleGroup: async (id) => {
    try {
      logDebug('getRuleGroup', `Fetching rule group with id: ${id}`);
      const result = await rulesApi.getGroup(id);
      logDebug('getRuleGroup', 'Rule group data:', result);
      return result;
    } catch (error) {
      logError('getRuleGroup', `Error fetching rule group ${id}:`, error);
      throw handleApiError(error);
    }
  },

  createRuleGroup: async (data) => {
    try {
      logDebug('createRuleGroup', 'Creating rule group with data:', data);
      const payload = {
        customer_service: data.customer_service,
        logic_operator: data.logic_operator
      };
      logDebug('createRuleGroup', 'Processed payload:', payload);
      const result = await rulesApi.createGroup(payload);
      logDebug('createRuleGroup', 'Created rule group:', result);
      return result;
    } catch (error) {
      logError('createRuleGroup', 'Error creating rule group:', error);
      throw handleApiError(error);
    }
  },

  updateRuleGroup: async (id, data) => {
    try {
      logDebug('updateRuleGroup', `Updating rule group ${id} with data:`, data);
      const result = await rulesApi.updateGroup(id, data);
      logDebug('updateRuleGroup', 'Updated rule group:', result);
      return result;
    } catch (error) {
      logError('updateRuleGroup', `Error updating rule group ${id}:`, error);
      throw handleApiError(error);
    }
  },

  deleteRuleGroup: async (id) => {
    try {
      logDebug('deleteRuleGroup', `Deleting rule group ${id}`);
      await rulesApi.deleteGroup(id);
      logDebug('deleteRuleGroup', `Successfully deleted rule group ${id}`);
    } catch (error) {
      logError('deleteRuleGroup', `Error deleting rule group ${id}:`, error);
      throw handleApiError(error);
    }
  },

  // Basic Rules
  getRules: async (groupId) => {
    try {
      logDebug('getRules', `Fetching rules for group ${groupId}`);
      const result = await rulesApi.listRules(groupId);
      logDebug('getRules', 'Rules data:', result);
      return result;
    } catch (error) {
      logError('getRules', `Error fetching rules for group ${groupId}:`, error);
      throw handleApiError(error);
    }
  },

  createRule: async (groupId, data) => {
    try {
      logDebug('createRule', `Creating rule for group ${groupId} with data:`, data);
      const result = await rulesApi.createRule(groupId, data);
      logDebug('createRule', 'Created rule:', result);
      return result;
    } catch (error) {
      logError('createRule', `Error creating rule for group ${groupId}:`, error);
      throw handleApiError(error);
    }
  },

  updateRule: async (id, data) => {
    try {
      logDebug('updateRule', `Updating rule ${id} with data:`, data);
      const result = await rulesApi.updateRule(id, data);
      logDebug('updateRule', 'Updated rule:', result);
      return result;
    } catch (error) {
      logError('updateRule', `Error updating rule ${id}:`, error);
      throw handleApiError(error);
    }
  },

  deleteRule: async (id) => {
    try {
      logDebug('deleteRule', `Deleting rule ${id}`);
      await rulesApi.deleteRule(id);
      logDebug('deleteRule', `Successfully deleted rule ${id}`);
    } catch (error) {
      logError('deleteRule', `Error deleting rule ${id}:`, error);
      throw handleApiError(error);
    }
  },

  // Advanced Rules
  getAdvancedRules: async (groupId) => {
    try {
      logDebug('getAdvancedRules', `Fetching advanced rules for group ${groupId}`);
      const result = await rulesApi.listAdvancedRules(groupId);
      logDebug('getAdvancedRules', 'Advanced rules data:', result);
      return result;
    } catch (error) {
      logError('getAdvancedRules', `Error fetching advanced rules for group ${groupId}:`, error);
      throw handleApiError(error);
    }
  },

  createAdvancedRule: async (groupId, data) => {
    try {
      logDebug('createAdvancedRule', `Creating advanced rule for group ${groupId} with data:`, data);
      const result = await rulesApi.createAdvancedRule(groupId, data);
      logDebug('createAdvancedRule', 'Created advanced rule:', result);
      return result;
    } catch (error) {
      logError('createAdvancedRule', `Error creating advanced rule for group ${groupId}:`, error);
      throw handleApiError(error);
    }
  },

  updateAdvancedRule: async (id, data) => {
    try {
      logDebug('updateAdvancedRule', `Updating advanced rule ${id} with data:`, data);
      const result = await rulesApi.updateAdvancedRule(id, data);
      logDebug('updateAdvancedRule', 'Updated advanced rule:', result);
      return result;
    } catch (error) {
      logError('updateAdvancedRule', `Error updating advanced rule ${id}:`, error);
      throw handleApiError(error);
    }
  },

  deleteAdvancedRule: async (id) => {
    try {
      logDebug('deleteAdvancedRule', `Deleting advanced rule ${id}`);
      await rulesApi.deleteAdvancedRule(id);
      logDebug('deleteAdvancedRule', `Successfully deleted advanced rule ${id}`);
    } catch (error) {
      logError('deleteAdvancedRule', `Error deleting advanced rule ${id}:`, error);
      throw handleApiError(error);
    }
  },

  // Utility Endpoints
  getOperatorChoices: async (field) => {
    try {
      logDebug('getOperatorChoices', `Fetching operator choices for field: ${field}`);
      const data = await rulesApi.getOperatorChoices(field);
      logDebug('getOperatorChoices', 'Raw operator choices:', data);
      const result = transformChoices(data, 'operators');
      logDebug('getOperatorChoices', 'Transformed operator choices:', result);
      return result;
    } catch (error) {
      logError('getOperatorChoices', `Error fetching operator choices for field ${field}:`, error);
      throw handleApiError(error);
    }
  },

  validateConditions: async (conditions) => {
    try {
      logDebug('validateConditions', 'Validating conditions:', conditions);
      const result = await rulesApi.validateConditions(conditions);
      logDebug('validateConditions', 'Validation result:', result);
      return result;
    } catch (error) {
      logError('validateConditions', 'Error validating conditions:', error);
      throw handleApiError(error);
    }
  },

  validateCalculations: async (calculations) => {
    try {
      logDebug('validateCalculations', 'Validating calculations:', calculations);
      const result = await rulesApi.validateCalculations(calculations);
      logDebug('validateCalculations', 'Validation result:', result);
      return result;
    } catch (error) {
      logError('validateCalculations', 'Error validating calculations:', error);
      throw handleApiError(error);
    }
  },

  getConditionsSchema: async () => {
    try {
      logDebug('getConditionsSchema', 'Fetching conditions schema');
      const result = await rulesApi.getConditionsSchema();
      logDebug('getConditionsSchema', 'Schema data:', result);
      return result;
    } catch (error) {
      logError('getConditionsSchema', 'Error fetching conditions schema:', error);
      throw handleApiError(error);
    }
  },

  getCalculationsSchema: async () => {
    try {
      logDebug('getCalculationsSchema', 'Fetching calculations schema');
      const result = await rulesApi.getCalculationsSchema();
      logDebug('getCalculationsSchema', 'Schema data:', result);
      return result;
    } catch (error) {
      logError('getCalculationsSchema', 'Error fetching calculations schema:', error);
      throw handleApiError(error);
    }
  },

  getAvailableFields: async () => {
    try {
      logDebug('getAvailableFields', 'Fetching available fields');
      const data = await rulesApi.getAvailableFields();
      logDebug('getAvailableFields', 'Raw fields data:', data);
      const result = transformChoices(data, 'fields');
      logDebug('getAvailableFields', 'Transformed fields:', result);
      return result;
    } catch (error) {
      logError('getAvailableFields', 'Error fetching available fields:', error);
      throw handleApiError(error);
    }
  },

  getCalculationTypes: async () => {
    try {
      logDebug('getCalculationTypes', 'Fetching calculation types');
      const data = await rulesApi.getCalculationTypes();
      logDebug('getCalculationTypes', 'Raw calculation types:', data);
      const result = transformChoices(data, 'calculationTypes');
      logDebug('getCalculationTypes', 'Transformed calculation types:', result);
      return result;
    } catch (error) {
      logError('getCalculationTypes', 'Error fetching calculation types:', error);
      throw handleApiError(error);
    }
  },

  validateRuleValue: async (data) => {
    try {
      logDebug('validateRuleValue', 'Validating rule value:', data);
      const result = await rulesApi.validateRuleValue(data);
      logDebug('validateRuleValue', 'Validation result:', result);
      return result;
    } catch (error) {
      logError('validateRuleValue', 'Error validating rule value:', error);
      throw handleApiError(error);
    }
  },

  getCustomerSkus: async (groupId) => {
    try {
      logDebug('getCustomerSkus', `Fetching customer SKUs for group ${groupId}`);
      const result = await rulesApi.getCustomerSkus(groupId);
      logDebug('getCustomerSkus', 'Customer SKUs data:', result);
      return result;
    } catch (error) {
      logError('getCustomerSkus', `Error fetching customer SKUs for group ${groupId}:`, error);
      throw handleApiError(error);
    }
  },

  // Customer Services
  getCustomerServices: async () => {
    try {
      logDebug('getCustomerServices', 'Fetching customer services');
      const response = await customerServiceApi.list();
      logDebug('getCustomerServices', 'Customer services response:', response);
      
      // Handle both response formats (with and without success property)
      const services = response.success ? response.data : response;
      
      if (!Array.isArray(services)) {
        throw new Error('Invalid response format: expected array of customer services');
      }
      
      return services;
    } catch (error) {
      logError('getCustomerServices', 'Error fetching customer services:', error);
      throw handleApiError(error);
    }
  }
};

export default rulesService;