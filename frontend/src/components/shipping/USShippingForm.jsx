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
  Divider,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { usShippingApi, customerApi, orderApi, handleApiError } from '../../utils/apiClient';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';

const USShippingForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    transaction: '',
    customer: '',
    ship_date: null,
    ship_to_name: '',
    ship_to_address_1: '',
    ship_to_address_2: '',
    ship_to_city: '',
    ship_to_state: '',
    ship_to_zip: '',
    ship_to_country_code: 'US',
    tracking_number: '',
    service_name: '',
    weight_lbs: '',
    length_in: '',
    width_in: '',
    height_in: '',
    base_chg: '',
    carrier_peak_charge: '',
    wizmo_peak_charge: '',
    accessorial_charges: '',
    rate: '',
    hst: '',
    gst: '',
    current_status: '',
    delivery_status: '',
    first_attempt_date: null,
    delivery_date: null,
    days_to_first_deliver: ''
  });

  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [statuses, setStatuses] = useState({ current: [], delivery: [] });
  const [serviceNames, setServiceNames] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchCustomers();
    fetchStatuses();
    fetchServiceNames();
    if (isEditMode) {
      fetchShipment();
    }
  }, [id]);

  useEffect(() => {
    if (formData.customer) {
      fetchCustomerOrders(formData.customer);
    }
  }, [formData.customer]);

  const fetchShipment = async () => {
    try {
      setLoading(true);
      const response = await usShippingApi.get(id);
      if (response.success) {
        setFormData({
          ...response.data,
          ship_date: response.data.ship_date ? new Date(response.data.ship_date) : null,
          first_attempt_date: response.data.first_attempt_date ? new Date(response.data.first_attempt_date) : null,
          delivery_date: response.data.delivery_date ? new Date(response.data.delivery_date) : null
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

  const fetchCustomerOrders = async (customerId) => {
    try {
      const response = await orderApi.list({ customer: customerId });
      if (response.success) {
        setOrders(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const fetchStatuses = async () => {
    try {
      const response = await usShippingApi.getStatuses();
      if (response.success) {
        setStatuses(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const fetchServiceNames = async () => {
    try {
      const response = await usShippingApi.getServiceNames();
      if (response.success) {
        setServiceNames(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.transaction) {
      newErrors.transaction = 'Order is required';
    }
    
    if (!formData.customer) {
      newErrors.customer = 'Customer is required';
    }

    // Validate shipping address fields if any are filled
    const shippingFields = [
      'ship_to_name',
      'ship_to_address_1',
      'ship_to_city',
      'ship_to_state',
      'ship_to_zip'
    ];
    
    if (shippingFields.some(field => formData[field])) {
      shippingFields.forEach(field => {
        if (!formData[field]) {
          newErrors[field] = 'Required for shipping';
        }
      });
    }

    // Validate numeric fields
    const numericFields = [
      'weight_lbs',
      'length_in',
      'width_in',
      'height_in',
      'base_chg',
      'carrier_peak_charge',
      'wizmo_peak_charge',
      'accessorial_charges',
      'rate',
      'hst',
      'gst'
    ];

    numericFields.forEach(field => {
      if (formData[field] && isNaN(parseFloat(formData[field]))) {
        newErrors[field] = 'Must be a number';
      }
    });

    // Validate dates
    if (formData.delivery_date && formData.ship_date) {
      if (formData.delivery_date < formData.ship_date) {
        newErrors.delivery_date = 'Delivery date cannot be earlier than ship date';
      }
    }

    if (formData.first_attempt_date && formData.ship_date) {
      if (formData.first_attempt_date < formData.ship_date) {
        newErrors.first_attempt_date = 'First attempt date cannot be earlier than ship date';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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
        ? () => usShippingApi.update(id, formData)
        : () => usShippingApi.create(formData);

      const response = await apiCall();

      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/shipping/us');
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
          {isEditMode ? 'Edit US Shipping Record' : 'New US Shipping Record'}
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Shipping record {isEditMode ? 'updated' : 'created'} successfully!
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth error={Boolean(errors.customer)}>
                <InputLabel>Customer</InputLabel>
                <Select
                  name="customer"
                  value={formData.customer}
                  onChange={handleChange}
                  label="Customer"
                  disabled={isEditMode}
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
              <FormControl fullWidth error={Boolean(errors.transaction)}>
                <InputLabel>Order</InputLabel>
                <Select
                  name="transaction"
                  value={formData.transaction}
                  onChange={handleChange}
                  label="Order"
                  disabled={isEditMode}
                >
                  {orders.map((order) => (
                    <MenuItem key={order.id} value={order.id}>
                      {order.reference_number}
                    </MenuItem>
                  ))}
                </Select>
                {errors.transaction && (
                  <Typography color="error" variant="caption">
                    {errors.transaction}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Shipping Information
                </Typography>
              </Divider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Ship to Name"
                name="ship_to_name"
                value={formData.ship_to_name}
                onChange={handleChange}
                error={Boolean(errors.ship_to_name)}
                helperText={errors.ship_to_name}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address Line 1"
                name="ship_to_address_1"
                value={formData.ship_to_address_1}
                onChange={handleChange}
                error={Boolean(errors.ship_to_address_1)}
                helperText={errors.ship_to_address_1}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address Line 2"
                name="ship_to_address_2"
                value={formData.ship_to_address_2}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="City"
                name="ship_to_city"
                value={formData.ship_to_city}
                onChange={handleChange}
                error={Boolean(errors.ship_to_city)}
                helperText={errors.ship_to_city}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="State"
                name="ship_to_state"
                value={formData.ship_to_state}
                onChange={handleChange}
                error={Boolean(errors.ship_to_state)}
                helperText={errors.ship_to_state}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ZIP Code"
                name="ship_to_zip"
                value={formData.ship_to_zip}
                onChange={handleChange}
                error={Boolean(errors.ship_to_zip)}
                helperText={errors.ship_to_zip}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Country Code"
                name="ship_to_country_code"
                value={formData.ship_to_country_code}
                onChange={handleChange}
                disabled
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Shipment Details
                </Typography>
              </Divider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Service Name</InputLabel>
                <Select
                  name="service_name"
                  value={formData.service_name}
                  onChange={handleChange}
                  label="Service Name"
                >
                  {serviceNames.map((service) => (
                    <MenuItem key={service} value={service}>
                      {service}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tracking Number"
                name="tracking_number"
                value={formData.tracking_number}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Ship Date"
                  value={formData.ship_date}
                  onChange={(newValue) => {
                    setFormData(prev => ({
                      ...prev,
                      ship_date: newValue
                    }));
                  }}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="First Attempt Date"
                  value={formData.first_attempt_date}
                  onChange={(newValue) => {
                    setFormData(prev => ({
                      ...prev,
                      first_attempt_date: newValue
                    }));
                  }}
                  renderInput={(params) => <TextField {...params} fullWidth error={Boolean(errors.first_attempt_date)} helperText={errors.first_attempt_date} />}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Delivery Date"
                  value={formData.delivery_date}
                  onChange={(newValue) => {
                    setFormData(prev => ({
                      ...prev,
                      delivery_date: newValue
                    }));
                  }}
                  renderInput={(params) => <TextField {...params} fullWidth error={Boolean(errors.delivery_date)} helperText={errors.delivery_date} />}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Current Status</InputLabel>
                <Select
                  name="current_status"
                  value={formData.current_status}
                  onChange={handleChange}
                  label="Current Status"
                >
                  {statuses.current_statuses?.map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Delivery Status</InputLabel>
                <Select
                  name="delivery_status"
                  value={formData.delivery_status}
                  onChange={handleChange}
                  label="Delivery Status"
                >
                  {statuses.delivery_statuses?.map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Package Information
                </Typography>
              </Divider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Weight (lbs)"
                name="weight_lbs"
                type="number"
                value={formData.weight_lbs}
                onChange={handleChange}
                error={Boolean(errors.weight_lbs)}
                helperText={errors.weight_lbs}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Length (in)"
                name="length_in"
                type="number"
                value={formData.length_in}
                onChange={handleChange}
                error={Boolean(errors.length_in)}
                helperText={errors.length_in}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Width (in)"
                name="width_in"
                type="number"
                value={formData.width_in}
                onChange={handleChange}
                error={Boolean(errors.width_in)}
                helperText={errors.width_in}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Height (in)"
                name="height_in"
                type="number"
                value={formData.height_in}
                onChange={handleChange}
                error={Boolean(errors.height_in)}
                helperText={errors.height_in}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Charges
                </Typography>
              </Divider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Base Charge"
                name="base_chg"
                type="number"
                value={formData.base_chg}
                onChange={handleChange}
                error={Boolean(errors.base_chg)}
                helperText={errors.base_chg}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Carrier Peak Charge"
                name="carrier_peak_charge"
                type="number"
                value={formData.carrier_peak_charge}
                onChange={handleChange}
                error={Boolean(errors.carrier_peak_charge)}
                helperText={errors.carrier_peak_charge}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Wizmo Peak Charge"
                name="wizmo_peak_charge"
                type="number"
                value={formData.wizmo_peak_charge}
                onChange={handleChange}
                error={Boolean(errors.wizmo_peak_charge)}
                helperText={errors.wizmo_peak_charge}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Accessorial Charges"
                name="accessorial_charges"
                type="number"
                value={formData.accessorial_charges}
                onChange={handleChange}
                error={Boolean(errors.accessorial_charges)}
                helperText={errors.accessorial_charges}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Rate"
                name="rate"
                type="number"
                value={formData.rate}
                onChange={handleChange}
                error={Boolean(errors.rate)}
                helperText={errors.rate}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="HST"
                name="hst"
                type="number"
                value={formData.hst}
                onChange={handleChange}
                error={Boolean(errors.hst)}
                helperText={errors.hst}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="GST"
                name="gst"
                type="number"
                value={formData.gst}
                onChange={handleChange}
                error={Boolean(errors.gst)}
                helperText={errors.gst}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/shipping/us')}
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
                    isEditMode ? 'Update Shipping Record' : 'Create Shipping Record'
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

export default USShippingForm;