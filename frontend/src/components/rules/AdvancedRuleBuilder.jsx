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
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import rulesService from '../../services/rulesService';

const AdvancedRuleBuilder = ({ groupId, initialData, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    field: '',
    operator: '',
    value: '',
    conditions: {},
    calculations: [],
    ...initialData,
  });
  const [fields, setFields] = useState([]);
  const [operators, setOperators] = useState([]);
  const [calculationTypes, setCalculationTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conditionsSchema, setConditionsSchema] = useState(null);

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
      return { ...prev, calculations: newCalculations };
    });
  };

  const handleCalculationRemove = (index) => {
    setFormData(prev => ({
      ...prev,
      calculations: prev.calculations.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setLoading(true);
      
      // Validate conditions and calculations
      await Promise.all([
        rulesService.validateConditions(formData.conditions),
        rulesService.validateCalculations(formData.calculations)
      ]);

      if (initialData) {
        await onSubmit(initialData.id, formData);
      } else {
        await onSubmit(formData);
      }
      setError(null);
    } catch (err) {
      setError('Failed to save advanced rule. Please check your inputs and try again.');
      console.error('Error saving advanced rule:', err);
    } finally {
      setLoading(false);
    }
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
          <Box display="flex" flexDirection="column" gap={2}>
            {error && (
              <Alert severity="error">
                {error}
              </Alert>
            )}

            {/* Basic Rule Fields */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Basic Rule Settings
              </Typography>
              <Box display="flex" gap={2}>
                <FormControl fullWidth required>
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
                      </MenuItem>
                    ))}
                  </Select>
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

            <Divider />

            {/* Conditions */}
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

            <Divider />

            {/* Calculations */}
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

                  <TextField
                    fullWidth
                    label="Value"
                    type="number"
                    value={calc.value}
                    onChange={(e) => handleCalculationChange(index, 'value', e.target.value)}
                    inputProps={{ step: '0.01' }}
                  />

                  <IconButton
                    color="error"
                    onClick={() => handleCalculationRemove(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
            </Box>
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

export default AdvancedRuleBuilder;