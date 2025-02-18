import React, { useState, useEffect } from 'react';
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
import { productApi, customerApi, handleApiError } from '../../utils/apiClient';

const ProductForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    sku: '',
    customer: '',
    labeling_unit_1: '',
    labeling_quantity_1: '',
    labeling_unit_2: '',
    labeling_quantity_2: '',
    labeling_unit_3: '',
    labeling_quantity_3: '',
    labeling_unit_4: '',
    labeling_quantity_4: '',
    labeling_unit_5: '',
    labeling_quantity_5: '',
  });
  const [customers, setCustomers] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchCustomers();
    if (isEditMode) {
      fetchProduct();
    }
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productApi.get(id);
      if (response) {
        setFormData({
          sku: response.sku,
          customer: response.customer,
          labeling_unit_1: response.labeling_unit_1 || '',
          labeling_quantity_1: response.labeling_quantity_1 || '',
          labeling_unit_2: response.labeling_unit_2 || '',
          labeling_quantity_2: response.labeling_quantity_2 || '',
          labeling_unit_3: response.labeling_unit_3 || '',
          labeling_quantity_3: response.labeling_quantity_3 || '',
          labeling_unit_4: response.labeling_unit_4 || '',
          labeling_quantity_4: response.labeling_quantity_4 || '',
          labeling_unit_5: response.labeling_unit_5 || '',
          labeling_quantity_5: response.labeling_quantity_5 || '',
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
    
    if (!formData.customer) {
      newErrors.customer = 'Customer is required';
    }

    // Validate labeling quantities are non-negative if provided
    for (let i = 1; i <= 5; i++) {
      const quantityField = `labeling_quantity_${i}`;
      const unitField = `labeling_unit_${i}`;
      
      const quantity = formData[quantityField];
      const unit = formData[unitField];

      // Only validate if either quantity or unit is provided
      if (quantity !== '' || unit !== '') {
        if (quantity === '') {
          newErrors[quantityField] = 'Quantity is required when unit is provided';
        } else if (parseInt(quantity, 10) < 0) {
          newErrors[quantityField] = 'Quantity cannot be negative';
        }

        if (!unit) {
          newErrors[unitField] = 'Unit is required when quantity is provided';
        }
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    // Convert quantity fields to integers
    if (name.startsWith('labeling_quantity_')) {
      setFormData(prev => ({
        ...prev,
        [name]: value === '' ? '' : parseInt(value, 10)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
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
      // Clean up empty values
      const cleanedData = Object.fromEntries(
        Object.entries(formData).map(([key, value]) => {
          if (key.startsWith('labeling_quantity_') && value === '') {
            return [key, null];
          }
          if (key.startsWith('labeling_unit_') && value === '') {
            return [key, null];
          }
          return [key, value];
        })
      );

      const apiCall = isEditMode
        ? () => productApi.update(id, cleanedData)
        : () => productApi.create(cleanedData);

      const response = await apiCall();

      if (response) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/products');
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
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
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
          {isEditMode ? 'Edit Product' : 'New Product'}
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Product {isEditMode ? 'updated' : 'created'} successfully!
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="SKU"
                name="sku"
                value={formData.sku}
                onChange={handleChange}
                error={Boolean(errors.sku)}
                helperText={errors.sku}
                disabled={isEditMode}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
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

            {[1, 2, 3, 4, 5].map((num) => (
              <React.Fragment key={num}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label={`Labeling Unit ${num}`}
                    name={`labeling_unit_${num}`}
                    value={formData[`labeling_unit_${num}`]}
                    onChange={handleChange}
                    error={Boolean(errors[`labeling_unit_${num}`])}
                    helperText={errors[`labeling_unit_${num}`]}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label={`Labeling Quantity ${num}`}
                    name={`labeling_quantity_${num}`}
                    value={formData[`labeling_quantity_${num}`]}
                    onChange={handleChange}
                    error={Boolean(errors[`labeling_quantity_${num}`])}
                    helperText={errors[`labeling_quantity_${num}`]}
                    InputProps={{
                      inputProps: { min: 0 }
                    }}
                  />
                </Grid>
              </React.Fragment>
            ))}

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/products')}
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
                    isEditMode ? 'Update Product' : 'Create Product'
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

export default ProductForm;