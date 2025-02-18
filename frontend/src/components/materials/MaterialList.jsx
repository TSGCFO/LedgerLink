import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MaterialReactTable } from 'material-react-table';
import { Box, Button, Typography } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';

const MaterialList = () => {
  const navigate = useNavigate();
  const [materials, setMaterials] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const columns = [
    {
      accessorKey: 'name',
      header: 'Name',
    },
    {
      accessorKey: 'description',
      header: 'Description',
    },
    {
      accessorKey: 'unit_price',
      header: 'Unit Price',
      Cell: ({ cell }) => {
        const value = cell.getValue();
        return value != null ? `$${Number(value).toFixed(2)}` : '';
      },
    },
  ];

  useEffect(() => {
    const fetchMaterials = async () => {
      try {
        const response = await axios.get('/api/materials/');
        setMaterials(response.data);
      } catch (error) {
        console.error('Error fetching materials:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMaterials();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Materials
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate('/materials/new')}
        >
          Add Material
        </Button>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={materials}
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
        }}
      />
    </Box>
  );
};

export default MaterialList;