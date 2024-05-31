import React, { useState, useCallback } from 'react';
import CreatePricingForm from './CreatePricingForm';
import axios from 'axios';

const PricingPage = () => {
  const [isFormOpen, setFormOpen] = useState(false);

  const handleOpenForm = useCallback(() => setFormOpen(true), []);
  const handleCloseForm = useCallback(() => setFormOpen(false), []);

  const fetchPricingOptions = async (customerId) => {
    try {
      const response = await axios.get(`/api/pricing-options?customerId=${customerId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching pricing options:', error);
      return [];
    }
  };

  return (
    <div>
      <h1>Pricing Management</h1>
      <p>Welcome to the Pricing Management page. Here you can manage all pricing related tasks.</p>
      <button onClick={handleOpenForm}>Create New Pricing</button>
      {isFormOpen && (
        <CreatePricingForm handleClose={handleCloseForm} fetchPricingOptions={fetchPricingOptions} />
      )}
    </div>
  );
}

export default PricingPage;
