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
import { serviceApi, handleApiError } from '../../utils/apiClient';

const ServiceList = () => {
  const [services, setServices] = useState([]);
  const [chargeTypes, setChargeTypes] = useState([]);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchServices();
    fetchChargeTypes();
  }, []);

  const fetchServices = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.charge_type) params.charge_type = filters.charge_type;
      
      const response = await serviceApi.list(params);
      if (response.success) {
        setServices(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const fetchChargeTypes = async () => {
    try {
      const response = await serviceApi.getChargeTypes();
      if (response.success) {
        setChargeTypes(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this service?')) {
      try {
        const response = await serviceApi.delete(id);
        if (response.success) {
          setSuccessMessage('Service deleted successfully');
          fetchServices();
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

  const columns = useMemo(
    () => [
      {
        accessorKey: 'service_name',
        header: 'Service Name',
        size: 200,
      },
      {
        accessorKey: 'description',
        header: 'Description',
        size: 300,
      },
      {
        accessorKey: 'charge_type',
        header: 'Charge Type',
        size: 150,
        Cell: ({ cell }) => (
          <Chip
            label={chargeTypes.find(t => t.value === cell.getValue())?.label || cell.getValue()}
            color="primary"
            variant="outlined"
            size="small"
          />
        ),
        filterVariant: 'select',
        filterSelectOptions: chargeTypes.map(type => ({
          text: type.label,
          value: type.value,
        })),
      },
      {
        id: 'actions',
        header: 'Actions',
        size: 100,
        Cell: ({ row: { original } }) => (
          <Box>
            <IconButton
              onClick={() => navigate(`/services/${original.id}/edit`)}
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
    [chargeTypes, navigate]
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
          data={services}
          enableColumnFiltering
          enableGlobalFilter
          enablePagination
          enableSorting
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
              onClick={() => navigate('/services/new')}
            >
              New Service
            </Button>
          )}
          muiTableProps={{
            sx: {
              tableLayout: 'fixed',
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

export default ServiceList;