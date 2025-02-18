/* eslint-disable react/prop-types */
import { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  IconButton,
  Button,
  Alert,
  Snackbar,
  Chip,
  TextField,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { MaterialReactTable } from 'material-react-table';
import { useNavigate } from 'react-router-dom';
import { usShippingApi, customerApi, handleApiError } from '../../utils/apiClient';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';

const USShippingList = () => {
  const [shipments, setShipments] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [statuses, setStatuses] = useState({ current: [], delivery: [] });
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchShipments();
    fetchCustomers();
    fetchStatuses();
  }, []);

  const fetchShipments = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.customer) params.customer = filters.customer;
      if (filters.current_status) params.current_status = filters.current_status;
      if (filters.delivery_status) params.delivery_status = filters.delivery_status;
      if (startDate) params.start_date = startDate.toISOString().split('T')[0];
      if (endDate) params.end_date = endDate.toISOString().split('T')[0];
      
      const response = await usShippingApi.list(params);
      if (response.success) {
        setShipments(response.data);
      }
    } catch (error) {
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

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this shipping record?')) {
      try {
        const response = await usShippingApi.delete(id);
        if (response.success) {
          setSuccessMessage('Shipping record deleted successfully');
          fetchShipments();
        }
      } catch (error) {
        setError(handleApiError(error));
      }
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

  const getStatusColor = (status) => {
    const colors = {
      'delivered': 'success',
      'in transit': 'primary',
      'pending': 'warning',
      'delayed': 'error',
      'cancelled': 'default'
    };
    return colors[status?.toLowerCase()] || 'default';
  };

  const columns = useMemo(
    () => [
      {
        accessorKey: 'transaction',
        header: 'Order ID',
        size: 100,
      },
      {
        accessorKey: 'customer_details.company_name',
        header: 'Customer',
        size: 150,
        filterVariant: 'select',
        filterSelectOptions: customers.map(customer => ({
          text: customer.company_name,
          value: customer.id,
        })),
      },
      {
        accessorKey: 'ship_date',
        header: 'Ship Date',
        size: 120,
        Cell: ({ cell }) =>
          cell.getValue()
            ? new Date(cell.getValue()).toLocaleDateString()
            : 'Not Shipped',
      },
      {
        accessorKey: 'ship_to_name',
        header: 'Ship To Name',
        size: 150,
      },
      {
        accessorKey: 'ship_to_address_1',
        header: 'Address 1',
        size: 150,
      },
      {
        accessorKey: 'ship_to_address_2',
        header: 'Address 2',
        size: 150,
      },
      {
        accessorKey: 'ship_to_city',
        header: 'City',
        size: 120,
      },
      {
        accessorKey: 'ship_to_state',
        header: 'State',
        size: 100,
      },
      {
        accessorKey: 'ship_to_zip',
        header: 'ZIP',
        size: 100,
      },
      {
        accessorKey: 'ship_to_country_code',
        header: 'Country',
        size: 100,
      },
      {
        accessorKey: 'tracking_number',
        header: 'Tracking #',
        size: 130,
        Cell: ({ cell }) => (
          <Chip
            label={cell.getValue() || 'No Tracking'}
            color={cell.getValue() ? 'primary' : 'default'}
            size="small"
          />
        ),
      },
      {
        accessorKey: 'service_name',
        header: 'Service',
        size: 150,
      },
      {
        accessorKey: 'weight_lbs',
        header: 'Weight (lbs)',
        size: 120,
      },
      {
        accessorKey: 'length_in',
        header: 'Length (in)',
        size: 120,
      },
      {
        accessorKey: 'width_in',
        header: 'Width (in)',
        size: 120,
      },
      {
        accessorKey: 'height_in',
        header: 'Height (in)',
        size: 120,
      },
      {
        accessorKey: 'base_chg',
        header: 'Base Charge',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'carrier_peak_charge',
        header: 'Carrier Peak',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'wizmo_peak_charge',
        header: 'Wizmo Peak',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'accessorial_charges',
        header: 'Accessorial',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'rate',
        header: 'Rate',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'hst',
        header: 'HST',
        size: 100,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'gst',
        header: 'GST',
        size: 100,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'current_status',
        header: 'Status',
        size: 120,
        Cell: ({ cell }) => (
          <Chip
            label={cell.getValue()}
            color={getStatusColor(cell.getValue())}
            size="small"
          />
        ),
        filterVariant: 'select',
        filterSelectOptions: statuses.current?.map(status => ({
          text: status,
          value: status,
        })) || [],
      },
      {
        accessorKey: 'delivery_status',
        header: 'Delivery',
        size: 120,
        Cell: ({ cell }) => (
          <Chip
            label={cell.getValue()}
            color={getStatusColor(cell.getValue())}
            size="small"
          />
        ),
      },
      {
        accessorKey: 'first_attempt_date',
        header: 'First Attempt',
        size: 120,
        Cell: ({ cell }) =>
          cell.getValue()
            ? new Date(cell.getValue()).toLocaleDateString()
            : 'N/A',
      },
      {
        accessorKey: 'delivery_date',
        header: 'Delivered',
        size: 120,
        Cell: ({ cell }) =>
          cell.getValue()
            ? new Date(cell.getValue()).toLocaleDateString()
            : 'Not Delivered',
      },
      {
        accessorKey: 'days_to_first_deliver',
        header: 'Days to Deliver',
        size: 120,
      },
      {
        id: 'actions',
        header: 'Actions',
        size: 100,
        Cell: ({ row: { original } }) => (
          <Box>
            <IconButton
              onClick={() => navigate(`/shipping/us/${original.transaction}/edit`)}
              color="primary"
              size="small"
            >
              <EditIcon />
            </IconButton>
            <IconButton
              onClick={() => handleDelete(original.transaction)}
              color="error"
              size="small"
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        ),
      },
    ],
    [customers, statuses, navigate]
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
                fetchShipments();
              }}
              renderInput={(params) => <TextField {...params} size="small" />}
            />
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newValue) => {
                setEndDate(newValue);
                fetchShipments();
              }}
              renderInput={(params) => <TextField {...params} size="small" />}
            />
          </LocalizationProvider>
        </Box>

        <MaterialReactTable
          columns={columns}
          data={shipments}
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
              onClick={() => navigate('/shipping/us/new')}
            >
              New US Shipment
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
          }}
        />
      </Paper>
    </Box>
  );
};

export default USShippingList;