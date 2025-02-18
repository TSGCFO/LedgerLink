import { useState, useEffect } from 'react';
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
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { insertApi, customerApi, productApi, handleApiError } from '../../utils/apiClient';

const InsertForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    sku: '',
    insert_name: '',
    insert_quantity: 0,
    customer: ''
  });
  const [customers, setCustomers] = useState([]);
  const [availableSkus, setAvailableSkus] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchCustomers();
    if (isEditMode) {
      fetchInsert();
    }
  }, [id]);

  // Fetch SKUs when customer is set in edit mode
  useEffect(() => {
    if (formData.customer) {
      fetchSkusByCustomer(formData.customer);
    }
  }, [formData.customer]);

  const fetchInsert = async () => {
    try {
      setLoading(true);
      const response = await insertApi.get(id);
      if (response.success) {
        setFormData({
          sku: response.data.sku,
          insert_name: response.data.insert_name,
          insert_quantity: response.data.insert_quantity,
          customer: response.data.customer
        });
      }
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await customerApi.list();
      if (response.success) {
        setCustomers(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.sku.trim()) {
      newErrors.sku = 'SKU is required';
    }
    
    if (!formData.insert_name.trim()) {
      newErrors.insert_name = 'Insert name is required';
    }

    if (!formData.customer) {
      newErrors.customer = 'Customer is required';
    }

    if (formData.insert_quantity < 0) {
      newErrors.insert_quantity = 'Quantity cannot be negative';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const fetchSkusByCustomer = async (customerId) => {
    try {
      const response = await productApi.getSkusByCustomer(customerId);
      if (response.success) {
        setAvailableSkus(response.data);
        // Clear SKU when customer changes
        setFormData(prev => ({
          ...prev,
          sku: ''
        }));
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Fetch SKUs when customer changes
    if (name === 'customer' && value) {
      fetchSkusByCustomer(value);
    }

    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
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
      const apiCall = isEditMode
        ? () => insertApi.update(id, formData)
        : () => insertApi.create(formData);

      const response = await apiCall();

      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/inserts');
        }, 1500);
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

  if (loading && isEditMode) {
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
          {isEditMode ? 'Edit Insert' : 'New Insert'}
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Insert {isEditMode ? 'updated' : 'created'} successfully!
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

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth error={Boolean(errors.sku)}>
                <InputLabel>SKU</InputLabel>
                <Select
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  label="SKU"
                  disabled={!formData.customer || isEditMode}
                >
                  {availableSkus.length === 0 ? (
                    <MenuItem disabled>No SKUs available for this customer</MenuItem>
                  ) : (
                    [...availableSkus]
                      .sort((a, b) => a.sku.localeCompare(b.sku))
                      .map((product) => (
                        <MenuItem key={product.id} value={product.sku}>
                          {product.sku}
                        </MenuItem>
                      ))
                  )}
                </Select>
                {errors.sku && (
                  <Typography color="error" variant="caption">
                    {errors.sku}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Insert Name"
                name="insert_name"
                value={formData.insert_name}
                onChange={handleChange}
                error={Boolean(errors.insert_name)}
                helperText={errors.insert_name}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Quantity"
                name="insert_quantity"
                type="number"
                value={formData.insert_quantity}
                onChange={handleChange}
                error={Boolean(errors.insert_quantity)}
                helperText={errors.insert_quantity}
                InputProps={{
                  inputProps: { min: 0 }
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/inserts')}
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
                    isEditMode ? 'Update Insert' : 'Create Insert'
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

export default InsertForm;