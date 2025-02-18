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
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { MaterialReactTable } from 'material-react-table';
import { useNavigate } from 'react-router-dom';
import { orderApi, handleApiError } from '../../utils/apiClient';

const OrderList = () => {
  const [orders, setOrders] = useState([]);
  const [statusCounts, setStatusCounts] = useState({});
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchOrders();
  }, []);

  useEffect(() => {
    updateStatusCounts();
  }, [orders]);

  const fetchOrders = async (filters = {}) => {
    try {
      const params = {};
      if (filters.search) params.search = filters.search;
      
      const response = await orderApi.list(params);
      if (response.success) {
        setOrders(response.data);
        updateStatusCounts();
      }
    } catch (error) {
      setError(handleApiError(error));
    }
  };

  const updateStatusCounts = () => {
    const counts = {
      draft: 0,
      submitted: 0,
      shipped: 0,
      delivered: 0
    };

    orders.forEach(order => {
      // Use the same logic as getOrderStatus
      if (order.close_date) {
        counts.delivered++;
      } else if (order.carrier) {
        counts.shipped++;
      } else if (order.ship_to_name && order.ship_to_address) {
        counts.submitted++;
      } else {
        counts.draft++;
      }
    });

    setStatusCounts(counts);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this order?')) {
      try {
        const response = await orderApi.delete(id);
        if (response.success) {
          setSuccessMessage('Order deleted successfully');
          fetchOrders();
        }
      } catch (error) {
        setError(handleApiError(error));
      }
    }
  };

  const handleCancel = async (id) => {
    if (window.confirm('Are you sure you want to cancel this order?')) {
      try {
        const response = await orderApi.cancel(id);
        if (response.success) {
          setSuccessMessage('Order cancelled successfully');
          fetchOrders();
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

  const getOrderStatus = (order) => {
    // If close_date exists, the order is delivered
    if (order.close_date) {
      return { status: 'delivered', color: 'success' };
    }
    // If carrier exists but no close_date, the order is shipped
    if (order.carrier) {
      return { status: 'shipped', color: 'info' };
    }
    // If shipping details exist but no carrier, the order is submitted
    if (order.ship_to_name && order.ship_to_address) {
      return { status: 'submitted', color: 'primary' };
    }
    // Default state is draft
    return { status: 'draft', color: 'default' };
  };

  const getOrderPriority = (order) => {
    // Determine priority based on total items and weight
    const totalItems = order.total_item_qty || 0;
    const weight = order.weight_lb || 0;
    
    if (totalItems > 100 || weight > 500) return { priority: 'high', color: 'error' };
    if (totalItems > 50 || weight > 250) return { priority: 'medium', color: 'warning' };
    return { priority: 'low', color: 'success' };
  };

  const columns = useMemo(
    () => [
      {
        accessorKey: 'transaction_id',
        header: 'Transaction ID',
        size: 120,
      },
      {
        accessorKey: 'customer_details.company_name',
        header: 'Customer',
        size: 180,
      },
      {
        accessorKey: 'reference_number',
        header: 'Reference',
        size: 120,
      },
      {
        accessorKey: 'ship_to_name',
        header: 'Ship To Name',
        size: 150,
      },
      {
        accessorKey: 'ship_to_company',
        header: 'Ship To Company',
        size: 150,
      },
      {
        accessorKey: 'ship_to_address',
        header: 'Address',
        size: 180,
      },
      {
        accessorKey: 'ship_to_address2',
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
        accessorKey: 'ship_to_country',
        header: 'Country',
        size: 120,
      },
      {
        accessorKey: 'weight_lb',
        header: 'Weight (lb)',
        size: 120,
      },
      {
        accessorKey: 'sku_quantity',
        header: 'SKU Quantities',
        size: 200,
        Cell: ({ cell }) => {
          const skuQuantities = cell.getValue();
          if (!skuQuantities) return '';
          
          try {
            // Parse the JSON if it's a string
            const quantities = typeof skuQuantities === 'string'
              ? JSON.parse(skuQuantities)
              : skuQuantities;
              
            const formattedText = Object.entries(quantities)
              .map(([sku, qty]) => `${sku}(${qty})`)
              .join(', ');
            
            // Create a more readable format for tooltip
            const tooltipText = Object.entries(quantities)
              .map(([sku, qty]) => `${sku}: ${qty}`)
              .join('\n');
            
            return (
              <Tooltip
                title={<pre style={{ margin: 0 }}>{tooltipText}</pre>}
                arrow
                placement="top"
              >
                <Box
                  component="span"
                  sx={{
                    display: 'block',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {formattedText}
                </Box>
              </Tooltip>
            );
          } catch (error) {
            console.error('Error parsing SKU quantities:', error);
            return '';
          }
        },
      },
      {
        accessorKey: 'line_items',
        header: 'Line Items',
        size: 100,
      },
      {
        accessorKey: 'total_item_qty',
        header: 'Total Qty',
        size: 100,
      },
      {
        accessorKey: 'volume_cuft',
        header: 'Volume (ft³)',
        size: 120,
      },
      {
        accessorKey: 'packages',
        header: 'Packages',
        size: 100,
      },
      {
        accessorKey: 'notes',
        header: 'Notes',
        size: 200,
      },
      {
        accessorKey: 'carrier',
        header: 'Carrier',
        size: 120,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        size: 120,
        Cell: ({ row: { original } }) => {
          const { status, color } = getOrderStatus(original);
          return (
            <Chip
              label={status}
              color={color}
              size="small"
            />
          );
        },
      },
      {
        accessorKey: 'priority',
        header: 'Priority',
        size: 120,
        Cell: ({ row: { original } }) => {
          const { priority, color } = getOrderPriority(original);
          return (
            <Chip
              label={priority}
              color={color}
              size="small"
            />
          );
        },
      },
      {
        accessorKey: 'close_date',
        header: 'Close Date',
        size: 150,
        Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleString() : '',
      },
      {
        id: 'actions',
        header: 'Actions',
        size: 150,
        Cell: ({ row: { original } }) => (
          <Box>
            <IconButton
              onClick={() => navigate(`/orders/${original.transaction_id}/edit`)}
              color="primary"
              size="small"
              disabled={original.status === 'cancelled'}
            >
              <EditIcon />
            </IconButton>
            {original.status !== 'cancelled' && (
              <IconButton
                onClick={() => handleCancel(original.transaction_id)}
                color="warning"
                size="small"
              >
                <CancelIcon />
              </IconButton>
            )}
            {['draft', 'cancelled'].includes(original.status) && (
              <IconButton
                onClick={() => handleDelete(original.transaction_id)}
                color="error"
                size="small"
              >
                <DeleteIcon />
              </IconButton>
            )}
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
          {Object.entries(statusCounts).map(([status, count]) => (
            <Grid item key={status}>
              <Chip
                label={`${status}: ${count}`}
                color={getOrderStatus({ status }).color}
                variant="outlined"
                sx={{ minWidth: 100 }}
              />
            </Grid>
          ))}
        </Grid>

        <MaterialReactTable
          columns={columns}
          data={orders}
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
              onClick={() => navigate('/orders/new')}
            >
              New Order
            </Button>
          )}
          muiTableProps={{
            sx: {
              tableLayout: 'auto', // Changed from 'fixed' to allow column resizing
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

export default OrderList;