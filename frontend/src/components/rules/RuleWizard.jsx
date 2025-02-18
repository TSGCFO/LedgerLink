import React from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Paper
} from '@mui/material';

const steps = ['Select Field', 'Choose Operator', 'Set Value', 'Configure Adjustment'];

// Field options from the Django model
const fieldOptions = [
  { value: 'reference_number', label: 'Reference Number', type: 'string' },
  { value: 'ship_to_name', label: 'Ship To Name', type: 'string' },
  { value: 'ship_to_company', label: 'Ship To Company', type: 'string' },
  { value: 'ship_to_city', label: 'Ship To City', type: 'string' },
  { value: 'ship_to_state', label: 'Ship To State', type: 'string' },
  { value: 'ship_to_country', label: 'Ship To Country', type: 'string' },
  { value: 'weight_lb', label: 'Weight (lb)', type: 'number' },
  { value: 'line_items', label: 'Line Items', type: 'number' },
  { value: 'sku_quantity', label: 'SKU Quantity', type: 'sku' },
  { value: 'total_item_qty', label: 'Total Item Quantity', type: 'number' },
  { value: 'packages', label: 'Packages', type: 'number' },
  { value: 'notes', label: 'Notes', type: 'string' },
  { value: 'carrier', label: 'Carrier', type: 'string' },
  { value: 'volume_cuft', label: 'Volume (cuft)', type: 'number' }
];

// Operator options based on field type
const operatorsByType = {
  string: [
    { value: 'eq', label: 'Equals' },
    { value: 'ne', label: 'Not equals' },
    { value: 'in', label: 'In' },
    { value: 'ni', label: 'Not in' },
    { value: 'contains', label: 'Contains' },
    { value: 'ncontains', label: 'Not contains' },
    { value: 'startswith', label: 'Starts with' },
    { value: 'endswith', label: 'Ends with' }
  ],
  number: [
    { value: 'gt', label: 'Greater than' },
    { value: 'lt', label: 'Less than' },
    { value: 'eq', label: 'Equals' },
    { value: 'ne', label: 'Not equals' },
    { value: 'ge', label: 'Greater than or equals' },
    { value: 'le', label: 'Less than or equals' }
  ],
  sku: [
    { value: 'contains', label: 'Contains' },
    { value: 'ncontains', label: 'Not contains' },
    { value: 'only_contains', label: 'Only Contains' }
  ]
};

const RuleWizard = ({ onClose, onSave }) => {
  const [activeStep, setActiveStep] = React.useState(0);
  const [ruleData, setRuleData] = React.useState({
    field: '',
    operator: '',
    value: '',
    adjustment_amount: ''
  });
  const [error, setError] = React.useState('');

  const handleNext = () => {
    if (validateCurrentStep()) {
      setActiveStep((prevStep) => prevStep + 1);
      setError('');
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
    setError('');
  };

  const validateCurrentStep = () => {
    switch (activeStep) {
      case 0:
        if (!ruleData.field) {
          setError('Please select a field');
          return false;
        }
        break;
      case 1:
        if (!ruleData.operator) {
          setError('Please select an operator');
          return false;
        }
        break;
      case 2:
        if (!ruleData.value) {
          setError('Please enter a value');
          return false;
        }
        break;
      case 3:
        if (ruleData.adjustment_amount === '') {
          setError('Please enter an adjustment amount');
          return false;
        }
        break;
    }
    return true;
  };

  const handleFieldChange = (event) => {
    const field = event.target.value;
    setRuleData({
      ...ruleData,
      field,
      operator: '', // Reset operator when field changes
      value: '' // Reset value when field changes
    });
  };

  const handleOperatorChange = (event) => {
    setRuleData({
      ...ruleData,
      operator: event.target.value,
      value: '' // Reset value when operator changes
    });
  };

  const handleValueChange = (event) => {
    setRuleData({
      ...ruleData,
      value: event.target.value
    });
  };

  const handleAdjustmentChange = (event) => {
    setRuleData({
      ...ruleData,
      adjustment_amount: event.target.value
    });
  };

  const handleFinish = () => {
    if (validateCurrentStep()) {
      onSave(ruleData);
      onClose();
    }
  };

  const renderFieldSelect = () => (
    <FormControl fullWidth>
      <InputLabel>Field</InputLabel>
      <Select
        value={ruleData.field}
        onChange={handleFieldChange}
        label="Field"
      >
        {fieldOptions.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );

  const renderOperatorSelect = () => {
    const selectedField = fieldOptions.find(f => f.value === ruleData.field);
    const operators = selectedField ? operatorsByType[selectedField.type] : [];
    return (
      <FormControl fullWidth>
        <InputLabel>Operator</InputLabel>
        <Select
          value={ruleData.operator}
          onChange={handleOperatorChange}
          label="Operator"
        >
          {operators.map((op) => (
            <MenuItem key={op.value} value={op.value}>
              {op.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  };

  const renderValueInput = () => {
    const fieldType = fieldOptions.find(f => f.value === ruleData.field)?.type;
    return (
      <TextField
        fullWidth
        label="Value"
        value={ruleData.value}
        onChange={handleValueChange}
        type={fieldType === 'number' ? 'number' : 'text'}
        helperText={fieldType === 'sku' ? 'For multiple SKUs, separate with semicolon (;)' : ''}
      />
    );
  };

  const renderAdjustmentInput = () => (
    <TextField
      fullWidth
      label="Adjustment Amount"
      value={ruleData.adjustment_amount}
      onChange={handleAdjustmentChange}
      type="number"
      inputProps={{ step: '0.01' }}
      helperText="Enter the amount to adjust the price"
    />
  );

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return renderFieldSelect();
      case 1:
        return renderOperatorSelect();
      case 2:
        return renderValueInput();
      case 3:
        return renderAdjustmentInput();
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        {getStepContent(activeStep)}
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2 }}>
        <Button
          color="inherit"
          onClick={onClose}
          sx={{ mr: 1 }}
        >
          Cancel
        </Button>
        <Box>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleFinish}
            >
              Finish
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleNext}
            >
              Next
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

RuleWizard.propTypes = {
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired
};

export default RuleWizard;