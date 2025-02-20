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
  FormHelperText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { billingApi, customerApi, handleApiError } from '../../utils/apiClient';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { Download as DownloadIcon, Close as CloseIcon } from '@mui/icons-material';

const BillingForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    customer: '',
    start_date: null,
    end_date: null,
    output_format: 'json'
  });
  const [customers, setCustomers] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [report, setReport] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState('excel');

  useEffect(() => {
    fetchCustomers();
    if (isEditMode) {
      fetchReport();
    }
  }, [id]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const response = await billingApi.get(id);
      if (response.success) {
        setFormData({
          customer: response.data.customer,
          start_date: new Date(response.data.start_date),
          end_date: new Date(response.data.end_date),
          output_format: 'json'
        });
        setReport(response.data);
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
    
    if (!formData.customer) {
      newErrors.customer = 'Customer is required';
    }
    
    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required';
    }
    
    if (!formData.end_date) {
      newErrors.end_date = 'End date is required';
    }

    if (formData.start_date && formData.end_date && formData.start_date > formData.end_date) {
      newErrors.end_date = 'End date must be after start date';
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
      // Format dates to YYYY-MM-DD
      const formatDate = (date) => {
        if (!date) return null;
        const d = new Date(date);
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      };

      // First generate preview
      const previewResponse = await billingApi.generateReport({
        customer: formData.customer,
        start_date: formatDate(formData.start_date),
        end_date: formatDate(formData.end_date),
        output_format: 'preview'
      });

      if (previewResponse.success) {
        setPreviewData(previewResponse.data);
        setShowPreview(true);
        setSuccess(true);
      }
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      setLoading(true);
      // Format dates to YYYY-MM-DD
      const formatDate = (date) => {
        if (!date) return null;
        const d = new Date(date);
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      };

      const response = await billingApi.generateReport({
        customer: formData.customer,
        start_date: formatDate(formData.start_date),
        end_date: formatDate(formData.end_date),
        output_format: format,
        report_id: previewData?.report_id
      });

      // Handle file download
      const blob = new Blob(
        [response.data],
        { 
          type: format === 'excel' 
            ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            : 'application/pdf'
        }
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `billing_report.${format === 'excel' ? 'xlsx' : 'pdf'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess(true);
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleClosePreview = () => {
    setShowPreview(false);
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
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          Generate Billing Report
        </Typography>

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Report generated successfully!
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
                  <FormHelperText>{errors.customer}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Start Date"
                  value={formData.start_date}
                  onChange={(newValue) => {
                    setFormData(prev => ({
                      ...prev,
                      start_date: newValue
                    }));
                    if (errors.start_date) {
                      setErrors(prev => ({
                        ...prev,
                        start_date: null
                      }));
                    }
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      fullWidth
                      error={Boolean(errors.start_date)}
                      helperText={errors.start_date}
                    />
                  )}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="End Date"
                  value={formData.end_date}
                  onChange={(newValue) => {
                    setFormData(prev => ({
                      ...prev,
                      end_date: newValue
                    }));
                    if (errors.end_date) {
                      setErrors(prev => ({
                        ...prev,
                        end_date: null
                      }));
                    }
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      fullWidth
                      error={Boolean(errors.end_date)}
                      helperText={errors.end_date}
                    />
                  )}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Export Format</InputLabel>
                <Select
                  name="format"
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                  label="Export Format"
                >
                  <MenuItem value="excel">Excel (.xlsx)</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {report && (
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Report Summary
                </Typography>
                <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                  <Typography>
                    Total Amount: {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD'
                    }).format(report.total_amount)}
                  </Typography>
                  <Typography>
                    Generated: {new Date(report.generated_at).toLocaleString()}
                  </Typography>
                </Box>
              </Grid>
            )}

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/billing')}
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
                    'Generate Report'
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {/* Preview Dialog */}
      <Dialog
        open={showPreview}
        onClose={handleClosePreview}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            Report Preview
            <IconButton onClick={handleClosePreview}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {previewData && (
            <>
              <Typography variant="h6" gutterBottom>
                {previewData.customer_name || 'Customer Report'}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Period: {new Date(previewData.start_date).toLocaleDateString()} to{' '}
                {new Date(previewData.end_date).toLocaleDateString()}
              </Typography>
              
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Order ID</TableCell>
                      <TableCell>Services</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(previewData.preview_data?.orders || []).map((order) => (
                      <TableRow key={order.order_id}>
                        <TableCell>{order.order_id}</TableCell>
                        <TableCell>
                          {(order.services || []).map((service, index) => (
                            <div key={service.service_id || index}>
                              {service.service_name}: ${service.amount || '0.00'}
                            </div>
                          ))}
                        </TableCell>
                        <TableCell align="right">
                          ${order.total_amount || '0.00'}
                        </TableCell>
                        <TableCell>{order.date || ''}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={2} align="right">
                        <strong>Total Amount:</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>${previewData.total_amount || '0.00'}</strong>
                      </TableCell>
                      <TableCell />
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreview}>Close</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleExport(selectedFormat)}
            startIcon={<DownloadIcon />}
          >
            Export as {selectedFormat === 'excel' ? 'Excel' : 'PDF'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BillingForm; 