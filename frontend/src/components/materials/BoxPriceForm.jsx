import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Grid,
  Alert,
} from '@mui/material';
import axios from 'axios';

const BoxPriceForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    box_type: '',
    price: '',
    length: '',
    width: '',
    height: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isEditing) {
      fetchBoxPrice();
    }
  }, [id]);

  const fetchBoxPrice = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`/api/box-prices/${id}/`);
      setFormData({
        box_type: response.data.box_type,
        price: response.data.price.toString(),
        length: response.data.length.toString(),
        width: response.data.width.toString(),
        height: response.data.height.toString(),
      });
    } catch (error) {
      setError('Failed to fetch box price details');
      console.error('Error fetching box price:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!formData.box_type.trim()) {
      setError('Box type is required');
      return false;
    }
    
    const numericFields = ['price', 'length', 'width', 'height'];
    for (const field of numericFields) {
      if (!formData[field] || isNaN(formData[field]) || parseFloat(formData[field]) <= 0) {
        setError(`Please enter a valid ${field.replace('_', ' ')}`);
        return false;
      }
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      setIsLoading(true);
      setError('');

      const payload = {
        ...formData,
        price: parseFloat(formData.price),
        length: parseFloat(formData.length),
        width: parseFloat(formData.width),
        height: parseFloat(formData.height),
      };

      if (isEditing) {
        await axios.put(`/api/box-prices/${id}/`, payload);
      } else {
        await axios.post('/api/box-prices/', payload);
      }

      navigate('/box-prices');
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to save box price');
      console.error('Error saving box price:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {isEditing ? 'Edit Box Price' : 'Add New Box Price'}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Box Type"
                name="box_type"
                value={formData.box_type}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Price"
                name="price"
                type="number"
                value={formData.price}
                onChange={handleChange}
                required
                disabled={isLoading}
                inputProps={{
                  step: "0.01",
                  min: "0"
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Length (cm)"
                name="length"
                type="number"
                value={formData.length}
                onChange={handleChange}
                required
                disabled={isLoading}
                inputProps={{
                  step: "0.01",
                  min: "0"
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Width (cm)"
                name="width"
                type="number"
                value={formData.width}
                onChange={handleChange}
                required
                disabled={isLoading}
                inputProps={{
                  step: "0.01",
                  min: "0"
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Height (cm)"
                name="height"
                type="number"
                value={formData.height}
                onChange={handleChange}
                required
                disabled={isLoading}
                inputProps={{
                  step: "0.01",
                  min: "0"
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/box-prices')}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Saving...' : 'Save Box Price'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
};

export default BoxPriceForm;