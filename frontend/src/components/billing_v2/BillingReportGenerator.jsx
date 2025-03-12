import React, { useState, useEffect } from 'react';
import { 
  Button, 
  FormControl, 
  TextField, 
  Select, 
  MenuItem, 
  InputLabel, 
  Paper, 
  Grid, 
  Typography, 
  CircularProgress,
  Autocomplete,
  Box,
  Alert,
  FormHelperText
} from '@mui/material';
// Removed date picker imports in favor of native date input
import { format, addDays } from 'date-fns';
import { billingV2Api } from '../../utils/api/billingV2Api';
import logger from '../../utils/logger';

/**
 * Form for generating new billing reports
 */
const BillingReportGenerator = ({ onReportGenerated, customers, loading: customersLoading }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    customerId: '',
    customer: null, // For Autocomplete
    startDate: null, // Using null for date pickers
    endDate: null,
    outputFormat: 'json'
  });
  const [validationErrors, setValidationErrors] = useState({});
  
  const validateForm = () => {
    const errors = {};
    
    if (!formData.customerId && !formData.customer) {
      errors.customer = 'Customer is required';
    }
    
    if (!formData.startDate) {
      errors.startDate = 'Start date is required';
    }
    
    if (!formData.endDate) {
      errors.endDate = 'End date is required';
    } else if (formData.startDate && formData.endDate < formData.startDate) {
      errors.endDate = 'End date must be after start date';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSelectChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleDateChange = (name, date) => {
    setFormData({
      ...formData,
      [name]: date
    });
  };
  
  const handleCustomerChange = (event, value) => {
    setFormData({
      ...formData,
      customer: value,
      customerId: value ? value.id : ''
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous states
    setError(null);
    setSuccess(false);
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    // Prepare data for API
    const apiData = {
      customer_id: formData.customerId,
      start_date: formData.startDate ? format(formData.startDate, 'yyyy-MM-dd') : null,
      end_date: formData.endDate ? format(formData.endDate, 'yyyy-MM-dd') : null,
      output_format: formData.outputFormat
    };
    
    try {
      const response = await billingV2Api.generateBillingReport(apiData);
      setLoading(false);
      
      // Check if response has expected format
      if (!response || typeof response !== 'object') {
        throw new Error('Invalid response format');
      }
      
      // Check for success property
      if (!response.success) {
        throw new Error(response.error || 'Failed to generate billing report');
      }
      
      setSuccess(true);
      
      // Reset form after successful submission
      setFormData({
        ...formData,
        startDate: null,
        endDate: null
      });
      
      // Notify parent component
      if (onReportGenerated && response.data) {
        onReportGenerated(response.data);
      }
    } catch (err) {
      logger.error('Error generating billing report', err);
      
      // Handle response errors (from our error checks)
      if (err.message?.includes('Failed to generate billing report')) {
        setError(err.message);
      }
      // Handle CSRF errors
      else if (err.status === 403 && err.message?.includes('CSRF')) {
        setError('CSRF verification failed. The server needs to be configured to allow your domain. Contact admin to add this domain to CSRF_TRUSTED_ORIGINS in Django settings.');
      } 
      // Handle server errors
      else if (err.status === 500) {
        setError('Server error occurred while generating report. Check server logs for details.');
      }
      // Handle 404 errors (endpoint not found)
      else if (err.status === 404) {
        setError('Report generation endpoint not found. Please check API configuration.');
      }
      // Generic error handling
      else {
        setError(err.message || 'An unexpected error occurred while generating the report');
      }
      
      setLoading(false);
    }
  };
  
  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Generate Billing Report
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} data-testid="error-alert">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} data-testid="success-alert">
          Report generated successfully!
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Autocomplete
              id="customer-select"
              options={customers || []}
              getOptionLabel={(option) => option.company_name || ''}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              value={formData.customer}
              onChange={handleCustomerChange}
              loading={customersLoading}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Customer"
                  required
                  error={!!validationErrors.customer}
                  helperText={validationErrors.customer}
                />
              )}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel id="output-format-label">Output Format</InputLabel>
              <Select
                labelId="output-format-label"
                name="outputFormat"
                value={formData.outputFormat}
                onChange={handleSelectChange}
                label="Output Format"
              >
                <MenuItem value="json">JSON</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              label="Start Date"
              type="date"
              fullWidth
              required
              value={formData.startDate ? format(formData.startDate, 'yyyy-MM-dd') : ''}
              onChange={(e) => {
                const date = e.target.value ? new Date(e.target.value) : null;
                handleDateChange('startDate', date);
              }}
              InputLabelProps={{ shrink: true }}
              error={!!validationErrors.startDate}
              helperText={validationErrors.startDate}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              label="End Date"
              type="date"
              fullWidth
              required
              value={formData.endDate ? format(formData.endDate, 'yyyy-MM-dd') : ''}
              onChange={(e) => {
                const date = e.target.value ? new Date(e.target.value) : null;
                handleDateChange('endDate', date);
              }}
              InputLabelProps={{ shrink: true }}
              error={!!validationErrors.endDate}
              helperText={validationErrors.endDate}
              inputProps={{
                min: formData.startDate ? format(addDays(formData.startDate, 1), 'yyyy-MM-dd') : ''
              }}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Box display="flex" justifyContent="flex-start" mt={2}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                data-testid="generate-report-button"
              >
                {loading ? 'Generating Report...' : 'Generate Report'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default BillingReportGenerator;