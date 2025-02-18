import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { customerServiceApi, customerApi, serviceApi, productApi, handleApiError } from '../../utils/apiClient';

const CustomerServiceForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    customer: '',
    service: '',
    unit_price: '',
    skus: []
  });
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [availableSkus, setAvailableSkus] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const fetchCustomers = useCallback(async () => {
    try {
      const response = await customerApi.list();
      if (response.success) {
        setCustomers(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  }, []);

  const fetchServices = useCallback(async () => {
    try {
      const response = await serviceApi.list();
      if (response.success) {
        setServices(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  }, []);

  const fetchCustomerService = useCallback(async () => {
    try {
      setLoading(true);
      const response = await customerServiceApi.get(id);
      if (response) {
        console.log('Customer Service data:', response);
        setFormData({
          customer: response.customer,
          service: response.service,
          unit_price: response.unit_price,
          skus: response.sku_list || []
        });

        // Fetch SKUs for the selected customer
        if (response.customer) {
          fetchSkus(response.customer);
        }
      }
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  }, [id]);

  const fetchSkus = useCallback(async (customerId) => {
    try {
      if (!customerId) {
        setAvailableSkus([]);
        return;
      }
      const response = await productApi.list({ customer: customerId });
      if (response.success) {
        setAvailableSkus(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  }, []);

  useEffect(() => {
    fetchCustomers();
    fetchServices();
    if (isEditMode) {
      fetchCustomerService();
    }
  }, [id, isEditMode, fetchCustomers, fetchServices, fetchCustomerService]);

  // Fetch SKUs when editing and customer service is loaded
  useEffect(() => {
    if (isEditMode && formData.customer) {
      fetchSkus(formData.customer);
    }
  }, [formData.customer, isEditMode, fetchSkus]);

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.customer) {
      newErrors.customer = 'Customer is required';
    }
    
    if (!formData.service) {
      newErrors.service = 'Service is required';
    }
    
    if (!formData.unit_price) {
      newErrors.unit_price = 'Unit price is required';
    } else if (isNaN(formData.unit_price) || parseFloat(formData.unit_price) <= 0) {
      newErrors.unit_price = 'Unit price must be a positive number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
      // Clear SKUs when customer changes
      ...(name === 'customer' ? { skus: [] } : {})
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
    // Fetch SKUs when customer changes
    if (name === 'customer') {
      fetchSkus(value);
    }
  };

  const handleSkuChange = (event) => {
    const { value } = event.target;
    setFormData(prev => ({
      ...prev,
      skus: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Create a copy of form data without skus for initial creation
      const { skus, ...serviceData } = formData;
      
      const apiCall = isEditMode
        ? () => customerServiceApi.update(id, serviceData)
        : () => customerServiceApi.create(serviceData);

      const response = await apiCall();

      if (response.success) {
        // If there are SKUs, add them after creation
        if (skus.length > 0) {
          await customerServiceApi.addSkus(response.data.id, { sku_ids: skus });
        }
        setSuccess(true);
        // Navigate immediately instead of using setTimeout
        navigate('/customer-services');
      }
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Snackbar
        open={Boolean(error)}
        autoHideDuration={6000}
        onClose={handleCloseError}
      >
        <Alert onClose={handleCloseError} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          {isEditMode ? 'Edit Customer Service' : 'New Customer Service'}
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Customer service {isEditMode ? 'updated' : 'created'} successfully!
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControl fullWidth error={Boolean(errors.customer)}>
                <InputLabel>Customer</InputLabel>
                <Select
                  name="customer"
                  value={formData.customer}
                  onChange={handleChange}
                  label="Customer"
                >
                  {customers.map((customer) => (
                    <MenuItem key={customer.id} value={customer.id}>
                      {customer.company_name}
                    </MenuItem>
                  ))}
                </Select>
                {errors.customer && (
                  <Typography color="error" variant="caption">
                    {errors.customer}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth error={Boolean(errors.service)}>
                <InputLabel>Service</InputLabel>
                <Select
                  name="service"
                  value={formData.service}
                  onChange={handleChange}
                  label="Service"
                >
                  {services.map((service) => (
                    <MenuItem key={service.id} value={service.id}>
                      {service.service_name}
                    </MenuItem>
                  ))}
                </Select>
                {errors.service && (
                  <Typography color="error" variant="caption">
                    {errors.service}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Unit Price"
                name="unit_price"
                type="number"
                value={formData.unit_price}
                onChange={handleChange}
                error={Boolean(errors.unit_price)}
                helperText={errors.unit_price}
                variant="outlined"
                inputProps={{ step: "0.01", min: "0" }}
              />
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>SKUs</InputLabel>
                <Select
                  multiple
                  name="skus"
                  value={formData.skus}
                  onChange={handleSkuChange}
                  input={<OutlinedInput label="SKUs" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {availableSkus.map((sku) => (
                    <MenuItem key={sku.id} value={sku.sku}>
                      {sku.sku} - {sku.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/customer-services')}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                >
                  {loading ? (
                    <CircularProgress size={24} />
                  ) : (
                    isEditMode ? 'Update Customer Service' : 'Create Customer Service'
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
};

export default CustomerServiceForm;