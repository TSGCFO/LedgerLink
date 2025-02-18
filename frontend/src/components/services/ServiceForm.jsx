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
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { serviceApi, handleApiError } from '../../utils/apiClient';

const ServiceForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    service_name: '',
    description: '',
    charge_type: 'quantity'  // Use the default value from the backend
  });
  const [chargeTypes, setChargeTypes] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const fetchChargeTypes = useCallback(async () => {
    try {
      const response = await serviceApi.getChargeTypes();
      if (response.success) {
        setChargeTypes(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  }, []);

  const fetchService = useCallback(async () => {
    try {
      setLoading(true);
      const response = await serviceApi.get(id);
      console.log('Service data:', response);
      if (response) {
        setFormData({
          service_name: response.service_name,
          description: response.description || '',
          charge_type: response.charge_type
        });
      }
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchChargeTypes();
    if (isEditMode) {
      fetchService();
    }
  }, [id, isEditMode, fetchChargeTypes, fetchService]);

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.service_name.trim()) {
      newErrors.service_name = 'Service name is required';
    }
    
    if (!formData.charge_type) {
      newErrors.charge_type = 'Charge type is required';
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
    // Clear error when user starts typing
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
        ? () => serviceApi.update(id, formData)
        : () => serviceApi.create(formData);

      const response = await apiCall();

      if (response.success) {
        setSuccess(true);
        // Navigate immediately instead of using setTimeout
        navigate('/services');
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
          {isEditMode ? 'Edit Service' : 'New Service'}
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Service {isEditMode ? 'updated' : 'created'} successfully!
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Service Name"
                name="service_name"
                value={formData.service_name}
                onChange={handleChange}
                error={Boolean(errors.service_name)}
                helperText={errors.service_name}
                variant="outlined"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                multiline
                rows={4}
                variant="outlined"
              />
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth error={Boolean(errors.charge_type)}>
                <InputLabel>Charge Type</InputLabel>
                <Select
                  name="charge_type"
                  value={formData.charge_type}
                  onChange={handleChange}
                  label="Charge Type"
                >
                  {chargeTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
                {errors.charge_type && (
                  <Typography color="error" variant="caption">
                    {errors.charge_type}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/services')}
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
                    isEditMode ? 'Update Service' : 'Create Service'
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

export default ServiceForm;