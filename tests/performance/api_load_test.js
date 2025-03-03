import http from 'k6/http';
import { sleep, check } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { SharedArray } from 'k6/data';

// Custom metrics
const errorRate = new Rate('error_rate');
const apiCallsPerSecond = new Counter('api_calls_per_second');
const responseTime = new Trend('response_time');

// Load test data
const testData = new SharedArray('test data', function() {
  // Load test data - this runs only once
  return JSON.parse(open('./test_data/customers.json'));
});

// Test configuration
export const options = {
  scenarios: {
    // Common API endpoints stress test
    api_stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },  // Ramp up
        { duration: '1m', target: 50 },   // Mid load
        { duration: '30s', target: 100 }, // High load
        { duration: '1m', target: 50 },   // Scale down
        { duration: '30s', target: 0 },   // Ramp down
      ],
      gracefulRampDown: '0s',
    },
    // Critical endpoints spike test
    billing_spike: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 20,
      maxVUs: 100,
      startTime: '3m30s', // Start after the API stress test
    },
  },
  thresholds: {
    // Response time thresholds
    'response_time': ['p(90) < 500', 'p(95) < 800', 'p(99) < 2000'],
    // Error rate thresholds
    'error_rate': ['rate < 0.1'], // Error rate less than 10%
    // Requests per second thresholds
    'http_req_duration{method:GET}': ['p(95) < 500'],
    'http_req_duration{method:POST}': ['p(95) < 1000'],
  },
};

// Helper function to get a random customer ID from test data
function getRandomCustomerId() {
  const idx = Math.floor(Math.random() * testData.length);
  return testData[idx].id;
}

// Helper function to get auth token
function getAuthToken() {
  const loginRes = http.post(`${__ENV.API_BASE_URL || 'http://localhost:8000'}/api/v1/auth/login/`, {
    username: __ENV.TEST_USERNAME || 'testuser',
    password: __ENV.TEST_PASSWORD || 'password123',
  });
  
  if (loginRes.status === 200) {
    const body = JSON.parse(loginRes.body);
    return body.token;
  } else {
    console.error('Failed to login:', loginRes.status, loginRes.body);
    return null;
  }
}

// Initialize test state
function setup() {
  const token = getAuthToken();
  return { token };
}

export default function(data) {
  const baseUrl = __ENV.API_BASE_URL || 'http://localhost:8000';
  const token = data.token;
  
  if (!token) {
    console.error('No authentication token available, skipping test');
    return;
  }
  
  // Common headers for authenticated requests
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  };
  
  // Test group for customer endpoints (high-traffic)
  {
    const customerId = getRandomCustomerId();
    
    // Customer list endpoint
    let response = http.get(`${baseUrl}/api/v1/customers/`, { headers });
    let success = check(response, {
      'customers-list-status-200': (r) => r.status === 200,
      'customers-list-data-valid': (r) => JSON.parse(r.body).length > 0,
    });
    errorRate.add(!success);
    apiCallsPerSecond.add(1);
    responseTime.add(response.timings.duration);
    
    // Customer detail endpoint
    if (customerId) {
      response = http.get(`${baseUrl}/api/v1/customers/${customerId}/`, { headers });
      success = check(response, {
        'customer-detail-status-200': (r) => r.status === 200,
        'customer-detail-data-valid': (r) => JSON.parse(r.body).id === customerId,
      });
      errorRate.add(!success);
      apiCallsPerSecond.add(1);
      responseTime.add(response.timings.duration);
    }
    
    sleep(1);
  }
  
  // Test group for orders endpoints (high-traffic)
  {
    // Orders list endpoint
    let response = http.get(`${baseUrl}/api/v1/orders/`, { headers });
    let success = check(response, {
      'orders-list-status-200': (r) => r.status === 200,
    });
    errorRate.add(!success);
    apiCallsPerSecond.add(1);
    responseTime.add(response.timings.duration);
    
    sleep(1);
  }
  
  // Test group for products endpoints (medium-traffic)
  {
    // Products list endpoint
    let response = http.get(`${baseUrl}/api/v1/products/`, { headers });
    let success = check(response, {
      'products-list-status-200': (r) => r.status === 200,
    });
    errorRate.add(!success);
    apiCallsPerSecond.add(1);
    responseTime.add(response.timings.duration);
    
    sleep(1);
  }
  
  // Test for billing endpoints (critical)
  if (__ITER % 10 === 0) { // Only run this for every 10th iteration to reduce load
    // Generate a billing report (expensive operation)
    const customerId = getRandomCustomerId();
    if (customerId) {
      const payload = JSON.stringify({
        customer: customerId,
        date_range: {
          start_date: '2025-01-01',
          end_date: '2025-03-01'
        },
        include_details: true
      });
      
      const response = http.post(`${baseUrl}/api/v1/billing/generate-report/`, payload, { headers });
      const success = check(response, {
        'billing-report-status-200': (r) => r.status === 200 || r.status === 202, 
        'billing-report-response-valid': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.success === true;
          } catch (e) {
            return false;
          }
        },
      });
      errorRate.add(!success);
      apiCallsPerSecond.add(1);
      responseTime.add(response.timings.duration);
    }
    
    sleep(2); // Longer sleep after heavy operation
  }
  
  // Test for rule evaluations (critical)
  if (__ITER % 5 === 0) { // Run for every 5th iteration
    const testOrder = {
      transaction_id: 12345,
      customer: getRandomCustomerId(),
      sku_quantity: { 'TEST-SKU-001': 10, 'TEST-SKU-002': 5 },
      ship_to_country: 'US',
      weight_lb: 15.5,
      packages: 2
    };
    
    const payload = JSON.stringify({
      order: testOrder,
      evaluate_all: true
    });
    
    const response = http.post(`${baseUrl}/api/v1/rules/evaluate-order/`, payload, { headers });
    const success = check(response, {
      'rule-evaluation-status-200': (r) => r.status === 200,
      'rule-evaluation-response-valid': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.results !== undefined;
        } catch (e) {
          return false;
        }
      },
    });
    errorRate.add(!success);
    apiCallsPerSecond.add(1);
    responseTime.add(response.timings.duration);
    
    sleep(1);
  }
}

// Clean up test resources
export function teardown(data) {
  // Nothing to clean up
}