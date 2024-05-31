import React, { useState } from 'react';
import { Button, TextField, FormControl, InputLabel, Select, MenuItem, Box, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';

function SKU() {
  const [customer, setCustomer] = useState('');
  const [skuData, setSkuData] = useState({
    skuCode: '',
    labelingUnitType1: '',
    labelingUnitQty1: '',
    labelingUnitType2: '',
    labelingUnitQty2: '',
    labelingUnitType3: '',
    labelingUnitQty3: ''
  });
  const [openUploadModal, setOpenUploadModal] = useState(false);

  const handleInputChange = (event) => {
    setSkuData({ ...skuData, [event.target.name]: event.target.value });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(skuData);
    // API call to save SKU data
  };

  const handleOpenUploadModal = () => {
    setOpenUploadModal(true);
  };

  const handleCloseUploadModal = () => {
    setOpenUploadModal(false);
  };

  return (
    <Box component="form" noValidate autoComplete="off" onSubmit={handleSubmit}>
      <FormControl fullWidth>
        <InputLabel id="customer-select-label">Customer</InputLabel>
        <Select
          labelId="customer-select-label"
          value={customer}
          onChange={(e) => setCustomer(e.target.value)}
          name="customer"
        >
          {/* Dynamic customer list */}
          <MenuItem value={10}>Customer 1</MenuItem>
          <MenuItem value={20}>Customer 2</MenuItem>
        </Select>
      </FormControl>
      <TextField fullWidth label="SKU Code" required name="skuCode" onChange={handleInputChange} />
      <TextField fullWidth label="Labeling Unit Type 1" required name="labelingUnitType1" onChange={handleInputChange} />
      <TextField fullWidth label="Labeling Unit Qty 1" type="number" required name="labelingUnitQty1" onChange={handleInputChange} />
      <TextField fullWidth label="Labeling Unit Type 2" name="labelingUnitType2" onChange={handleInputChange} />
      <TextField fullWidth label="Labeling Unit Qty 2" type="number" name="labelingUnitQty2" onChange={handleInputChange} />
      <TextField fullWidth label="Labeling Unit Type 3" name="labelingUnitType3" onChange={handleInputChange} />
      <TextField fullWidth label="Labeling Unit Qty 3" type="number" name="labelingUnitQty3" onChange={handleInputChange} />
      <Button onClick={handleOpenUploadModal}>Upload SKU</Button>
      <Dialog open={openUploadModal} onClose={handleCloseUploadModal}>
        <DialogTitle>Upload SKU List</DialogTitle>
        <DialogContent>
          <FormControl fullWidth>
            <InputLabel id="upload-customer-select-label">Select Customer</InputLabel>
            <Select
              labelId="upload-customer-select-label"
              value={customer}
              onChange={(e) => setCustomer(e.target.value)}
              name="customer"
            >
              <MenuItem value={10}>Customer 1</MenuItem>
              <MenuItem value={20}>Customer 2</MenuItem>
            </Select>
          </FormControl>
          <TextField
            type="file"
            onChange={(e) => console.log(e.target.files[0])} // Handle file change
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadModal}>Cancel</Button>
          <Button onClick={() => console.log('Upload logic here')}>Upload</Button>
        </DialogActions>
      </Dialog>
      <Button type="submit">Save SKU</Button>
    </Box>
  );
}

export default SKU;
