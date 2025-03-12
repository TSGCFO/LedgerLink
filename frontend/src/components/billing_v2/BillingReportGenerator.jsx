import React, { useState, useEffect, useRef } from 'react';
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
  FormHelperText,
  Checkbox,
  ListItemText,
  LinearProgress,
  Card,
  CardContent,
  Divider,
  Chip
} from '@mui/material';
// Removed date picker imports in favor of native date input
import { format, addDays, parseISO } from 'date-fns';
import { billingV2Api } from '../../utils/api/billingV2Api';
import logger from '../../utils/logger';

/**
 * Form for generating new billing reports
 */
const BillingReportGenerator = ({ onReportGenerated, customers, loading: customersLoading }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [customerServices, setCustomerServices] = useState([]);
  const [loadingServices, setLoadingServices] = useState(false);
  const [progress, setProgress] = useState(null);
  const progressInterval = useRef(null);
  
  const [formData, setFormData] = useState({
    customerId: '',
    customer: null, // For Autocomplete
    startDate: null, // Using null for date pickers
    endDate: null,
    outputFormat: 'json',
    customerServices: [], // IDs of selected customer services
    customerServicesSelectAll: true // Whether to select all customer services
  });
  const [validationErrors, setValidationErrors] = useState({});
  
  // Fetch customer services when customer changes
  useEffect(() => {
    const fetchCustomerServices = async () => {
      if (!formData.customerId) {
        setCustomerServices([]);
        return;
      }
      
      setLoadingServices(true);
      try {
        logger.info('Fetching customer services for customer ID:', formData.customerId);
        const response = await billingV2Api.getCustomerServices(formData.customerId);
        logger.info('Customer services response:', response);
        
        if (response.success && response.data) {
          setCustomerServices(response.data);
          logger.info('Customer services set:', response.data);
          
          // By default, select all services
          if (formData.customerServicesSelectAll) {
            const serviceIds = response.data.map(service => service.id);
            logger.info('Selecting all service IDs:', serviceIds);
            setFormData(prev => ({
              ...prev,
              customerServices: serviceIds
            }));
          }
        } else {
          logger.warn('Invalid response format from customer services API', response);
          setCustomerServices([]);
        }
      } catch (err) {
        logger.error('Error fetching customer services', err);
        setCustomerServices([]);
      } finally {
        setLoadingServices(false);
      }
    };
    
    fetchCustomerServices();
    
    // Clean up any progress polling
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
        progressInterval.current = null;
      }
    };
  }, [formData.customerId, formData.customerServicesSelectAll]);
  
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
      customerId: value ? value.id : '',
      customerServices: [] // Reset selected services when customer changes
    });
  };
  
  const handleCustomerServicesChange = (event) => {
    const { value } = event.target;
    
    // Check if "All" was selected or deselected
    if (value.includes('all')) {
      if (formData.customerServices.length === customerServices.length) {
        // If all were already selected, deselect all
        setFormData({
          ...formData,
          customerServices: [],
          customerServicesSelectAll: false
        });
      } else {
        // Select all
        setFormData({
          ...formData,
          customerServices: customerServices.map(service => service.id),
          customerServicesSelectAll: true
        });
      }
    } else {
      // Regular service selection
      setFormData({
        ...formData,
        customerServices: value,
        customerServicesSelectAll: value.length === customerServices.length
      });
    }
  };
  
  // Check progress for a report generation
  const checkProgress = async (params) => {
    try {
      logger.info('Checking progress with params', params);
      const response = await billingV2Api.getReportProgress(params);
      logger.info('Progress response', response);
      
      if (response.success && response.data) {
        setProgress(response.data);
        logger.info('Progress data set', response.data);
        
        // Stop polling when completed
        if (response.data.status === 'completed' || response.data.status === 'error') {
          if (progressInterval.current) {
            clearInterval(progressInterval.current);
            progressInterval.current = null;
          }
          
          // If completed successfully, trigger the success state
          if (response.data.status === 'completed' && response.data.report_id) {
            setSuccess(true);
            setLoading(false);
            
            // Fetch full report data to ensure accurate information
            try {
              const reportId = response.data.report_id;
              const fullReport = await billingV2Api.getBillingReport(reportId);
              
              // Notify parent component with the full report data
              if (onReportGenerated && fullReport.success) {
                onReportGenerated(fullReport.data);
              } else {
                onReportGenerated({ id: response.data.report_id });
              }
            } catch (err) {
              logger.error("Error fetching full report after completion", err);
              // Fall back to just the ID if fetch fails
              if (onReportGenerated) {
                onReportGenerated({ id: response.data.report_id });
              }
            }
          }
          
          // If error occurred, show error message
          if (response.data.status === 'error') {
            setError(response.data.current_step || 'An error occurred during report generation');
            setLoading(false);
          }
        }
      } else {
        logger.warn('Invalid progress response format', response);
      }
    } catch (err) {
      // If progress checking fails, we just log it but don't stop the polling
      logger.error('Error checking report progress', err);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous states
    setError(null);
    setSuccess(false);
    setProgress(null);
    
    // Stop any existing progress polling
    if (progressInterval.current) {
      clearInterval(progressInterval.current);
      progressInterval.current = null;
    }
    
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
    
    // Add customer services if not using "all" and some services are selected
    if (!formData.customerServicesSelectAll && formData.customerServices.length > 0) {
      apiData.customer_services = formData.customerServices;
    }
    
    logger.info('Submitting report generation with data:', apiData);
    
    try {
      // For CSV output format that downloads directly, handle differently
      if (apiData.output_format === 'csv') {
        logger.info('CSV format requested, using direct download method');
        await billingV2Api.generateBillingReport(apiData);
        
        // Since the CSV download happens via file download, we can consider this successful
        setSuccess(true);
        setLoading(false);
        
        // Reset form dates after successful submission
        setFormData({
          ...formData,
          startDate: null,
          endDate: null
        });
        
        return;
      }
      
      // Start report generation for non-CSV formats
      const response = await billingV2Api.generateBillingReport(apiData);
      logger.info('Report generation response:', response);
      
      // Check if response has expected format
      if (!response || typeof response !== 'object') {
        throw new Error('Invalid response format');
      }
      
      // Check for success property
      if (!response.success) {
        throw new Error(response.error || 'Failed to generate billing report');
      }
      
      // If we have a quick response with data, handle it directly
      if (response.data) {
        setSuccess(true);
        setLoading(false);
        
        // Reset form dates after successful submission
        setFormData({
          ...formData,
          startDate: null,
          endDate: null
        });
        
        // Explicitly fetch the report to ensure we have the most accurate data
        try {
          const reportId = response.data.id;
          const fullReport = await billingV2Api.getBillingReport(reportId);
          
          // Notify parent component with the full report data
          if (onReportGenerated && fullReport.success) {
            onReportGenerated(fullReport.data);
          } else {
            onReportGenerated(response.data);
          }
        } catch (err) {
          logger.error("Error fetching full report after generation", err);
          // Fall back to original data if fetch fails
          if (onReportGenerated) {
            onReportGenerated(response.data);
          }
        }
        
        return;
      }
      
      // Otherwise, start polling for progress
      // Configure progress polling parameters
      const progressParams = {
        customer_id: apiData.customer_id,
        start_date: apiData.start_date,
        end_date: apiData.end_date
      };
      
      logger.info('Setting up progress polling with params:', progressParams);
      
      // Start with an immediate progress check
      await checkProgress(progressParams);
      
      // Set up polling for progress updates
      progressInterval.current = setInterval(() => {
        checkProgress(progressParams);
      }, 1000); // Check every second
      
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
  
  // Progress indicator component
  const ProgressIndicator = ({ progress }) => {
    // Always render progress indicator, even with minimal data
    const progressData = progress || {
      percent_complete: 0,
      current_step: "Initializing...",
      status: "initializing"
    };
    
    // Format estimated completion time if available
    let estimatedTimeDisplay = 'Calculating...';
    if (progressData.estimated_completion_time) {
      try {
        const estimatedTime = parseISO(progressData.estimated_completion_time);
        estimatedTimeDisplay = format(estimatedTime, 'h:mm:ss a');
      } catch (err) {
        estimatedTimeDisplay = 'Calculating...';
      }
    }
    
    return (
      <Card variant="outlined" sx={{ mb: 2, mt: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Report Generation Progress
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={progressData.percent_complete || 0} 
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Box display="flex" justifyContent="space-between" mt={0.5}>
              <Typography variant="body2" color="text.secondary">
                {progressData.percent_complete || 0}% Complete
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {progressData.processed_orders || 0} / {progressData.total_orders || '?'} Orders
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ mb: 1 }}>
            <Typography variant="body1" fontWeight="bold">
              Current Step:
            </Typography>
            <Typography variant="body1">
              {progressData.current_step || 'Initializing...'}
            </Typography>
          </Box>
          
          <Box sx={{ mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Status: {progressData.status || 'processing'}
            </Typography>
            {progressData.status !== 'completed' && progressData.estimated_completion_time && (
              <Typography variant="body2" color="text.secondary">
                Estimated completion: {estimatedTimeDisplay}
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    );
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
      
      {/* Progress indicator - show if either loading with progress, or loading for more than 2 seconds */}
      {loading && (
        <ProgressIndicator 
          progress={progress || { 
            percent_complete: 0, 
            current_step: "Initializing report...",
            status: "initializing" 
          }} 
        />
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
          
          {/* Customer Services Selection */}
          {formData.customerId && customerServices.length > 0 && (
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="customer-services-label">Services to Include</InputLabel>
                <Select
                  labelId="customer-services-label"
                  id="customer-services-select"
                  multiple
                  value={formData.customerServices}
                  onChange={handleCustomerServicesChange}
                  renderValue={(selected) => {
                    if (selected.includes('all') || selected.length === customerServices.length) {
                      return <Chip label="All Services" />;
                    }
                    
                    return (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => {
                          const service = customerServices.find(s => s.id === value);
                          return service ? (
                            <Chip key={value} label={service.service_name} />
                          ) : null;
                        })}
                      </Box>
                    );
                  }}
                  label="Services to Include"
                  MenuProps={{
                    PaperProps: {
                      style: {
                        maxHeight: 300,
                      },
                    },
                  }}
                >
                  <MenuItem value="all">
                    <Checkbox 
                      checked={formData.customerServicesSelectAll || formData.customerServices.length === customerServices.length} 
                    />
                    <ListItemText primary="All Services" />
                  </MenuItem>
                  
                  <Divider />
                  
                  {customerServices.map((service) => (
                    <MenuItem key={service.id} value={service.id}>
                      <Checkbox checked={formData.customerServices.indexOf(service.id) > -1} />
                      <ListItemText 
                        primary={service.service_name} 
                        secondary={`${service.charge_type} - $${service.unit_price}`} 
                      />
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>
                  {loadingServices ? 'Loading services...' : 
                    customerServices.length > 0 ? 
                    `${formData.customerServices.length} of ${customerServices.length} services selected` : 
                    'No services available'}
                </FormHelperText>
              </FormControl>
            </Grid>
          )}
          
          <Grid item xs={12}>
            <Box display="flex" justifyContent="flex-start" mt={2}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                startIcon={loading && !progress ? <CircularProgress size={20} color="inherit" /> : null}
                data-testid="generate-report-button"
              >
                {loading && !progress ? 'Initializing...' : loading ? 'Generating Report...' : 'Generate Report'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default BillingReportGenerator;