import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  CircularProgress,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import BasicRuleForm from './BasicRuleForm';
import ConditionBuilder from './ConditionBuilder';
import CalculationBuilder from './CalculationBuilder';
// Import RuleTester component when needed
import RuleTester from './RuleTester';
import rulesService from '../../services/rulesService';
import { validateRuleValue, validateCalculation, validateConditions } from '../../utils/validationUtils';

const HELP_TEXTS = {
  field: 'Select the order field to evaluate. This determines what aspect of the order will be checked.',
  operator: 'Choose how to compare the field value. Different fields support different operators.',
  value: 'Enter the value to compare against. Format depends on the selected field and operator.',
  conditions: 'Add additional conditions that must be met for this rule to apply.',
  calculations: 'Define how to calculate the final price when this rule applies.',
  caseTiers: 'Set up pricing tiers based on the number of cases in an order.',
  excludedSkus: 'List any SKUs that should not be counted in case calculations.',
};

const EXAMPLES = {
  field: {
    'weight_lb': 'Example: Check if order weight is greater than 50 lbs',
    'sku_quantity': 'Example: Check if order contains specific SKUs',
    'total_item_qty': 'Example: Check if total items exceed 100 units',
  },
  operator: {
    'gt': 'Example: weight_lb > 50',
    'contains': 'Example: sku_quantity contains "SKU-123"',
    'between': 'Example: total_item_qty between 100 and 500',
  },
};

const AdvancedRuleBuilder = ({ groupId, initialData, onSubmit, onCancel }) => {
  console.log('AdvancedRuleBuilder initialized with:', { groupId, initialData });
  
  const [formData, setFormData] = useState({
    field: '',
    operator: '',
    value: '',
    conditions: {},
    calculations: [],
    tier_config: {
      ranges: [],
      excluded_skus: []
    },
    ...initialData,
  });
  const [fields, setFields] = useState([]);
  const [operators, setOperators] = useState([]);
  const [calculationTypes, setCalculationTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conditionsSchema, setConditionsSchema] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [validationErrors, setValidationErrors] = useState({});
  const [helpOpen, setHelpOpen] = useState({});

  useEffect(() => {
    console.log('Fetching initial data for AdvancedRuleBuilder');
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (formData.field) {
      fetchOperators(formData.field);
    }
  }, [formData.field]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      console.log('Starting to fetch fields, calculation types, and schema...');
      
      try {
        const availableFields = await rulesService.getAvailableFields();
        console.log('Available fields fetched:', availableFields);
        setFields(availableFields);
      } catch (fieldErr) {
        console.error('Error fetching available fields:', fieldErr);
        setError('Failed to fetch field options. Please try again.');
      }
      
      try {
        const availableCalculationTypes = await rulesService.getCalculationTypes();
        console.log('Available calculation types fetched:', availableCalculationTypes);
        setCalculationTypes(availableCalculationTypes);
      } catch (calcErr) {
        console.error('Error fetching calculation types:', calcErr);
        setError('Failed to fetch calculation types. Please try again.');
      }
      
      try {
        const conditionsSchemaData = await rulesService.getConditionsSchema();
        console.log('Conditions schema fetched:', conditionsSchemaData);
        setConditionsSchema(conditionsSchemaData);
      } catch (schemaErr) {
        console.error('Error fetching conditions schema:', schemaErr);
        setError('Failed to fetch conditions schema. Please try again.');
      }
      
    } catch (err) {
      setError('Failed to fetch initial data. Please try again.');
      console.error('Error in fetchInitialData:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchOperators = async (field) => {
    try {
      console.log('Fetching operators for field:', field);
      const availableOperators = await rulesService.getOperatorChoices(field);
      console.log('Available operators fetched:', availableOperators);
      
      // Check if operators is in the right format
      if (availableOperators && availableOperators.operators && Array.isArray(availableOperators.operators)) {
        console.log('Setting operators from operators property:', availableOperators.operators);
        setOperators(availableOperators.operators);
        
        // Reset operator if current one is not valid for the new field
        if (formData.operator && !availableOperators.operators.find(op => op.value === formData.operator)) {
          console.log('Current operator not valid for this field, resetting');
          setFormData(prev => ({ ...prev, operator: '' }));
        }
      } else if (Array.isArray(availableOperators)) {
        console.log('Setting operators from array:', availableOperators);
        setOperators(availableOperators);
        
        // Reset operator if current one is not valid for the new field
        if (formData.operator && !availableOperators.find(op => op.value === formData.operator)) {
          console.log('Current operator not valid for this field, resetting');
          setFormData(prev => ({ ...prev, operator: '' }));
        }
      } else {
        console.error('Unexpected operators format:', availableOperators);
        setError('Received invalid operators format from the server');
      }
    } catch (err) {
      console.error('Error fetching operators:', err);
      setError(`Failed to fetch operators for field "${field}". Please try again.`);
    }
  };

  const handleBasicFieldChange = async (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    if (name === 'value') {
      try {
        await rulesService.validateRuleValue({
          field: formData.field,
          operator: formData.operator,
          value
        });
        setError(null);
      } catch (err) {
        setError('Invalid value format for selected field and operator.');
      }
    }
  };

  const handleConditionAdd = () => {
    setFormData(prev => ({
      ...prev,
      conditions: {
        ...prev.conditions,
        ['']: { '': '' }
      }
    }));
  };

  const handleConditionChange = (oldField, field, operator, value) => {
    setFormData(prev => {
      const newConditions = { ...prev.conditions };
      if (oldField !== field) {
        delete newConditions[oldField];
      }
      newConditions[field] = { [operator]: value };
      return { ...prev, conditions: newConditions };
    });
  };

  const handleConditionRemove = (field) => {
    setFormData(prev => {
      const newConditions = { ...prev.conditions };
      delete newConditions[field];
      return { ...prev, conditions: newConditions };
    });
  };

  const handleCalculationAdd = () => {
    setFormData(prev => ({
      ...prev,
      calculations: [...prev.calculations, { type: '', value: '' }]
    }));
  };

  const handleCalculationChange = (index, field, value) => {
    setFormData(prev => {
      const newCalculations = [...prev.calculations];
      newCalculations[index] = {
        ...newCalculations[index],
        [field]: value
      };

      // Initialize tier_config when selecting case_based_tier
      if (field === 'type' && value === 'case_based_tier') {
        newCalculations[index] = {
          ...newCalculations[index],
          value: 1, // Default value
          tier_config: {
            ranges: [
              { min: 1, max: 1, multiplier: 1.0 },
              { min: 2, max: 4, multiplier: 2.0 },
              { min: 5, max: 6, multiplier: 3.0 },
              { min: 7, max: 8, multiplier: 4.0 }
            ],
            excluded_skus: []
          }
        };
      }

      return { ...prev, calculations: newCalculations };
    });
  };

  const handleCalculationRemove = (index) => {
    setFormData(prev => ({
      ...prev,
      calculations: prev.calculations.filter((_, i) => i !== index)
    }));
  };

  const handleTierAdd = () => {
    setFormData(prev => ({
      ...prev,
      tier_config: {
        ...prev.tier_config,
        ranges: [
          ...prev.tier_config.ranges,
          { min: 0, max: 0, multiplier: 1.0 }
        ]
      }
    }));
  };

  const handleTierChange = (index, field, value) => {
    setFormData(prev => {
      const newRanges = [...prev.tier_config.ranges];
      newRanges[index] = {
        ...newRanges[index],
        [field]: Number(value)
      };
      return {
        ...prev,
        tier_config: {
          ...prev.tier_config,
          ranges: newRanges
        }
      };
    });
  };

  const handleTierRemove = (index) => {
    setFormData(prev => ({
      ...prev,
      tier_config: {
        ...prev.tier_config,
        ranges: prev.tier_config.ranges.filter((_, i) => i !== index)
      }
    }));
  };

  const handleExcludedSkusChange = (event) => {
    const skus = event.target.value.split(';').map(sku => sku.trim()).filter(Boolean);
    setFormData(prev => ({
      ...prev,
      tier_config: {
        ...prev.tier_config,
        excluded_skus: skus
      }
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setLoading(true);
      
      // Format the data for submission
      const submissionData = {
        ...formData,
        calculations: formData.calculations.map(calc => {
          if (calc.type === 'case_based_tier') {
            return {
              type: calc.type,
              value: calc.value,
              tier_config: formData.tier_config
            };
          }
          return calc;
        })
      };

      // Validate conditions and calculations
      await Promise.all([
        rulesService.validateConditions(submissionData.conditions),
        rulesService.validateCalculations(submissionData.calculations)
      ]);

      if (initialData) {
        await onSubmit(initialData.id, submissionData);
      } else {
        await onSubmit(submissionData);
      }
      setError(null);
    } catch (err) {
      setError('Failed to save advanced rule. Please check your inputs and try again.');
      console.error('Error saving advanced rule:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const validateStep = (step) => {
    console.log(`Validating step ${step}`);
    const errors = {};
    
    try {
      switch (step) {
        case 0: // Basic Rule
          if (!formData.field) errors.field = 'Field is required';
          if (!formData.operator) errors.operator = 'Operator is required';
          if (!formData.value) errors.value = 'Value is required';
          break;
        case 1: // Conditions
          // Validate each condition has all required fields
          if (formData.conditions && typeof formData.conditions === 'object') {
            Object.entries(formData.conditions).forEach(([field, criteria], index) => {
              if (!field) errors[`condition_${index}_field`] = 'Field is required';
              
              // Safely handle criteria that might be undefined or not an object
              if (criteria && typeof criteria === 'object') {
                const entries = Object.entries(criteria);
                const [operator, value] = entries.length > 0 ? entries[0] : ['', ''];
                if (!operator) errors[`condition_${index}_operator`] = 'Operator is required';
                if (!value) errors[`condition_${index}_value`] = 'Value is required';
              } else {
                errors[`condition_${index}_operator`] = 'Operator is required';
                errors[`condition_${index}_value`] = 'Value is required';
              }
            });
          }
          break;
        case 2: // Calculations
          if (Array.isArray(formData.calculations)) {
            formData.calculations.forEach((calc, index) => {
              if (!calc || typeof calc !== 'object') {
                errors[`calculation_${index}`] = 'Invalid calculation format';
                return;
              }
              
              if (!calc.type) errors[`calculation_${index}_type`] = 'Calculation type is required';
              if (calc.value === undefined || calc.value === null || calc.value === '') {
                errors[`calculation_${index}_value`] = 'Value is required';
              }
            });
          }
          break;
        default:
          console.warn(`Unknown step: ${step}`);
      }

      console.log('Validation errors:', errors);
      setValidationErrors(errors);
      return Object.keys(errors).length === 0;
    } catch (err) {
      console.error('Error in validateStep:', err);
      setError('Validation error occurred. Please check your inputs.');
      return false;
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return renderBasicRule();
      case 1:
        return renderConditions();
      case 2:
        return renderCalculations();
      default:
        return null;
    }
  };

  // Memoize the fields array for better performance
  const formattedFields = useMemo(() => {
    if (!fields || typeof fields !== 'object') {
      console.error('Fields not in expected format:', fields);
      return [];
    }
    
    try {
      return Object.entries(fields).map(([value, info]) => ({
        value,
        label: info.label || value,
        description: (EXAMPLES.field && EXAMPLES.field[value]) || '',
        type: info.type || 'unknown'
      }));
    } catch (err) {
      console.error('Error formatting fields:', err);
      return [];
    }
  }, [fields]);
  
  // Memoize the operators array for better performance
  const formattedOperators = useMemo(() => {
    if (!operators) {
      console.error('Operators not available');
      return [];
    }
    
    try {
      // Handle both array format and object with operators property
      if (Array.isArray(operators)) {
        return operators.map(op => ({
          value: op.value,
          label: op.label
        }));
      } else if (operators.operators && Array.isArray(operators.operators)) {
        return operators.operators.map(op => ({
          value: op.value,
          label: op.label
        }));
      } else {
        console.error('Operators not in expected format:', operators);
        return [];
      }
    } catch (err) {
      console.error('Error formatting operators:', err);
      return [];
    }
  }, [operators]);
  
  // Handle field changes with named parameters
  const handleNamedFieldChange = useCallback((name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const renderBasicRule = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Basic Rule Settings
      </Typography>
      
      <BasicRuleForm
        field={formData.field}
        operator={formData.operator}
        value={formData.value}
        availableFields={formattedFields}
        availableOperators={formattedOperators}
        onChange={handleNamedFieldChange}
        errors={validationErrors}
      />
    </Box>
  );

  const renderConditions = () => {
    // Ensure we have valid operators data before rendering
    if (!formattedOperators || !Array.isArray(formattedOperators) || formattedOperators.length === 0) {
      console.warn('No valid operators available:', formattedOperators);
      return (
        <Box p={2}>
          <Typography color="error">
            Unable to load operators. Please select a field first.
          </Typography>
        </Box>
      );
    }
    
    return (
      <ConditionBuilder
        conditions={formData.conditions}
        fields={formattedFields}
        operators={formattedOperators}
        onConditionAdd={handleConditionAdd}
        onConditionChange={handleConditionChange}
        onConditionRemove={handleConditionRemove}
        errors={validationErrors}
      />
    );
  };

  // Format calculation types for the component
  const formattedCalculationTypes = useMemo(() => {
    // Check if calculationTypes exists and is an object
    if (!calculationTypes || typeof calculationTypes !== 'object') {
      console.warn('calculationTypes is not in expected format:', calculationTypes);
      return {};
    }
    
    // If it's already in the right format (an object with key-value pairs), return it directly
    if (!Array.isArray(calculationTypes)) {
      console.log('Using calculation types directly:', calculationTypes);
      return calculationTypes;
    }
    
    // If it's an array of objects with value and label properties, convert to object
    if (Array.isArray(calculationTypes) && calculationTypes.length > 0 && 'value' in calculationTypes[0]) {
      console.log('Converting array of objects to object format');
      return calculationTypes.reduce((acc, item) => {
        acc[item.value] = item.label;
        return acc;
      }, {});
    }
    
    // Otherwise convert from array of [key, value] entries to object
    console.log('Converting calculation types to object format');
    return Object.entries(calculationTypes).reduce((acc, [key, value]) => {
      acc[key] = value;
      return acc;
    }, {});
  }, [calculationTypes]);

  const renderCalculations = () => (
    <CalculationBuilder
      calculations={formData.calculations}
      tierConfig={formData.tier_config}
      calculationTypes={formattedCalculationTypes}
      onCalculationChange={handleCalculationChange}
      onCalculationAdd={handleCalculationAdd}
      onCalculationRemove={handleCalculationRemove}
      onTierChange={handleTierChange}
      onTierAdd={handleTierAdd}
      onTierRemove={handleTierRemove}
      onExcludedSkusChange={handleExcludedSkusChange}
      errors={validationErrors}
    />
  );

  // Rule tester toggle state and handler
  const [showRuleTester, setShowRuleTester] = useState(false);
  
  const handleToggleRuleTester = () => {
    setShowRuleTester(!showRuleTester);
  };

  if (loading && !formData.field) {
    return (
      <Dialog open fullWidth maxWidth="md">
        <DialogContent>
          <Box display="flex" justifyContent="center" p={2}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }
  
  return (
    <Dialog open onClose={onCancel} fullWidth maxWidth="md">
      <DialogTitle>
        {initialData ? 'Edit Advanced Rule' : 'Create Advanced Rule'}
      </DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            <Step>
              <StepLabel>
                Basic Rule
                <Typography variant="caption" display="block">
                  Define the primary condition for this rule
                </Typography>
              </StepLabel>
              <StepContent>
                {renderBasicRule()}
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Continue
                  </Button>
                </Box>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>
                Conditions
                <Typography variant="caption" display="block">
                  Add additional conditions that must be met for this rule to apply
                </Typography>
              </StepLabel>
              <StepContent>
                {renderConditions()}
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleBack}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    sx={{ mt: 1, ml: 1 }}
                  >
                    Continue
                  </Button>
                </Box>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>
                Calculations
                <Typography variant="caption" display="block">
                  Define how to calculate the final price when this rule applies
                </Typography>
              </StepLabel>
              <StepContent>
                {renderCalculations()}
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleBack}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    sx={{ mt: 1, ml: 1 }}
                  >
                    Continue
                  </Button>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
          
          {/* Show Rule Tester if formData is complete */}
          {formData.field && formData.operator && formData.value && (
            <Box mt={3}>
              <Button 
                variant="outlined" 
                color="secondary"
                onClick={handleToggleRuleTester}
                sx={{ mb: 2 }}
              >
                {showRuleTester ? "Hide Rule Tester" : "Test This Rule"}
              </Button>
              
              {showRuleTester && (
                <Box>
                  <RuleTester rule={formData} />
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onCancel}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !formData.field || !formData.operator || !formData.value}
          >
            {loading ? <CircularProgress size={24} /> : (initialData ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AdvancedRuleBuilder;