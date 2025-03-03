# Continuous Integration Guide for LedgerLink

This guide outlines the continuous integration (CI) setup for the LedgerLink application, ensuring that all code changes are automatically tested before being merged.

## Table of Contents

1. [CI Pipeline Overview](#ci-pipeline-overview)
2. [GitHub Actions Setup](#github-actions-setup)
3. [PostgreSQL Testing Setup](#postgresql-testing-setup)
4. [Test Execution Strategy](#test-execution-strategy)
5. [Performance Monitoring](#performance-monitoring)
6. [Contract Testing in CI](#contract-testing-in-ci)
7. [Deployment Pipeline](#deployment-pipeline)

## CI Pipeline Overview

The LedgerLink CI pipeline consists of the following stages:

1. **Code Quality Checks**
   - Linting (flake8, eslint)
   - Type checking
   - Code formatting verification

2. **Unit Testing**
   - Django model, view, and utility tests
   - React component and hook tests

3. **Integration Testing**
   - Cross-module integration tests
   - Database view tests
   - Service integration tests

4. **Contract Testing**
   - Pact contract verification

5. **Performance Testing**
   - API response time tests
   - Database query optimization tests
   - Scaling tests

6. **Deployment**
   - Staging deployment
   - Production deployment (manual trigger)

## GitHub Actions Setup

The CI pipeline is implemented using GitHub Actions in `.github/workflows/ci.yml`:

```yaml
name: LedgerLink CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          cd frontend && npm ci
      
      - name: Check Python code quality
        run: |
          flake8 .
          black --check .
          isort --check .
      
      - name: Check JavaScript code quality
        run: |
          cd frontend && npm run lint
  
  backend-tests:
    runs-on: ubuntu-latest
    needs: [code-quality]
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run unit tests
        run: |
          python -m pytest
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
  
  frontend-tests:
    runs-on: ubuntu-latest
    needs: [code-quality]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      
      - name: Install dependencies
        run: |
          cd frontend && npm ci
      
      - name: Run unit tests
        run: |
          cd frontend && npm test -- --coverage --watchAll=false
  
  integration-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run integration tests
        run: |
          python -m pytest tests/integration/
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
  
  contract-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pact-python
      
      - name: Run contract tests
        run: |
          # Start Django server in the background
          python manage.py runserver &
          sleep 5
          
          # Run Pact verification
          python tests/integration/pact-provider-verify.py
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
  
  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # Only run on schedule, not every PR
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run performance tests
        run: |
          python -m pytest tests/integration/test_performance.py
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
  
  deploy-staging:
    runs-on: ubuntu-latest
    needs: [integration-tests, contract-tests]
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        # Add deployment steps here
```

## PostgreSQL Testing Setup

LedgerLink tests require PostgreSQL for full compatibility. The GitHub Actions workflow sets up a PostgreSQL service container:

```yaml
services:
  postgres:
    image: postgres:13
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test_db
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### Test Database Configuration

Tests access the database using environment variables:

```yaml
env:
  DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
```

### Schema Setup

The database schema for tests is set up using:

1. **Django migrations** during test initialization
2. **Custom view creation** in `tests/integration/conftest.py`
3. **Test fixtures** for consistent starting state

## Test Execution Strategy

### Unit Tests

Unit tests run first and must pass before proceeding:

- Backend unit tests run with pytest
- Frontend unit tests run with Jest
- Both have coverage requirements (minimum 85% coverage)

### Integration Tests

Integration tests run after unit tests pass:

- Focus on cross-module interactions
- Test with realistic data volumes
- Verify critical business logic paths

### Contract Tests

Contract tests verify API consistency:

1. Generate Pact contracts from consumer expectations
2. Verify provider implementation matches contracts
3. Fail the build if contracts are broken

### Performance Tests

Performance tests run on a schedule, not on every PR:

- Measure response times for key API endpoints
- Track database query counts
- Monitor scaling behavior

## Performance Monitoring

Performance metrics are tracked over time:

1. **CI Test Results**: Stored as test artifacts
2. **Historical Trends**: Graphed in GitHub Actions summary
3. **Regression Detection**: Alert on significant performance degradation

### Performance Thresholds

CI enforces these performance thresholds:

- API response time: < 500ms for critical endpoints
- Database query count: ≤ 10 for list views
- Maximum memory usage: < 200MB during test execution

## Contract Testing in CI

Contract testing verifies that frontend and backend agree on API structure.

### Pact File Management

1. **Generation**: Frontend tests generate Pact files
2. **Storage**: Pact files are stored as artifacts
3. **Verification**: Backend verifies it can fulfill contracts

### Pact Broker (Optional)

For larger teams, set up a Pact Broker:

```yaml
- name: Publish Pact files
  run: |
    pact-broker publish pacts/ \
      --broker-base-url $PACT_BROKER_URL \
      --broker-username $PACT_BROKER_USERNAME \
      --broker-password $PACT_BROKER_PASSWORD \
      --consumer-app-version $GITHUB_SHA
  env:
    PACT_BROKER_URL: ${{ secrets.PACT_BROKER_URL }}
    PACT_BROKER_USERNAME: ${{ secrets.PACT_BROKER_USERNAME }}
    PACT_BROKER_PASSWORD: ${{ secrets.PACT_BROKER_PASSWORD }}
```

## Deployment Pipeline

After tests pass, the code can be deployed:

### Staging Deployment

Automatically deploy to staging when tests pass on the develop branch:

```yaml
deploy-staging:
  runs-on: ubuntu-latest
  needs: [integration-tests, contract-tests]
  if: github.ref == 'refs/heads/develop'
  
  steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to staging
      # Add deployment steps here
```

### Production Deployment

Production deployment requires manual approval:

```yaml
deploy-production:
  runs-on: ubuntu-latest
  needs: [integration-tests, contract-tests]
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://ledgerlink.example.com
  
  steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      # Add production deployment steps here
```

## Best Practices

1. **Optimize Test Speed**: Keep tests fast to maintain quick feedback loops
2. **Separate Slow Tests**: Run slow tests on a schedule, not every PR
3. **Maintain Test Data**: Use consistent test data across CI runs
4. **Monitor Test Flakiness**: Track and fix flaky tests quickly
5. **Keep Dependencies Updated**: Regularly update testing dependencies
6. **Document CI Changes**: Keep this guide updated when changing CI configuration

## Troubleshooting CI Issues

If CI tests fail, follow these steps:

1. Check the CI logs for specific error messages
2. Reproduce the failure locally using the same environment
3. Examine test data for potential issues
4. Check for environment differences between CI and local development
5. Verify database schema matches expectations

## Further Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pact Contract Testing](https://docs.pact.io/)
- [PostgreSQL Testing Best Practices](https://www.postgresql.org/docs/current/app-pgtestdatabase.html)