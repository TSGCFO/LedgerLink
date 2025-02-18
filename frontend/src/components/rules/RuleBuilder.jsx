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
} from '@mui/material';
import rulesService from '../../services/rulesService';

const RuleBuilder = ({ groupId, initialData, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    field: '',
    operator: '',
    value: '',
    adjustment_amount: '',
    ...(initialData ? {
      ...initialData,
      value: initialData.value || ''
    } : {})
  });
  const [fields, setFields] = useState([]);
  const [operators, setOperators] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFields();
  }, []);

  useEffect(() => {
    console.log('Field changed:', formData.field);
    if (formData.field) {
      fetchOperators(formData.field);
    }
  }, [formData.field]);

  const fetchFields = async () => {
    try {
      setLoading(true);
      const availableFields = await rulesService.getAvailableFields();
      console.log('Available fields:', availableFields);
      setFields(availableFields);
    } catch (err) {
      setError('Failed to fetch fields. Please try again.');
      console.error('Error fetching fields:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchOperators = async (field) => {
    try {
      console.log('Fetching operators for field:', field);
      const availableOperators = await rulesService.getOperatorChoices(field);
      console.log('Available operators:', availableOperators);
      setOperators(availableOperators);
      // Reset operator if current one is not valid for new field
      if (!availableOperators.find(op => op.value === formData.operator)) {
        setFormData(prev => ({ ...prev, operator: '' }));
      }
    } catch (err) {
      console.error('Error fetching operators:', err);
    }
  };

  const handleChange = async (event) => {
    const { name, value } = event.target;
    console.log('handleChange:', name, value);
    
    // Format the value if needed
    const formattedValue = formatValue(name, value);
    
    // Update form data immediately for UI responsiveness
    setFormData(prev => ({ ...prev, [name]: formattedValue }));

    // If field changed, operators will be fetched via useEffect and fields reset
    if (name === 'field') {
      setFormData(prev => ({
        ...prev,
        [name]: formattedValue,
        operator: '',
        value: isNumericField(formattedValue) ? '0' : '' // Initialize numeric fields with '0'
      }));
      return; // Skip validation as we're resetting fields
    }

    // For any field change that affects validation
    if (['field', 'operator', 'value'].includes(name)) {
      try {
        const updatedFormData = {
          field: name === 'field' ? formattedValue : formData.field,
          operator: name === 'operator' ? formattedValue : formData.operator,
          value: name === 'value' ? formattedValue : formData.value
        };
        
        // Only validate if we have all required fields
        if (updatedFormData.field && updatedFormData.operator && updatedFormData.value) {
          // For numeric fields, ensure the value is a valid number
          if (isNumericField(updatedFormData.field)) {
            const numValue = parseFloat(updatedFormData.value);
            if (isNaN(numValue)) {
              throw new Error('Value must be a valid number');
            }
            // Update with the parsed number to ensure proper format
            updatedFormData.value = numValue.toString();
          }
          
          await rulesService.validateRuleValue(updatedFormData);
          setError(null);
        } else {
          // Clear error if we don't have all fields yet
          setError(null);
        }
      } catch (err) {
        const errorMessage = err.response?.data?.error || err.message || 'Invalid value format for selected field and operator.';
        setError(errorMessage);
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setLoading(true);
      
      // Format data before submission
      const submissionData = {
        ...formData,
        value: isNumericField(formData.field)
          ? parseFloat(formData.value || 0).toString()
          : formData.value,
        adjustment_amount: formData.adjustment_amount
          ? parseFloat(formData.adjustment_amount).toString()
          : null
      };

      if (initialData) {
        await onSubmit(initialData.id, submissionData);
      } else {
        await onSubmit(submissionData);
      }
      setError(null);
      onCancel();
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to save rule. Please check your inputs and try again.';
      setError(errorMessage);
      console.error('Error saving rule:', err);
    } finally {
      setLoading(false);
    }
  };

  const isNumericField = (field) => {
    const numericFields = [
      'weight_lb',
      'line_items',
      'total_item_qty',
      'volume_cuft',
      'sku_count',
      'packages'
    ];
    return numericFields.includes(field);
  };

  const formatValue = (name, value) => {
    // Handle numeric fields
    if (name === 'value' && isNumericField(formData.field)) {
      // Convert empty string to 0
      if (value === '') return '0';
      // Ensure decimal format for numeric fields
      const num = parseFloat(value);
      return isNaN(num) ? '0' : num.toString();
    }
    return value;
  };

  if (loading && !formData.field) {
    return (
      <Dialog open fullWidth maxWidth="sm">
        <DialogContent>
          <Box display="flex" justifyContent="center" p={2}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open onClose={onCancel} fullWidth maxWidth="sm">
      <DialogTitle>
        {initialData ? 'Edit Rule' : 'Create Rule'}
      </DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2}>
            {error && (
              <Alert severity="error">
                {error}
              </Alert>
            )}

            <FormControl fullWidth required>
              <InputLabel>Field</InputLabel>
              <Select
                name="field"
                value={formData.field}
                onChange={handleChange}
                label="Field"
              >
                {fields.map((field) => (
                  <MenuItem key={field.value} value={field.value}>
                    {field.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth required disabled={!formData.field}>
              <InputLabel>Operator</InputLabel>
              <Select
                name="operator"
                value={formData.operator}
                onChange={handleChange}
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
              onChange={handleChange}
              disabled={!formData.operator}
              type={isNumericField(formData.field) ? 'number' : 'text'}
              helperText={formData.field === 'sku_quantity' ? 
                'For multiple values, separate with semicolon (;)' : ''}
            />

            <TextField
              fullWidth
              label="Adjustment Amount"
              name="adjustment_amount"
              value={formData.adjustment_amount}
              onChange={handleChange}
              type="number"
              inputProps={{ step: '0.01' }}
              helperText="Optional: Amount to adjust the price"
            />
          </Box>
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

export default RuleBuilder;