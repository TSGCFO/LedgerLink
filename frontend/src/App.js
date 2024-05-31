import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CustomerPage from './components/customer/CustomerPage';
import PricingPage from './components/pricing/PricingPage';
import InventoryPage from './components/inventory/InventoryPage';

function App() {
  const [customers, setCustomers] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/customers')
      .then(response => response.json())
      .then(data => {
        setCustomers(data);
      })
      .catch(error => {
        console.error('Error fetching customers:', error);
      });
  }, []);

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Welcome to Our Billing Application</h1>
          <nav>
            <ul>
              <li><Link to="/customer">Customer</Link></li>
              <li><Link to="/pricing">Pricing</Link></li>
              <li><Link to="/inventory">Inventory</Link></li>
            </ul>
          </nav>
        </header>
        <Routes>
          <Route path="/customer" element={<CustomerPage customers={customers} />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
