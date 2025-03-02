import { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  IconButton,
  Button,
  Alert,
  Snackbar,
  Grid,
  Chip,
  TextField,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  CircularProgress,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { MaterialReactTable } from 'material-react-table';
import { useNavigate } from 'react-router-dom';
import { billingApi, customerApi, handleApiError } from '../../utils/apiClient';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';

const BillingList = () => {
  const [reports, setReports] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [billingData, setBillingData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCustomers();
  }, []);

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

  const handleCalculate = async () => {
    if (!selectedCustomer || !startDate || !endDate) {
      setError('Please select a customer and date range');
      return;
    }

    if (startDate > endDate) {
      setError('Start date must be before end date');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await billingApi.generateReport({
        customer: selectedCustomer,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        output_format: 'preview'
      });

      if (response.success && response.data?.preview_data) {
        // Transform the data for the table
        const transformedData = response.data.preview_data.orders.map(order => {
          const row = {
            order_id: order.order_id,
            total_amount: order.total_amount,
            services: order.services, // Keep the full services array for column generation
          };
          
          // Add service amounts as columns
          order.services.forEach(service => {
            row[`service_${service.service_id}`] = service.amount;
          });
          
          return row;
        });

        setBillingData(transformedData);
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

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const columns = useMemo(() => {
    if (!billingData.length) return [];

    // Start with the basic columns
    const baseColumns = [
      {
        accessorKey: 'order_id',
        header: 'Order ID',
        size: 120,
      },
      {
        accessorKey: 'total_amount',
        header: 'Total Amount',
        size: 150,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
        Footer: ({ table }) => {
          const total = table.getFilteredRowModel().rows.reduce(
            (sum, row) => sum + parseFloat(row.original.total_amount || 0),
            0
          );
          return <strong>{formatCurrency(total)}</strong>;
        },
      },
    ];

    // Add service columns dynamically based on the first row's services
    const firstRow = billingData[0];
    const serviceColumns = firstRow.services.map(service => ({
      accessorKey: `service_${service.service_id}`,
      header: service.service_name,
      size: 150,
      Cell: ({ cell }) => formatCurrency(cell.getValue()),
      Footer: ({ table }) => {
        const total = table.getFilteredRowModel().rows.reduce(
          (sum, row) => sum + parseFloat(row[`service_${service.service_id}`] || 0),
          0
        );
        return <strong>{formatCurrency(total)}</strong>;
      },
    }));

    return [...baseColumns, ...serviceColumns];
  }, [billingData]);

  return (
    <Box sx={{ width: '100%', mb: 2 }}>
      <Snackbar
        open={Boolean(error)}
        autoHideDuration={6000}
        onClose={handleCloseError}
      >
        <Alert onClose={handleCloseError} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Paper sx={{ width: '100%', mb: 2, p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Generate Billing Report
        </Typography>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Customer</InputLabel>
              <Select
                value={selectedCustomer}
                onChange={(e) => setSelectedCustomer(e.target.value)}
                label="Customer"
              >
                {customers.map((customer) => (
                  <MenuItem key={customer.id} value={customer.id}>
                    {customer.company_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={startDate}
                onChange={setStartDate}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
          </Grid>

          <Grid item xs={12} md={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="End Date"
                value={endDate}
                onChange={setEndDate}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
          </Grid>

          <Grid item xs={12} md={2}>
            <Button
              variant="contained"
              onClick={handleCalculate}
              disabled={loading}
              fullWidth
              sx={{ height: '56px' }}
            >
              {loading ? <CircularProgress size={24} /> : 'Calculate'}
            </Button>
          </Grid>
        </Grid>

        {billingData.length > 0 && (
          <MaterialReactTable
            columns={columns}
            data={billingData}
            enableColumnFiltering
            enableGlobalFilter
            enablePagination
            enableSorting
            enableColumnResizing
            columnResizeMode="onChange"
            muiTableProps={{
              sx: {
                tableLayout: 'auto',
              },
            }}
            initialState={{
              density: 'compact',
              pagination: { pageSize: 10 },
              sorting: [{ id: 'order_id', desc: false }],
            }}
          />
        )}
      </Paper>
    </Box>
  );
};

export default BillingList; 