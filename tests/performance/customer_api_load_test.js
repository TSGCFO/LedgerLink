import { check, sleep } from 'k6';
import http from 'k6/http';
import { SharedArray } from 'k6/data';
import { Rate } from 'k6/metrics';

// Define custom metrics
const errorRate = new Rate('error_rate');

// Load test data from a JSON file (create this file with test data before running)
const customers = new SharedArray('customers', function() {
  return JSON.parse(open('./test_data/customers.json'));
});

// Define test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 }, // Ramp up to 10 users over 30 seconds
    { duration: '1m', target: 10 },  // Stay at 10 users for 1 minute
    { duration: '20s', target: 20 }, // Ramp up to 20 users over 20 seconds
    { duration: '1m', target: 20 },  // Stay at 20 users for 1 minute
    { duration: '30s', target: 0 },  // Ramp down to 0 users over 30 seconds
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should complete within 500ms
    error_rate: ['rate<0.1'],         // Error rate should be less than 10%
  },
};

// Authentication function to get JWT token
function getToken() {
  const loginUrl = 'http://localhost:8000/api/v1/auth/token/';
  const loginPayload = JSON.stringify({
    username: 'admin',
    password: 'adminpassword'
  });
  
  const loginParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const loginResponse = http.post(loginUrl, loginPayload, loginParams);
  
  check(loginResponse, {
    'Login successful': (resp) => resp.status === 200,
    'Token received': (resp) => resp.json('access') !== undefined,
  });
  
  return loginResponse.json('access');
}

// Setup function - runs once per VU
export function setup() {
  return { token: getToken() };
}

// Main function - default function called by k6
export default function(data) {
  const token = data.token;
  const baseUrl = 'http://localhost:8000/api/v1/customers/';
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
  
  // Test case 1: List customers (GET)
  const listResponse = http.get(baseUrl, params);
  check(listResponse, {
    'List customers status is 200': (r) => r.status === 200,
    'List customers returns data': (r) => r.json('results') !== undefined,
    'List customers returned at least one customer': (r) => r.json('results').length > 0,
  });
  
  errorRate.add(listResponse.status !== 200);
  sleep(1);
  
  // Test case 2: Get a single customer (GET)
  // Get a random customer from the results
  const customerList = listResponse.json('results');
  if (customerList && customerList.length > 0) {
    const randomCustomer = customerList[Math.floor(Math.random() * customerList.length)];
    const customerId = randomCustomer.id;
    
    const getResponse = http.get(`${baseUrl}${customerId}/`, params);
    check(getResponse, {
      'Get customer status is 200': (r) => r.status === 200,
      'Get customer returns correct ID': (r) => r.json('id') === customerId,
    });
    
    errorRate.add(getResponse.status !== 200);
    sleep(1);
  }
  
  // Test case 3: Create a customer (POST)
  // Select a random customer from test data
  const randomCustomerData = customers[Math.floor(Math.random() * customers.length)];
  
  // Make the customer unique by adding a timestamp
  const timestamp = new Date().getTime();
  randomCustomerData.company_name = `${randomCustomerData.company_name} ${timestamp}`;
  randomCustomerData.email = `test.${timestamp}@example.com`;
  
  const createResponse = http.post(
    baseUrl,
    JSON.stringify(randomCustomerData),
    params
  );
  
  check(createResponse, {
    'Create customer status is 201': (r) => r.status === 201,
    'Create customer returns data': (r) => r.json('id') !== undefined,
    'Create customer has correct name': (r) => r.json('company_name') === randomCustomerData.company_name,
  });
  
  errorRate.add(createResponse.status !== 201);
  const createdCustomerId = createResponse.json('id');
  sleep(1);
  
  // Test case 4: Update a customer (PUT)
  if (createdCustomerId) {
    const updateData = {
      company_name: `Updated ${randomCustomerData.company_name}`,
      contact_name: randomCustomerData.contact_name,
      email: randomCustomerData.email,
    };
    
    const updateResponse = http.put(
      `${baseUrl}${createdCustomerId}/`,
      JSON.stringify(updateData),
      params
    );
    
    check(updateResponse, {
      'Update customer status is 200': (r) => r.status === 200,
      'Update customer returns correct ID': (r) => r.json('id') === createdCustomerId,
      'Update customer has updated name': (r) => r.json('company_name') === updateData.company_name,
    });
    
    errorRate.add(updateResponse.status !== 200);
    sleep(1);
    
    // Test case 5: Delete a customer (DELETE)
    const deleteResponse = http.del(`${baseUrl}${createdCustomerId}/`, null, params);
    
    check(deleteResponse, {
      'Delete customer status is 204': (r) => r.status === 204,
    });
    
    errorRate.add(deleteResponse.status !== 204);
  }
  
  sleep(1);
}