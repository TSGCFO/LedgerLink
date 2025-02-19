import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  CircularProgress,
  Alert,
  Typography,
  IconButton,
  Divider,
  Tooltip,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormHelperText,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Help as HelpIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';

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
      const [
        availableFields,
        availableCalculationTypes,
        conditionsSchemaData,
      ] = await Promise.all([
        rulesService.getAvailableFields(),
        rulesService.getCalculationTypes(),
        rulesService.getConditionsSchema(),
      ]);
      
      setFields(availableFields);
      setCalculationTypes(availableCalculationTypes);
      setConditionsSchema(conditionsSchemaData);
    } catch (err) {
      setError('Failed to fetch initial data. Please try again.');
      console.error('Error fetching initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchOperators = async (field) => {
    try {
      const availableOperators = await rulesService.getOperatorChoices(field);
      setOperators(availableOperators);
      if (!availableOperators.find(op => op.value === formData.operator)) {
        setFormData(prev => ({ ...prev, operator: '' }));
      }
    } catch (err) {
      console.error('Error fetching operators:', err);
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
    const errors = {};
    
    switch (step) {
      case 0: // Basic Rule
        if (!formData.field) errors.field = 'Field is required';
        if (!formData.operator) errors.operator = 'Operator is required';
        if (!formData.value) errors.value = 'Value is required';
        break;
      case 1: // Conditions
        // Validate each condition has all required fields
        Object.entries(formData.conditions).forEach(([field, criteria], index) => {
          if (!field) errors[`condition_${index}_field`] = 'Field is required';
          const [operator, value] = Object.entries(criteria)[0] || ['', ''];
          if (!operator) errors[`condition_${index}_operator`] = 'Operator is required';
          if (!value) errors[`condition_${index}_value`] = 'Value is required';
        });
        break;
      case 2: // Calculations
        formData.calculations.forEach((calc, index) => {
          if (!calc.type) errors[`calculation_${index}_type`] = 'Calculation type is required';
          if (!calc.value) errors[`calculation_${index}_value`] = 'Value is required';
        });
        break;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
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

  const renderBasicRule = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Basic Rule Settings
        <Tooltip title={HELP_TEXTS.field}>
          <IconButton size="small" onClick={() => setHelpOpen({ ...helpOpen, field: true })}>
            <HelpIcon />
          </IconButton>
        </Tooltip>
      </Typography>
      
      <Box display="flex" gap={2}>
        <FormControl fullWidth required error={!!validationErrors.field}>
          <InputLabel>Field</InputLabel>
          <Select
            name="field"
            value={formData.field}
            onChange={handleBasicFieldChange}
            label="Field"
          >
            {fields.map((field) => (
              <MenuItem key={field.value} value={field.value}>
                {field.label}
                <Tooltip title={EXAMPLES.field[field.value] || ''}>
                  <IconButton size="small">
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>{validationErrors.field}</FormHelperText>
        </FormControl>

        <FormControl fullWidth required disabled={!formData.field}>
          <InputLabel>Operator</InputLabel>
          <Select
            name="operator"
            value={formData.operator}
            onChange={handleBasicFieldChange}
            label="Operator"
          >
            {operators.map((operator) => (
              <MenuItem key={operator.value} value={operator.value}>
                {operator.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          fullWidth
          required
          label="Value"
          name="value"
          value={formData.value}
          onChange={handleBasicFieldChange}
          disabled={!formData.operator}
        />
      </Box>
    </Box>
  );

  const renderConditions = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Additional Conditions
        </Typography>
        <Button
          startIcon={<AddIcon />}
          onClick={handleConditionAdd}
        >
          Add Condition
        </Button>
      </Box>

      {Object.entries(formData.conditions).map(([field, criteria], index) => {
        const [operator, value] = Object.entries(criteria)[0] || ['', ''];
        return (
          <Box key={index} display="flex" gap={2} mb={2}>
            <FormControl fullWidth>
              <InputLabel>Field</InputLabel>
              <Select
                value={field}
                onChange={(e) => handleConditionChange(field, e.target.value, operator, value)}
                label="Field"
              >
                {fields.map((f) => (
                  <MenuItem key={f.value} value={f.value}>
                    {f.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Operator</InputLabel>
              <Select
                value={operator}
                onChange={(e) => handleConditionChange(field, field, e.target.value, value)}
                label="Operator"
              >
                {operators.map((op) => (
                  <MenuItem key={op.value} value={op.value}>
                    {op.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Value"
              value={value}
              onChange={(e) => handleConditionChange(field, field, operator, e.target.value)}
            />

            <IconButton
              color="error"
              onClick={() => handleConditionRemove(field)}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        );
      })}
    </Box>
  );

  const renderCalculations = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Calculations
        </Typography>
        <Button
          startIcon={<AddIcon />}
          onClick={handleCalculationAdd}
        >
          Add Calculation
        </Button>
      </Box>

      {formData.calculations.map((calc, index) => (
        <Box key={index} display="flex" gap={2} mb={2}>
          <FormControl fullWidth>
            <InputLabel>Type</InputLabel>
            <Select
              value={calc.type}
              onChange={(e) => handleCalculationChange(index, 'type', e.target.value)}
              label="Type"
            >
              {calculationTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {calc.type === 'case_based_tier' ? (
            <Box sx={{ width: '100%' }}>
              <Typography variant="subtitle2" gutterBottom>
                Case-Based Tiers
                <Tooltip title={HELP_TEXTS.caseTiers}>
                  <IconButton size="small">
                    <HelpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Typography>
              
              {formData.tier_config.ranges.map((tier, tierIndex) => (
                <Box key={tierIndex} display="flex" gap={2} mb={1}>
                  <TextField
                    label="Min Cases"
                    type="number"
                    value={tier.min}
                    onChange={(e) => handleTierChange(tierIndex, 'min', e.target.value)}
                    size="small"
                  />
                  <TextField
                    label="Max Cases"
                    type="number"
                    value={tier.max}
                    onChange={(e) => handleTierChange(tierIndex, 'max', e.target.value)}
                    size="small"
                  />
                  <TextField
                    label="Price Multiplier"
                    type="number"
                    value={tier.multiplier}
                    onChange={(e) => handleTierChange(tierIndex, 'multiplier', e.target.value)}
                    size="small"
                    inputProps={{ step: '0.1' }}
                  />
                  <IconButton
                    color="error"
                    onClick={() => handleTierRemove(tierIndex)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              
              <Button
                startIcon={<AddIcon />}
                onClick={handleTierAdd}
                size="small"
                sx={{ mt: 1 }}
              >
                Add Tier
              </Button>

              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Excluded SKUs
                  <Tooltip title={HELP_TEXTS.excludedSkus}>
                    <IconButton size="small">
                      <HelpIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <TextField
                  fullWidth
                  label="Excluded SKUs"
                  value={formData.tier_config.excluded_skus.join(';')}
                  onChange={handleExcludedSkusChange}
                  helperText="Enter SKUs separated by semicolons (;)"
                  size="small"
                />
              </Box>
            </Box>
          ) : (
            <TextField
              fullWidth
              label="Value"
              type="number"
              value={calc.value}
              onChange={(e) => handleCalculationChange(index, 'value', e.target.value)}
              inputProps={{ step: '0.01' }}
            />
          )}

          <IconButton
            color="error"
            onClick={() => handleCalculationRemove(index)}
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      ))}
    </Box>
  );

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