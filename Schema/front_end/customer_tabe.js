// Example using Fetch API to send customer data to Flask backend
const customerData = {
    company_name: "Example Corp",
    legal_business_name: "Example Corporation",
    email: "info@example.com",
    phone: "123-456-7890",
    address: "123 Main St",
    city: "Anytown",
    state: "Anystate",
    zip: "12345",
    country: "USA",
    business_type: "Retail"
  };
  
  fetch('/api/customers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(customerData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Customer added:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
  