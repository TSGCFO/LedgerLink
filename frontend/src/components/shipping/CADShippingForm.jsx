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
import { cadShippingApi, customerApi, orderApi, handleApiError } from '../../utils/apiClient';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DateTimePicker } from '@mui/x-date-pickers';
import { ListSubheader, ListItemText } from '@mui/material';
import { FixedSizeList } from 'react-window';
import { Autocomplete } from '@mui/material';
import debounce from 'lodash/debounce';

// Virtual List Component for Order Select
const VirtualizedOrderList = React.forwardRef(function VirtualizedOrderList(props, ref) {
  const { items, itemSize = 48, maxHeight = 250, onItemClick } = props;
  
  const Row = ({ index, style }) => (
    <MenuItem
      style={style}
      onClick={() => onItemClick(items[index])}
      key={items[index].id}
    >
      <ListItemText
        primary={`Order #${items[index].id}`}
        secondary={`${items[index].customer_name} - ${new Date(items[index].created_at).toLocaleDateString()}`}
      />
    </MenuItem>
  );

  return (
    <FixedSizeList
      height={Math.min(maxHeight, items.length * itemSize)}
      width="100%"
      itemSize={itemSize}
      itemCount={items.length}
      ref={ref}
    >
      {Row}
    </FixedSizeList>
  );
});

const CADShippingForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    transaction: '',
    customer: '',
    service_code_description: '',
    ship_to_name: '',
    ship_to_address_1: '',
    ship_to_address_2: '',
    shiptoaddress3: '',
    ship_to_city: '',
    ship_to_state: '',
    ship_to_country: '',
    ship_to_postal_code: '',
    tracking_number: '',
    pre_tax_shipping_charge: '',
    tax1type: '',
    tax1amount: '',
    tax2type: '',
    tax2amount: '',
    tax3type: '',
    tax3amount: '',
    fuel_surcharge: '',
    reference: '',
    weight: '',
    gross_weight: '',
    box_length: '',
    box_width: '',
    box_height: '',
    box_name: '',
    ship_date: null,
    carrier: '',
    raw_ship_date: ''
  });

  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredOrders, setFilteredOrders] = useState([]);

  useEffect(() => {
    fetchCustomers();
    if (isEditMode) {
      fetchShipment();
    }
  }, [id]);

  useEffect(() => {
    if (formData.customer) {
      fetchCustomerOrders(formData.customer);
    }
  }, [formData.customer]);

  useEffect(() => {
    if (!searchTerm) {
      setFilteredOrders(orders);
      return;
    }
    
    const lowercaseSearch = searchTerm.toLowerCase();
    const filtered = orders.filter(order => 
      order.id.toString().includes(lowercaseSearch) ||
      order.customer_name.toLowerCase().includes(lowercaseSearch)
    );
    setFilteredOrders(filtered);
  }, [searchTerm, orders]);

  const handleSearchChange = debounce((value) => {
    setSearchTerm(value);
  }, 300);

  const fetchShipment = async () => {
    try {
      setLoading(true);
      const response = await cadShippingApi.get(id);
      if (response.success) {
        setFormData({
          ...response.data,
          ship_date: response.data.ship_date ? new Date(response.data.ship_date) : null
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
      'ship_to_postal_code'
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
      'pre_tax_shipping_charge',
      'tax1amount',
      'tax2amount',
      'tax3amount',
      'fuel_surcharge',
      'weight',
      'gross_weight',
      'box_length',
      'box_width',
      'box_height'
    ];

    numericFields.forEach(field => {
      if (formData[field] && isNaN(parseFloat(formData[field]))) {
        newErrors[field] = 'Must be a number';
      }
    });
    
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
        ? () => cadShippingApi.update(id, formData)
        : () => cadShippingApi.create(formData);

      const response = await apiCall();

      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/shipping/cad');
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
          {isEditMode ? 'Edit CAD Shipping Record' : 'New CAD Shipping Record'}
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
                <InputLabel id="order-select-label">Order</InputLabel>
                <Autocomplete
                  id="order-select"
                  options={filteredOrders}
                  getOptionLabel={(option) => `Order #${option.id} - ${option.customer_name}`}
                  value={orders.find(o => o.id === formData.transaction) || null}
                  onChange={(event, newValue) => {
                    handleChange({
                      target: {
                        name: 'transaction',
                        value: newValue ? newValue.id : ''
                      }
                    });
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Search Orders"
                      onChange={(e) => handleSearchChange(e.target.value)}
                      error={Boolean(errors.transaction)}
                      helperText={errors.transaction}
                    />
                  )}
                  ListboxComponent={VirtualizedOrderList}
                  ListboxProps={{
                    items: filteredOrders,
                    onItemClick: (item) => {
                      handleChange({
                        target: {
                          name: 'transaction',
                          value: item.id
                        }
                      });
                    }
                  }}
                />
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
                label="State/Province"
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
                label="Postal Code"
                name="ship_to_postal_code"
                value={formData.ship_to_postal_code}
                onChange={handleChange}
                error={Boolean(errors.ship_to_postal_code)}
                helperText={errors.ship_to_postal_code}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Country"
                name="ship_to_country"
                value={formData.ship_to_country}
                onChange={handleChange}
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
              <TextField
                fullWidth
                label="Carrier"
                name="carrier"
                value={formData.carrier}
                onChange={handleChange}
              />
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
                <DateTimePicker
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
              <TextField
                fullWidth
                label="Service Code Description"
                name="service_code_description"
                value={formData.service_code_description}
                onChange={handleChange}
              />
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
                label="Weight (kg)"
                name="weight"
                type="number"
                value={formData.weight}
                onChange={handleChange}
                error={Boolean(errors.weight)}
                helperText={errors.weight}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Gross Weight (kg)"
                name="gross_weight"
                type="number"
                value={formData.gross_weight}
                onChange={handleChange}
                error={Boolean(errors.gross_weight)}
                helperText={errors.gross_weight}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Length (cm)"
                name="box_length"
                type="number"
                value={formData.box_length}
                onChange={handleChange}
                error={Boolean(errors.box_length)}
                helperText={errors.box_length}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Width (cm)"
                name="box_width"
                type="number"
                value={formData.box_width}
                onChange={handleChange}
                error={Boolean(errors.box_width)}
                helperText={errors.box_width}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Height (cm)"
                name="box_height"
                type="number"
                value={formData.box_height}
                onChange={handleChange}
                error={Boolean(errors.box_height)}
                helperText={errors.box_height}
                inputProps={{ step: "0.1" }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Box Name/Description"
                name="box_name"
                value={formData.box_name}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Charges and Taxes
                </Typography>
              </Divider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Pre-tax Shipping Charge"
                name="pre_tax_shipping_charge"
                type="number"
                value={formData.pre_tax_shipping_charge}
                onChange={handleChange}
                error={Boolean(errors.pre_tax_shipping_charge)}
                helperText={errors.pre_tax_shipping_charge}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Fuel Surcharge"
                name="fuel_surcharge"
                type="number"
                value={formData.fuel_surcharge}
                onChange={handleChange}
                error={Boolean(errors.fuel_surcharge)}
                helperText={errors.fuel_surcharge}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tax 1 Type"
                name="tax1type"
                value={formData.tax1type}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tax 1 Amount"
                name="tax1amount"
                type="number"
                value={formData.tax1amount}
                onChange={handleChange}
                error={Boolean(errors.tax1amount)}
                helperText={errors.tax1amount}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tax 2 Type"
                name="tax2type"
                value={formData.tax2type}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tax 2 Amount"
                name="tax2amount"
                type="number"
                value={formData.tax2amount}
                onChange={handleChange}
                error={Boolean(errors.tax2amount)}
                helperText={errors.tax2amount}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tax 3 Type"
                name="tax3type"
                value={formData.tax3type}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tax 3 Amount"
                name="tax3amount"
                type="number"
                value={formData.tax3amount}
                onChange={handleChange}
                error={Boolean(errors.tax3amount)}
                helperText={errors.tax3amount}
                inputProps={{ step: "0.01" }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reference"
                name="reference"
                value={formData.reference}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/shipping/cad')}
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

export default CADShippingForm;