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
} from '@mui/icons-material';
import { MaterialReactTable } from 'material-react-table';
import { useNavigate } from 'react-router-dom';
import { productApi, handleApiError } from '../../utils/apiClient';

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState({ total_products: 0, products_by_customer: [] });
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, []);

  const fetchProducts = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.customer) params.customer = filters.customer;
      
      const response = await productApi.list(params);
      if (response.success) {
        setProducts(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const fetchStats = async () => {
    try {
      const response = await productApi.getStats();
      if (response.success) {
        setStats(response.data);
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        const response = await productApi.delete(id);
        if (response.success) {
          setSuccessMessage('Product deleted successfully');
          fetchProducts();
          fetchStats();
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
        accessorKey: 'sku',
        header: 'SKU',
        size: 120,
      },
      {
        accessorKey: 'customer_details.company_name',
        header: 'Customer',
        size: 150,
      },
      {
        accessorKey: 'labeling_unit_1',
        header: 'Unit 1',
        size: 100,
      },
      {
        accessorKey: 'labeling_quantity_1',
        header: 'Qty 1',
        size: 80,
      },
      {
        accessorKey: 'labeling_unit_2',
        header: 'Unit 2',
        size: 100,
      },
      {
        accessorKey: 'labeling_quantity_2',
        header: 'Qty 2',
        size: 80,
      },
      {
        accessorKey: 'labeling_unit_3',
        header: 'Unit 3',
        size: 100,
      },
      {
        accessorKey: 'labeling_quantity_3',
        header: 'Qty 3',
        size: 80,
      },
      {
        accessorKey: 'labeling_unit_4',
        header: 'Unit 4',
        size: 100,
      },
      {
        accessorKey: 'labeling_quantity_4',
        header: 'Qty 4',
        size: 80,
      },
      {
        accessorKey: 'labeling_unit_5',
        header: 'Unit 5',
        size: 100,
      },
      {
        accessorKey: 'labeling_quantity_5',
        header: 'Qty 5',
        size: 80,
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
              onClick={() => navigate(`/products/${original.id}/edit`)}
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
        <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <Grid item>
            <Chip
              label={`Total Products: ${stats.total_products || 0}`}
              color="primary"
              variant="outlined"
            />
          </Grid>
          {stats.products_by_customer?.map((stat) => (
            <Grid item key={stat.customer__company_name}>
              <Chip
                label={`${stat.customer__company_name}: ${stat.count}`}
                color="secondary"
                variant="outlined"
              />
            </Grid>
          ))}
        </Grid>

        <MaterialReactTable
          columns={columns}
          data={products}
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
              onClick={() => navigate('/products/new')}
            >
              New Product
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

export default ProductList;