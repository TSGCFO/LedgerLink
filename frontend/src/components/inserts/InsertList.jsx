/* eslint-disable react/prop-types */
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
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  AddCircle as AddCircleIcon,
  RemoveCircle as RemoveCircleIcon,
} from '@mui/icons-material';
import { MaterialReactTable } from 'material-react-table';
import { useNavigate } from 'react-router-dom';
import { insertApi, customerApi, handleApiError } from '../../utils/apiClient';

const InsertList = () => {
  const [inserts, setInserts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [stats, setStats] = useState({});
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchInserts();
    fetchCustomers();
    fetchStats();
  }, []);

  const fetchInserts = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.customer) params.customer = filters.customer;
      if (filters.min_quantity) params.min_quantity = filters.min_quantity;
      if (filters.max_quantity) params.max_quantity = filters.max_quantity;
      
      const response = await insertApi.list(params);
      if (response.success) {
        setInserts(response.data);
      } else {
        console.error('Failed to fetch inserts:', response);
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
      } else {
        console.error('Failed to fetch customers:', response);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const fetchStats = async () => {
    try {
      const response = await insertApi.getStats();
      if (response.success) {
        setStats(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this insert?')) {
      try {
        const response = await insertApi.delete(id);
        if (response.success) {
          setSuccessMessage('Insert deleted successfully');
          fetchInserts();
          fetchStats();
        }
      } catch (error) {
        setError(handleApiError(error));
      }
    }
  };

  const handleUpdateQuantity = async (id, quantity, operation) => {
    try {
      const response = await insertApi.updateQuantity(id, quantity, operation);
      if (response.success) {
        setSuccessMessage(`Quantity ${operation}ed successfully`);
        fetchInserts();
        fetchStats();
      }
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

  const columns = useMemo(
    () => [
      {
        accessorKey: 'sku',
        header: 'SKU',
        size: 120,
      },
      {
        accessorKey: 'insert_name',
        header: 'Name',
        size: 200,
      },
      {
        accessorKey: 'customer_details.company_name',
        header: 'Customer',
        size: 200,
        filterVariant: 'select',
        filterSelectOptions: customers.map(customer => ({
          text: customer.company_name,
          value: customer.id,
        })),
        Cell: ({ cell }) => cell.getValue() || 'N/A',
      },
      {
        accessorKey: 'insert_quantity',
        header: 'Quantity',
        size: 150,
        Cell: ({ row: { original } }) => (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {original.insert_quantity}
            <IconButton
              size="small"
              onClick={() => handleUpdateQuantity(original.id, 1, 'add')}
              color="primary"
            >
              <AddCircleIcon />
            </IconButton>
            <IconButton
              size="small"
              onClick={() => handleUpdateQuantity(original.id, 1, 'subtract')}
              color="error"
              disabled={original.insert_quantity <= 0}
            >
              <RemoveCircleIcon />
            </IconButton>
          </Box>
        ),
        Filter: ({ column }) => (
          <Box sx={{ display: 'flex', gap: 1, p: 1 }}>
            <input
              type="number"
              placeholder="Min"
              onChange={(e) => {
                column.setFilterValue((prev) => [
                  e.target.value,
                  prev?.[1],
                ]);
              }}
              style={{ width: 60 }}
            />
            <input
              type="number"
              placeholder="Max"
              onChange={(e) => {
                column.setFilterValue((prev) => [
                  prev?.[0],
                  e.target.value,
                ]);
              }}
              style={{ width: 60 }}
            />
          </Box>
        ),
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
        Cell: ({ row: { original } }) => (
          <Box>
            <IconButton
              onClick={() => navigate(`/inserts/${original.id}/edit`)}
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
        <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <Grid item>
            <Chip
              label={`Total Inserts: ${stats.total_inserts || 0}`}
              color="primary"
              variant="outlined"
            />
          </Grid>
          <Grid item>
            <Chip
              label={`Total Quantity: ${stats.total_quantity || 0}`}
              color="secondary"
              variant="outlined"
            />
          </Grid>
        </Grid>

        <MaterialReactTable
          columns={columns}
          data={inserts}
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
              onClick={() => navigate('/inserts/new')}
            >
              New Insert
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

export default InsertList;