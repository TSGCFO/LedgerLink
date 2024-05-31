import React, { useState } from 'react';
import CustomerModal from './CustomerModal';
import CustomerList from './CustomerList';

function CustomerPage() {
  const [isModalOpen, setModalOpen] = useState(false);

  const handleOpen = () => setModalOpen(true);
  const handleClose = () => setModalOpen(false);

  return (
    <div>
      <h2>Customer Management</h2>
      <button onClick={handleOpen}>Create Customer</button>
      <CustomerModal open={isModalOpen} handleClose={handleClose} />
      <CustomerList />
    </div>
  );
}

export default CustomerPage;
