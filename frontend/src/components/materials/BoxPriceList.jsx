import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MaterialReactTable } from 'material-react-table';
import { Box, Button, Typography } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';

const BoxPriceList = () => {
  const navigate = useNavigate();
  const [boxPrices, setBoxPrices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const columns = [
    {
      accessorKey: 'box_type',
      header: 'Box Type',
    },
    {
      accessorKey: 'price',
      header: 'Price',
      Cell: ({ cell }) => {
        const value = cell.getValue();
        return value != null ? `$${Number(value).toFixed(2)}` : '';
      },
    },
    {
      accessorKey: 'length',
      header: 'Length',
      Cell: ({ cell }) => {
        const value = cell.getValue();
        return value != null ? `${Number(value).toFixed(2)} cm` : '';
      },
    },
    {
      accessorKey: 'width',
      header: 'Width',
      Cell: ({ cell }) => {
        const value = cell.getValue();
        return value != null ? `${Number(value).toFixed(2)} cm` : '';
      },
    },
    {
      accessorKey: 'height',
      header: 'Height',
      Cell: ({ cell }) => {
        const value = cell.getValue();
        return value != null ? `${Number(value).toFixed(2)} cm` : '';
      },
    },
  ];

  useEffect(() => {
    const fetchBoxPrices = async () => {
      try {
        const response = await axios.get('/api/box-prices/');
        setBoxPrices(response.data);
      } catch (error) {
        console.error('Error fetching box prices:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBoxPrices();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Box Prices
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate('/box-prices/new')}
        >
          Add Box Price
        </Button>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={boxPrices}
        state={{ isLoading }}
        enableColumnFilters
        enableColumnOrdering
        enableSorting
        enablePagination
        manualPagination={false}
        enableRowSelection={false}
        enableColumnResizing
        columnResizeMode="onChange"
        muiTableProps={{
          sx: {
            tableLayout: 'auto',
          },
        }}
        initialState={{
          density: 'compact',
          pagination: { pageSize: 20 },
          sorting: [{ id: 'box_type', desc: false }],
        }}
      />
    </Box>
  );
};

export default BoxPriceList;