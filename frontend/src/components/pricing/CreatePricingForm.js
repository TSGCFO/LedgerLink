import React, { useState, useEffect, Fragment } from 'react';
import { Button, TextField, Box, Dialog, DialogTitle, List, ListItem } from '@mui/material';
import axios from 'axios';

const CreatePricingForm = ({ customerId, handleClose }) => {
  const [pricingData, setPricingData] = useState({
    customer: customerId,
    generalPricing: {},
    additionalOptions: []
  });
  const [openPopup, setOpenPopup] = useState(false);
  const [options, setOptions] = useState([]);

  useEffect(() => {
    if (customerId) {
      axios.get(`http://localhost:5000/api/pricing-options?customerId=${customerId}`)
        .then(response => {
          setOptions(response.data);
        })
        .catch(error => {
          console.error('Error fetching pricing options:', error);
        });
    }
  }, [customerId]);

  const handleAddOption = (option) => {
    if (!pricingData.additionalOptions.some(o => o.key === option.key)) {
      setPricingData({
        ...pricingData,
        additionalOptions: [...pricingData.additionalOptions, { ...option, value: '' }]
      });
    }
    setOpenPopup(false);
  };

  const handleOptionValueChange = (key, value) => {
    const newOptions = pricingData.additionalOptions.map(o => o.key === key ? { ...o, value } : o);
    setPricingData({ ...pricingData, additionalOptions: newOptions });
  };

  const handleRemoveOption = (key) => {
    const newOptions = pricingData.additionalOptions.filter(o => o.key !== key);
    setPricingData({ ...pricingData, additionalOptions: newOptions });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    axios.post('http://localhost:5000/api/pricing', {
      customerId: pricingData.customer,
      pricingDetails: {
        generalPricing: pricingData.generalPricing,
        additionalOptions: pricingData.additionalOptions
      }
    })
    .then(response => {
      console.log(response.data);
      handleClose();
    })
    .catch(error => {
      console.error('There was an error!', error);
    });
  };

  const handleReset = () => {
    setPricingData({ customer: customerId, generalPricing: {}, additionalOptions: [] });
  };

  return (
    <Box component="form" noValidate autoComplete="off" onSubmit={handleSubmit}>
      <h2>Create Pricing for Customer {customerId}</h2>
      <Button onClick={() => setOpenPopup(true)}>Add More Pricing Options</Button>
      {pricingData.additionalOptions.map((option) => (
        <Fragment key={option.key}>
          <TextField
            fullWidth
            margin="normal"
            label={option.label}
            value={option.value}
            onChange={(e) => handleOptionValueChange(option.key, e.target.value)}
            name={option.key}
          />
          <Button onClick={() => handleRemoveOption(option.key)}>Remove</Button>
        </Fragment>
      ))}
      <Dialog open={openPopup} onClose={() => setOpenPopup(false)}>
        <DialogTitle>Select Pricing Options</DialogTitle>
        <List>
          {options.map(option => (
            <ListItem key={option.key} button onClick={() => handleAddOption(option)}>
              {option.label}
            </ListItem>
          ))}
        </List>
      </Dialog>
      <Button type="submit">Save</Button>
      <Button onClick={handleReset}>Save and New</Button>
      <Button onClick={handleClose}>Cancel</Button>
    </Box>
  );
}

export default CreatePricingForm;
