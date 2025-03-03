# API Contract Testing with Pact

This document explains the contract testing implementation in the LedgerLink project using Pact.

## Overview

Contract testing ensures that the API communication between the frontend (consumer) and backend (provider) works as expected. Instead of testing the entire integration, contract tests verify that both sides agree on the structure and format of their communications.

### Benefits of Contract Testing

- **Decoupled Testing**: Frontend and backend teams can verify their integrations without requiring the other system to be running.
- **Early Detection**: API incompatibilities are caught before integration testing.
- **Documentation**: The contracts serve as living documentation of the API.
- **Confidence**: Changes to either side can be verified against the contracts.

## Architecture

LedgerLink uses the [Pact](https://pact.io/) framework for contract testing:

1. **Consumer (Frontend)**: Defines expectations for API interactions
2. **Provider (Backend)**: Verifies it can fulfill these expectations
3. **Pact Broker** (optional): Central storage for sharing contracts

### Project Structure

```
├── frontend/
│   └── pact/
│       ├── consumers/           # Consumer contract tests
│       │   └── customer.test.js
│       ├── jest.config.js       # Jest configuration for Pact tests
│       └── publish.js           # Script to publish pacts to a broker
└── api/
    └── tests/
        └── pact/
            └── providers/       # Provider verification tests
                └── test_customers_provider.py
```

## Running Contract Tests

### Prerequisites

- Node.js and npm for consumer tests
- Python and pytest for provider tests
- PostgreSQL database for provider tests

### Consumer Tests (Frontend)

Consumer tests define the contract by specifying expected interactions with the backend API.

```bash
# Install dependencies
npm install

# Run Pact consumer tests
npm run test:pact

# Publish contracts to Pact broker (optional)
npm run test:pact:publish
```

This will:
1. Run the consumer tests, which create mock API interactions
2. Generate Pact contract files in the `pacts/` directory
3. (If publishing) Upload the contracts to a Pact broker

### Provider Tests (Backend)

Provider tests verify that the backend can fulfill the requirements specified in the contract.

```bash
# Run provider verification tests
npm run test:pact:verify
# or directly with pytest
python -m pytest -xvs api/tests/pact/
```

This will:
1. Start a test Django server
2. Verify each interaction defined in the contract against this server
3. Report any discrepancies

## Environment Variables

For a Pact broker integration, the following environment variables can be set:

```
# For both consumer and provider
PACT_BROKER_URL=http://your-broker.example.com
PACT_BROKER_USERNAME=username
PACT_BROKER_PASSWORD=password
# or
PACT_BROKER_TOKEN=your-token

# For provider verification
PACT_PROVIDER_VERSION=1.0.0
PACT_PUBLISH_RESULTS=true
ENVIRONMENT=dev
```

## Adding New Contract Tests

### Adding a Consumer Test

1. Create a new test file in `frontend/pact/consumers/` for the API resource
2. Define the expected request/response for each interaction
3. Create mock API interactions using Pact
4. Verify your client code works with these mocks

Example:

```javascript
// Example of adding a new interaction
await provider.addInteraction({
  state: 'resource exists',
  uponReceiving: 'a request for the resource',
  withRequest: {
    method: 'GET',
    path: '/api/resource/',
  },
  willRespondWith: {
    status: 200,
    body: {...},
  },
});
```

### Adding a Provider Test

1. Add a provider state setup function in `api/tests/pact/providers/test_customers_provider.py`
2. Register the provider state in the `PROVIDER_STATES` dictionary

Example:

```python
def setup_resource_exists(variables, **kwargs):
    """Setup provider state for 'resource exists'."""
    # Create test data
    ResourceFactory.create()
    
# Then add to PROVIDER_STATES
PROVIDER_STATES = {
    # ...
    'resource exists': setup_resource_exists,
}
```

## Versioning and Compatibility

### Contract Versioning

Pact contracts should be versioned along with your application. The recommended approach is:

1. Tag contracts with environment names (e.g., 'dev', 'staging', 'production')
2. Version provider implementations with git commits or semantic versions
3. Use these when publishing verification results

### Breaking Changes

When making breaking API changes:

1. Create a new version of the API endpoint
2. Keep the old endpoint working until all consumers have migrated
3. Create new contracts for the new endpoint
4. Mark old contracts as deprecated

## Best Practices

1. **Focus on structure, not data**: Use matchers like `like()` and `term()` to define structure without tying to specific values
2. **Keep provider states simple**: Create minimal test data needed for verification
3. **Regular verification**: Run provider verification in CI/CD to catch regressions
4. **Document provider states**: Make sure the states are clearly documented for both teams
5. **Use semantic versioning**: For your API contracts to indicate compatibility

## Troubleshooting

### Common Issues

- **Connection refused**: Make sure the provider server is running during verification
- **Contract not found**: Check that consumer tests have been run and have generated pact files
- **Provider state not found**: Ensure all provider states mentioned in consumer tests are implemented
- **Verification failure**: Compare the expected vs. actual responses carefully for formatting differences

### Debugging Tips

- Enable verbose output for Pact: `PACT_LOGLEVEL=debug npm run test:pact`
- Check generated pact files in the `pacts/` directory
- Use your browser's network inspector to compare actual API responses with the contract