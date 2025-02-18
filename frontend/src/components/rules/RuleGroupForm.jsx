import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  CircularProgress,
  Alert,
  Tooltip,
} from '@mui/material';
import rulesService from '../../services/rulesService';

const LOGIC_OPERATORS = [
  { value: 'AND', label: 'All conditions must be true (AND)' },
  { value: 'OR', label: 'Any condition can be true (OR)' },
  { value: 'NOT', label: 'Condition must not be true (NOT)' },
  { value: 'XOR', label: 'Only one condition must be true (XOR)' },
  { value: 'NAND', label: 'At least one condition must be false (NAND)' },
  { value: 'NOR', label: 'None of the conditions must be true (NOR)' },
];

const RuleGroupForm = ({ initialData, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    customer_service: '',
    logic_operator: 'AND',
    ...initialData,
  });
  const [customerServices, setCustomerServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCustomerServices = async () => {
      try {
        setLoading(true);
        setError(null);
        const services = await rulesService.getCustomerServices();
        
        if (services.length === 0) {
          setError('No customer services available. Please create a customer service first.');
        }
        setCustomerServices(services);
      } catch (error) {
        console.error('Error fetching customer services:', error);
        setError(error.message || 'Failed to load customer services');
      } finally {
        setLoading(false);
      }
    };

    fetchCustomerServices();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.customer_service) {
      setError('Please select a customer service');
      return;
    }
    try {
      await onSubmit(formData);
    } catch (error) {
      setError(error.message || 'Failed to save rule group');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Dialog open onClose={onCancel} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {initialData ? 'Edit Rule Group' : 'Create Rule Group'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            <FormControl fullWidth required error={!loading && customerServices.length === 0}>
              <Box display="flex" alignItems="center" gap={1}>
                <Box flexGrow={1}>
                  <InputLabel>Customer Service</InputLabel>
                  <Select
                    name="customer_service"
                    value={formData.customer_service}
                    onChange={handleChange}
                    label="Customer Service"
                    disabled={loading || customerServices.length === 0}
                    fullWidth
                  >
                    {customerServices.map((service) => (
                      <MenuItem key={service.id} value={service.id}>
                        {`${service.customer_details?.company_name || ''} - ${service.service_details?.service_name || ''}`}
                      </MenuItem>
                    ))}
                  </Select>
                </Box>
                {loading && <CircularProgress size={20} />}
              </Box>
              {loading ? (
                <FormHelperText>Loading customer services...</FormHelperText>
              ) : customerServices.length === 0 ? (
                <FormHelperText error>No customer services available</FormHelperText>
              ) : null}
            </FormControl>

            <FormControl fullWidth required>
              <InputLabel>Logic Operator</InputLabel>
              <Select
                name="logic_operator"
                value={formData.logic_operator}
                onChange={handleChange}
                label="Logic Operator"
              >
                {LOGIC_OPERATORS.map((operator) => (
                  <MenuItem key={operator.value} value={operator.value}>
                    {operator.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onCancel}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={!formData.customer_service || loading || customerServices.length === 0 || error}
          >
            {initialData ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default RuleGroupForm;