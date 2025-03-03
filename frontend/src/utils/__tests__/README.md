# API Contract Testing in LedgerLink

This directory contains consumer-side contract tests for LedgerLink APIs using Pact. These tests ensure the API contracts between the frontend (consumer) and backend (provider) remain consistent.

## What is Contract Testing?

Contract testing is a methodology where contracts between service consumers and providers are tested independently to ensure they maintain compatibility. It's particularly valuable in microservices or frontend/backend architectures.

## Contract Tests in LedgerLink

We have implemented contract tests for the following APIs:

- **[billing.pact.test.js](./billing.pact.test.js)**: Tests for the Billing API
- **[customers.pact.test.js](./customers.pact.test.js)**: Tests for the Customers API
- **[orders.pact.test.js](./orders.pact.test.js)**: Tests for the Orders API
- **[products.pact.test.js](./products.pact.test.js)**: Tests for the Products API
- **[rules.pact.test.js](./rules.pact.test.js)**: Tests for the Rules API

## How the Pact Tests Work

1. **Define Expectations**: Tests define what the frontend expects from the backend
2. **Generate Contracts**: Running tests creates Pact files (JSON contracts)
3. **Verify Provider**: Backend tests verify these contracts are satisfied
4. **CI Integration**: Both sides verified in CI/CD pipeline

## Running the Tests

```bash
# Run all Pact tests
npm run test:pact

# Run specific Pact test
npm test -- src/utils/__tests__/products.pact.test.js
```

## Common Patterns

Our contract tests follow consistent patterns:

1. **Setup**: Configure the Pact mock provider
2. **Define interactions**: Specify API requests and expected responses
3. **Verify**: Make actual API calls and verify they match expectations

Example:
```javascript
describe('GET /api/v1/products/', () => {
  beforeEach(() => {
    // Define the expected interaction
    return provider.addInteraction({
      state: 'products exist',
      uponReceiving: 'a request for all products',
      withRequest: {
        method: 'GET',
        path: '/api/v1/products/',
        headers: { /* headers */ }
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: { /* expected response */ }
      }
    });
  });
  
  test('can retrieve a list of products', async () => {
    // Make the actual API call
    const response = await apiClient.get('/api/v1/products/');
    
    // Verify response meets expectations
    expect(response.status).toEqual(200);
    expect(response.data.results).toBeDefined();
    
    // Verify against the contract
    return provider.verify();
  });
});
```

## Best Practices

1. **Focus on Structure, Not Data**: Test for field existence and types, not specific values
2. **Use Matchers**: Use Pact matchers to be flexible about exact values
3. **Keep Provider States Simple**: Provider states should be clear and focused
4. **Test Common Scenarios**: Cover main success and error paths
5. **Update Contracts First**: When changing an API, update the contract test first

## Adding a New Contract Test

To create a new contract test:

1. Create a new file: `<entity>.pact.test.js`
2. Import the Pact library and provider from pact-utils
3. Define test scenarios using the describe/test pattern
4. Test both success and error cases
5. Run the tests to generate the contract

## Troubleshooting

If tests are failing:

1. **Check API Changes**: Has the API changed without updating tests?
2. **Verify Matchers**: Are Pact matchers set up correctly?
3. **Check Provider States**: Are provider states implemented correctly?
4. **Run in Debug Mode**: Set `process.env.PACT_DEBUG=true` for detailed logs

## Further Resources

- [Pact Documentation](https://docs.pact.io/)
- [Consumer-Driven Contracts with Pact](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Pact JavaScript Documentation](https://github.com/pact-foundation/pact-js)