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
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchReports();
    fetchCustomers();
  }, []);

  const fetchReports = async (filters = {}) => {
    try {
      const params = {
        ...filters,
        start_date: startDate?.toISOString().split('T')[0],
        end_date: endDate?.toISOString().split('T')[0],
      };
      
      const response = await billingApi.list(params);
      console.log('Billing reports response:', response);
      
      if (response.success) {
        const reportData = response.data?.data || [];
        console.log('Setting reports:', reportData);
        setReports(reportData);
      } else {
        console.error('Failed to fetch reports:', response.error);
        setError(response.error || 'Failed to fetch reports');
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
      setError(handleApiError(error));
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

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this billing report?')) {
      try {
        const response = await billingApi.delete(id);
        if (response.success) {
          setSuccessMessage('Billing report deleted successfully');
          fetchReports();
        }
      } catch (error) {
        setError(handleApiError(error));
      }
    }
  };

  const handleDownload = async (id, format = 'json') => {
    try {
      const response = await billingApi.generateReport({
        report_id: id,
        output_format: format
      });
      
      // Handle the downloaded file based on format
      const blob = new Blob([response.data], {
        type: format === 'csv' ? 'text/csv' : 'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `billing-report-${id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  const handleCloseSuccess = () => {
    setSuccessMessage('');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const columns = useMemo(
    () => [
      {
        accessorKey: 'customer_details.company_name',
        header: 'Customer',
        size: 200,
        Cell: ({ row }) => row.original.customer_details?.company_name || 'N/A',
        filterVariant: 'select',
        filterSelectOptions: customers.map(customer => ({
          text: customer.company_name,
          value: customer.id,
        })),
      },
      {
        accessorKey: 'start_date',
        header: 'Start Date',
        size: 120,
        Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleDateString() : 'N/A',
      },
      {
        accessorKey: 'end_date',
        header: 'End Date',
        size: 120,
        Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleDateString() : 'N/A',
      },
      {
        accessorKey: 'total_amount',
        header: 'Total Amount',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
        Footer: ({ table }) => {
          const total = table.getFilteredRowModel().rows.reduce(
            (sum, row) => sum + (parseFloat(row.original.total_amount) || 0),
            0
          );
          return <strong>{formatCurrency(total)}</strong>;
        },
      },
      {
        accessorKey: 'generated_at',
        header: 'Generated',
        size: 150,
        Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleString() : 'N/A',
      },
      {
        id: 'actions',
        header: 'Actions',
        size: 200,
        Cell: ({ row: { original } }) => (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="View Details">
              <IconButton
                onClick={() => navigate(`/billing/${original.id}/edit`)}
                color="primary"
                size="small"
              >
                <EditIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Download JSON">
              <IconButton
                onClick={() => handleDownload(original.id, 'json')}
                color="secondary"
                size="small"
              >
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Download CSV">
              <IconButton
                onClick={() => handleDownload(original.id, 'csv')}
                color="info"
                size="small"
              >
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton
                onClick={() => handleDelete(original.id)}
                color="error"
                size="small"
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        ),
      },
    ],
    [customers, navigate]
  );

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

      <Snackbar
        open={Boolean(successMessage)}
        autoHideDuration={6000}
        onClose={handleCloseSuccess}
      >
        <Alert onClose={handleCloseSuccess} severity="success">
          {successMessage}
        </Alert>
      </Snackbar>

      <Paper sx={{ width: '100%', mb: 2, p: 2 }}>
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Start Date"
              value={startDate}
              onChange={(newValue) => {
                setStartDate(newValue);
                fetchReports();
              }}
              renderInput={(params) => <TextField {...params} size="small" />}
            />
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newValue) => {
                setEndDate(newValue);
                fetchReports();
              }}
              renderInput={(params) => <TextField {...params} size="small" />}
            />
          </LocalizationProvider>
        </Box>

        <MaterialReactTable
          columns={columns}
          data={reports}
          enableColumnFiltering
          enableGlobalFilter
          enablePagination
          enableSorting
          enableColumnResizing
          columnResizeMode="onChange"
          muiToolbarAlertBannerProps={
            error
              ? {
                  color: 'error',
                  children: error,
                }
              : undefined
          }
          renderTopToolbarCustomActions={() => (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/billing/new')}
            >
              New Billing Report
            </Button>
          )}
          muiTableProps={{
            sx: {
              tableLayout: 'auto',
            },
          }}
          initialState={{
            density: 'compact',
            pagination: { pageSize: 10 },
            sorting: [{ id: 'generated_at', desc: true }],
          }}
        />
      </Paper>
    </Box>
  );
};

export default BillingList; 