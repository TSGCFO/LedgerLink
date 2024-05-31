import React, { useEffect, useState } from 'react';

const CustomerList = () => {
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
    <div>
      <h2>Customer Data</h2>
      <table>
        <thead>
          <tr>
            <th>Customer ID</th>
            <th>Company Name</th>
            <th>Legal Business Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th>City</th>
            <th>State</th>
            <th>Zip</th>
            <th>Country</th>
            <th>Business Type</th>
          </tr>
        </thead>
        <tbody>
          {customers.map(customer => (
            <tr key={customer.customerId}>
              <td>{customer.customerId}</td>
              <td>{customer.companyName}</td>
              <td>{customer.legalBusinessName}</td>
              <td>{customer.email}</td>
              <td>{customer.phone}</td>
              <td>{customer.address}</td>
              <td>{customer.city}</td>
              <td>{customer.state}</td>
              <td>{customer.zip}</td>
              <td>{customer.country}</td>
              <td>{customer.businessType}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomerList;
