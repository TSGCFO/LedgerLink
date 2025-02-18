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
import { cadShippingApi, customerApi, handleApiError } from '../../utils/apiClient';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';

const CADShippingList = () => {
  const [shipments, setShipments] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [carriers, setCarriers] = useState([]);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchShipments();
    fetchCustomers();
    fetchCarriers();
  }, []);

  const fetchShipments = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.customer) params.customer = filters.customer;
      if (filters.carrier) params.carrier = filters.carrier;
      if (startDate) params.start_date = startDate.toISOString().split('T')[0];
      if (endDate) params.end_date = endDate.toISOString().split('T')[0];
      
      const response = await cadShippingApi.list(params);
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

  const fetchCarriers = async () => {
    try {
      const response = await cadShippingApi.getCarriers();
      if (response.success) {
        setCarriers(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this shipping record?')) {
      try {
        const response = await cadShippingApi.delete(id);
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
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount || 0);
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
        accessorKey: 'service_code_description',
        header: 'Service',
        size: 150,
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
        accessorKey: 'shiptoaddress3',
        header: 'Address 3',
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
        accessorKey: 'ship_to_country',
        header: 'Country',
        size: 100,
      },
      {
        accessorKey: 'ship_to_postal_code',
        header: 'Postal Code',
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
        accessorKey: 'pre_tax_shipping_charge',
        header: 'Pre-tax Charge',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'tax1type',
        header: 'Tax 1 Type',
        size: 100,
      },
      {
        accessorKey: 'tax1amount',
        header: 'Tax 1',
        size: 100,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'tax2type',
        header: 'Tax 2 Type',
        size: 100,
      },
      {
        accessorKey: 'tax2amount',
        header: 'Tax 2',
        size: 100,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'tax3type',
        header: 'Tax 3 Type',
        size: 100,
      },
      {
        accessorKey: 'tax3amount',
        header: 'Tax 3',
        size: 100,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'fuel_surcharge',
        header: 'Fuel Surcharge',
        size: 120,
        Cell: ({ cell }) => formatCurrency(cell.getValue()),
      },
      {
        accessorKey: 'reference',
        header: 'Reference',
        size: 150,
      },
      {
        accessorKey: 'weight',
        header: 'Weight',
        size: 100,
      },
      {
        accessorKey: 'gross_weight',
        header: 'Gross Weight',
        size: 120,
      },
      {
        accessorKey: 'box_length',
        header: 'Length',
        size: 100,
      },
      {
        accessorKey: 'box_width',
        header: 'Width',
        size: 100,
      },
      {
        accessorKey: 'box_height',
        header: 'Height',
        size: 100,
      },
      {
        accessorKey: 'box_name',
        header: 'Box Name',
        size: 120,
      },
      {
        accessorKey: 'carrier',
        header: 'Carrier',
        size: 120,
        filterVariant: 'select',
        filterSelectOptions: carriers.map(carrier => ({
          text: carrier,
          value: carrier,
        })),
      },
      {
        accessorKey: 'ship_date',
        header: 'Ship Date',
        size: 150,
        Cell: ({ cell }) =>
          cell.getValue()
            ? new Date(cell.getValue()).toLocaleDateString()
            : 'Not Shipped',
      },
      {
        id: 'actions',
        header: 'Actions',
        size: 100,
        Cell: ({ row: { original } }) => (
          <Box>
            <IconButton
              onClick={() => navigate(`/shipping/cad/${original.transaction}/edit`)}
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
    [customers, carriers, navigate]
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
              onClick={() => navigate('/shipping/cad/new')}
            >
              New CAD Shipment
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

export default CADShippingList;