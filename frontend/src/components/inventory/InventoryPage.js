import React, { useState } from 'react';
import { Tabs, Tab, Box, AppBar } from '@mui/material';
import SKU from './SKU';
import Inserts from './Inserts';

function InventoryPage() {
  const [value, setValue] = useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%', bgcolor: 'background.paper' }}>
      <AppBar position="static">
        <Tabs value={value} onChange={handleChange} aria-label="Inventory Tabs">
          <Tab label="SKU List" />
          <Tab label="Inserts" />
        </Tabs>
      </AppBar>
      {value === 0 && (
        <Box p={3}>
          <SKU />
        </Box>
      )}
      {value === 1 && (
        <Box p={3}>
          <Inserts />
        </Box>
      )}
    </Box>
  );
}

export default InventoryPage;
