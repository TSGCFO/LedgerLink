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
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { MaterialReactTable } from 'material-react-table';
import { useNavigate } from 'react-router-dom';
import { customerApi, handleApiError } from '../../utils/apiClient';

const CustomerList = () => {
  const [customers, setCustomers] = useState([]);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.business_type) params.business_type = filters.business_type;
      
      const response = await customerApi.list(params);
      if (response.success) {
        setCustomers(response.data);
        console.log('Customers data:', response.data);
      } else {
        console.error('Failed to fetch customers:', response);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        const response = await customerApi.delete(id);
        if (response.success) {
          setSuccessMessage('Customer deleted successfully');
          fetchCustomers();
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

  const getStatusColor = (isActive) => {
    return isActive ? 'success' : 'error';
  };

  const columns = useMemo(
    () => [
      {
        accessorKey: 'company_name',
        header: 'Company Name',
        size: 200,
      },
      {
        accessorKey: 'legal_business_name',
        header: 'Legal Name',
        size: 200,
      },
      {
        accessorKey: 'email',
        header: 'Email',
        size: 200,
      },
      {
        accessorKey: 'phone',
        header: 'Phone',
        size: 150,
      },
      {
        accessorKey: 'address',
        header: 'Address',
        size: 200,
      },
      {
        accessorKey: 'city',
        header: 'City',
        size: 150,
      },
      {
        accessorKey: 'state',
        header: 'State',
        size: 100,
      },
      {
        accessorKey: 'zip',
        header: 'ZIP',
        size: 100,
      },
      {
        accessorKey: 'country',
        header: 'Country',
        size: 150,
      },
      {
        accessorKey: 'business_type',
        header: 'Business Type',
        size: 150,
      },
      {
        accessorKey: 'is_active',
        header: 'Status',
        size: 100,
        Cell: ({ cell }) => (
          <Chip
            label={cell.getValue() ? 'Active' : 'Inactive'}
            color={getStatusColor(cell.getValue())}
            size="small"
          />
        ),
        filterVariant: 'select',
        filterSelectOptions: [
          { text: 'Active', value: true },
          { text: 'Inactive', value: false },
        ],
      },
      {
        accessorKey: 'created_at',
        header: 'Created',
        size: 150,
        Cell: ({ cell }) => new Date(cell.getValue()).toLocaleString(),
      },
      {
        accessorKey: 'updated_at',
        header: 'Updated',
        size: 150,
        Cell: ({ cell }) => new Date(cell.getValue()).toLocaleString(),
      },
      {
        id: 'actions',
        header: 'Actions',
        size: 100,
        // eslint-disable-next-line react/prop-types
        Cell: ({ row: { original } }) => (
          <Box>
            <IconButton
              onClick={() => navigate(`/customers/${original.id}/edit`)}
              color="primary"
              size="small"
            >
              <EditIcon />
            </IconButton>
            <IconButton
              onClick={() => handleDelete(original.id)}
              color="error"
              size="small"
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        ),
      },
    ],
    [navigate]
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
        <MaterialReactTable
          columns={columns}
          data={customers}
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
              onClick={() => navigate('/customers/new')}
            >
              New Customer
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

export default CustomerList;