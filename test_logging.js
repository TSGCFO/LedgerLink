/**
 * Test script for LedgerLink logging system
 * Generates various log events to test logging functionality
 */

// Import the logger if running in Node.js
// In a browser environment, this script would be loaded after the logger
const isBrowser = typeof window !== 'undefined';
console.log(`Running in ${isBrowser ? 'browser' : 'Node.js'} environment`);

// Simulate different log levels
console.log('Simple log message');
console.debug('Debug message with details');
console.info('Informational message about system state');
console.warn('Warning about potential issue');
console.error('Critical error occurred');

// Log messages with structured data
console.log('User data', { id: 123, name: 'Test User', role: 'Admin' });
console.info('System metrics', { 
  cpu: '45%', 
  memory: '1.2GB', 
  diskSpace: '128GB',
  connections: 42
});

// Test error handling
try {
  // Generate an error
  const nonExistentFunction = undefined;
  nonExistentFunction();
} catch (error) {
  console.error('Caught an error', {
    message: error.message,
    stack: error.stack,
    code: 'TEST_ERROR_001'
  });
}

// Simulate API interactions
console.log('API Request', {
  method: 'POST',
  url: '/api/v1/orders/',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ***'
  },
  body: {
    customer_id: 42,
    products: [
      { id: 101, quantity: 5 },
      { id: 102, quantity: 10 }
    ],
    shipping_address: {
      street: '123 Test St',
      city: 'Testville',
      state: 'TS',
      zip: '12345'
    }
  }
});

console.log('API Response', {
  status: 201,
  statusText: 'Created',
  data: {
    id: 1234,
    status: 'pending',
    total: 149.99
  }
});

// Test sensitive data handling
console.log('Configuration loaded', {
  apiEndpoint: 'https://api.example.com',
  apiKey: 'sensitive-key-should-be-masked',
  debug: true
});

// Generate a series of related logs
for (let i = 1; i <= 5; i++) {
  console.log(`Processing batch ${i} of 5`);
  if (i === 3) {
    console.warn('Batch processing partially failed, retrying...');
  }
}

// Simulate an uncaught exception in async code (in browser)
if (isBrowser) {
  setTimeout(() => {
    throw new Error('Uncaught asynchronous error');
  }, 100);
}

console.log('Logging test complete');