import http from 'k6/http';
import { sleep, check } from 'k6';
import { Counter } from 'k6/metrics';

// Define metrics
const errors = new Counter('errors');
const apiCalls = new Counter('api_calls');

// Test configuration
export const options = {
  stages: [
    { duration: '20s', target: 10 },   // Ramp up to 10 users over 20 seconds
    { duration: '1m', target: 20 },    // Ramp up to 20 users over 1 minute
    { duration: '30s', target: 50 },   // Ramp up to 50 users over 30 seconds
    { duration: '1m', target: 50 },    // Stay at 50 users for 1 minute
    { duration: '30s', target: 0 },    // Ramp down to 0 users over 30 seconds
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    'http_req_duration{name:get-orders}': ['p(95)<400'], // 95% of GET orders should be below 400ms
    'http_req_duration{name:get-order-detail}': ['p(95)<300'], // 95% of GET order detail should be below 300ms
    'http_req_duration{name:create-order}': ['p(95)<800'], // 95% of POST orders should be below 800ms
    errors: ['count<10'] // Error count should be less than 10
  }
};

// Login function to get token
function login() {
  const loginUrl = 'http://localhost:8000/api/v1/auth/token/';
  const payload = JSON.stringify({
    username: 'admin',
    password: 'adminpassword'
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  const loginRes = http.post(loginUrl, payload, params);
  
  if (loginRes.status !== 200) {
    errors.add(1);
    console.log(`Login failed: ${loginRes.status} ${loginRes.body}`);
    return null;
  }
  
  return JSON.parse(loginRes.body).access;
}

// Main test function
export default function() {
  // Login to get token
  const token = login();
  
  if (!token) {
    console.log('Login failed, skipping requests');
    sleep(1);
    return;
  }
  
  // Set headers for authenticated requests
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  };
  
  // Test 1: Get all orders
  const ordersRes = http.get('http://localhost:8000/api/v1/orders/', params, {
    tags: { name: 'get-orders' }
  });
  apiCalls.add(1);
  
  check(ordersRes, {
    'orders status is 200': (r) => r.status === 200,
    'orders response has data': (r) => JSON.parse(r.body).results.length > 0
  });
  
  // Extract first order ID for detail test
  let orderId = 1;
  try {
    const ordersBody = JSON.parse(ordersRes.body);
    if (ordersBody.results && ordersBody.results.length > 0) {
      orderId = ordersBody.results[0].id;
    }
  } catch (e) {
    console.log(`Error parsing orders response: ${e.message}`);
  }
  
  // Test 2: Get order detail
  const orderDetailRes = http.get(`http://localhost:8000/api/v1/orders/${orderId}/`, params, {
    tags: { name: 'get-order-detail' }
  });
  apiCalls.add(1);
  
  check(orderDetailRes, {
    'order detail status is 200': (r) => r.status === 200,
    'order detail has correct ID': (r) => JSON.parse(r.body).id === orderId
  });
  
  // Test 3: Create a new order
  const newOrder = {
    customer: 1,
    order_number: `TEST-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    shipping_address: '123 Performance Test Street',
    shipping_method: 'Standard',
    status: 'pending',
    priority: 'normal',
    notes: 'Created during performance testing'
  };
  
  const createOrderRes = http.post(
    'http://localhost:8000/api/v1/orders/',
    JSON.stringify(newOrder),
    params,
    {
      tags: { name: 'create-order' }
    }
  );
  apiCalls.add(1);
  
  check(createOrderRes, {
    'create order status is 201': (r) => r.status === 201,
    'created order has ID': (r) => JSON.parse(r.body).id !== undefined
  });
  
  if (createOrderRes.status !== 201) {
    errors.add(1);
    console.log(`Create order failed: ${createOrderRes.status} ${createOrderRes.body}`);
  }
  
  // Short sleep between iterations
  sleep(1);
}