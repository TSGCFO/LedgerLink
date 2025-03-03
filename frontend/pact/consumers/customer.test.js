const { Pact } = require('@pact-foundation/pact');
const { Matchers } = require('@pact-foundation/pact');
const { like, term, eachLike } = Matchers;
const path = require('path');
const axios = require('axios');

const customerApiClient = {
  getCustomers: async (baseUrl) => {
    const response = await axios.get(`${baseUrl}/api/customers/`);
    return response.data;
  },
  
  getCustomer: async (baseUrl, id) => {
    const response = await axios.get(`${baseUrl}/api/customers/${id}/`);
    return response.data;
  },
  
  createCustomer: async (baseUrl, customerData) => {
    const response = await axios.post(`${baseUrl}/api/customers/`, customerData);
    return response.data;
  },
  
  updateCustomer: async (baseUrl, id, customerData) => {
    const response = await axios.put(`${baseUrl}/api/customers/${id}/`, customerData);
    return response.data;
  },
  
  deleteCustomer: async (baseUrl, id) => {
    await axios.delete(`${baseUrl}/api/customers/${id}/`);
    return true;
  }
};

// Define the Pact setup
describe('Customer API Contract Tests', () => {
  const provider = new Pact({
    consumer: 'LedgerLinkFrontend',
    provider: 'LedgerLinkBackend',
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    logLevel: 'warn',
    dir: path.resolve(process.cwd(), 'pacts'),
    cors: true,
  });

  // Set up the provider
  beforeAll(() => provider.setup());
  
  // Clean up after tests
  afterAll(() => provider.finalize());
  
  // Verify interactions after each test
  afterEach(() => provider.verify());

  describe('Get Customers API', () => {
    const customerListMatcher = {
      count: like(1),
      next: null,
      previous: null,
      results: eachLike({
        id: like(1),
        company_name: like('Test Company'),
        contact_name: like('John Doe'),
        contact_email: term({
          matcher: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          generate: 'john@example.com'
        }),
        contact_phone: term({
          matcher: '^[0-9\\-\\+\\s\\(\\)]+$',
          generate: '123-456-7890'
        }),
        address: like('123 Test St'),
        city: like('Test City'),
        state: like('TS'),
        postal_code: like('12345'),
        country: like('Test Country'),
        created_at: term({
          matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
          generate: '2025-03-03T12:00:00Z'
        }),
        updated_at: term({
          matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
          generate: '2025-03-03T12:00:00Z'
        })
      })
    };

    it('returns a list of customers', async () => {
      // Set up the expected interaction
      await provider.addInteraction({
        state: 'there are customers',
        uponReceiving: 'a request for all customers',
        withRequest: {
          method: 'GET',
          path: '/api/customers/',
          headers: {
            Accept: 'application/json',
          },
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
          body: customerListMatcher,
        },
      });

      // Test the customer API client against the mock provider
      const response = await customerApiClient.getCustomers(provider.mockService.baseUrl);
      
      // Validate the response contains what we expect
      expect(response).toHaveProperty('results');
      expect(response.results).toBeInstanceOf(Array);
    });
  });

  describe('Get Single Customer API', () => {
    const customerMatcher = {
      id: like(1),
      company_name: like('Test Company'),
      contact_name: like('John Doe'),
      contact_email: term({
        matcher: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
        generate: 'john@example.com'
      }),
      contact_phone: like('123-456-7890'),
      address: like('123 Test St'),
      city: like('Test City'),
      state: like('TS'),
      postal_code: like('12345'),
      country: like('Test Country'),
      created_at: term({
        matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
        generate: '2025-03-03T12:00:00Z'
      }),
      updated_at: term({
        matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
        generate: '2025-03-03T12:00:00Z'
      })
    };

    it('returns a single customer by id', async () => {
      const customerId = 1;
      
      // Set up the expected interaction
      await provider.addInteraction({
        state: `customer with id ${customerId} exists`,
        uponReceiving: `a request for customer with id ${customerId}`,
        withRequest: {
          method: 'GET',
          path: `/api/customers/${customerId}/`,
          headers: {
            Accept: 'application/json',
          },
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
          body: customerMatcher,
        },
      });

      // Test the customer API client against the mock provider
      const response = await customerApiClient.getCustomer(provider.mockService.baseUrl, customerId);
      
      // Validate the response contains what we expect
      expect(response).toHaveProperty('id');
      expect(response).toHaveProperty('company_name');
      expect(response).toHaveProperty('contact_email');
    });
  });

  describe('Create Customer API', () => {
    const newCustomer = {
      company_name: 'New Company',
      contact_name: 'Jane Smith',
      contact_email: 'jane@example.com',
      contact_phone: '987-654-3210',
      address: '456 New St',
      city: 'New City',
      state: 'NS',
      postal_code: '54321',
      country: 'New Country'
    };

    const createdCustomerMatcher = {
      id: like(2),
      company_name: like(newCustomer.company_name),
      contact_name: like(newCustomer.contact_name),
      contact_email: like(newCustomer.contact_email),
      contact_phone: like(newCustomer.contact_phone),
      address: like(newCustomer.address),
      city: like(newCustomer.city),
      state: like(newCustomer.state),
      postal_code: like(newCustomer.postal_code),
      country: like(newCustomer.country),
      created_at: term({
        matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
        generate: '2025-03-03T12:00:00Z'
      }),
      updated_at: term({
        matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
        generate: '2025-03-03T12:00:00Z'
      })
    };

    it('creates a new customer', async () => {
      // Set up the expected interaction
      await provider.addInteraction({
        state: 'can create a new customer',
        uponReceiving: 'a request to create a customer',
        withRequest: {
          method: 'POST',
          path: '/api/customers/',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: newCustomer,
        },
        willRespondWith: {
          status: 201,
          headers: {
            'Content-Type': 'application/json',
          },
          body: createdCustomerMatcher,
        },
      });

      // Test the customer API client against the mock provider
      const response = await customerApiClient.createCustomer(provider.mockService.baseUrl, newCustomer);
      
      // Validate the response contains what we expect
      expect(response).toHaveProperty('id');
      expect(response.company_name).toEqual(newCustomer.company_name);
      expect(response.contact_email).toEqual(newCustomer.contact_email);
    });
  });

  describe('Update Customer API', () => {
    const customerId = 1;
    const updatedCustomer = {
      company_name: 'Updated Company',
      contact_name: 'John Updated',
      contact_email: 'updated@example.com',
      contact_phone: '555-555-5555',
      address: '789 Update St',
      city: 'Update City',
      state: 'UP',
      postal_code: '99999',
      country: 'Updated Country'
    };

    const updatedCustomerMatcher = {
      id: like(customerId),
      company_name: like(updatedCustomer.company_name),
      contact_name: like(updatedCustomer.contact_name),
      contact_email: like(updatedCustomer.contact_email),
      contact_phone: like(updatedCustomer.contact_phone),
      address: like(updatedCustomer.address),
      city: like(updatedCustomer.city),
      state: like(updatedCustomer.state),
      postal_code: like(updatedCustomer.postal_code),
      country: like(updatedCustomer.country),
      created_at: term({
        matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
        generate: '2025-03-03T12:00:00Z'
      }),
      updated_at: term({
        matcher: '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$',
        generate: '2025-03-03T12:30:00Z'
      })
    };

    it('updates an existing customer', async () => {
      // Set up the expected interaction
      await provider.addInteraction({
        state: `customer with id ${customerId} exists`,
        uponReceiving: `a request to update customer with id ${customerId}`,
        withRequest: {
          method: 'PUT',
          path: `/api/customers/${customerId}/`,
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: updatedCustomer,
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
          body: updatedCustomerMatcher,
        },
      });

      // Test the customer API client against the mock provider
      const response = await customerApiClient.updateCustomer(
        provider.mockService.baseUrl, 
        customerId, 
        updatedCustomer
      );
      
      // Validate the response contains what we expect
      expect(response.id).toEqual(customerId);
      expect(response.company_name).toEqual(updatedCustomer.company_name);
      expect(response.contact_email).toEqual(updatedCustomer.contact_email);
    });
  });

  describe('Delete Customer API', () => {
    const customerId = 1;

    it('deletes an existing customer', async () => {
      // Set up the expected interaction
      await provider.addInteraction({
        state: `customer with id ${customerId} exists`,
        uponReceiving: `a request to delete customer with id ${customerId}`,
        withRequest: {
          method: 'DELETE',
          path: `/api/customers/${customerId}/`,
        },
        willRespondWith: {
          status: 204,
        },
      });

      // Test the customer API client against the mock provider
      const result = await customerApiClient.deleteCustomer(provider.mockService.baseUrl, customerId);
      
      // Validate the response is as expected
      expect(result).toBe(true);
    });
  });
});