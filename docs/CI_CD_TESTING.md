# CI/CD Testing Integration

This document explains how the LedgerLink testing infrastructure is integrated with CI/CD pipelines through GitHub Actions.

## Overview

LedgerLink uses GitHub Actions to automate testing on code pushes and pull requests. The CI/CD workflow includes:

1. **Linting**: Check code style and formatting
2. **Unit Tests**: Run backend and frontend unit tests
3. **Contract Tests**: Verify API contracts
4. **E2E Tests**: Run Cypress tests against a live instance
5. **Coverage Reports**: Generate and publish coverage reports

## Workflow Files

The CI/CD configuration is split into two workflow files:

- `.github/workflows/main.yml`: Core testing workflow (linting, unit tests, contract tests)
- `.github/workflows/e2e-tests.yml`: End-to-end testing workflow

## When Tests Run

Tests are automatically triggered on:

- **Push** to `main` or `develop` branches
- **Pull Requests** targeting `main` or `develop` branches
- **Manual trigger** via GitHub Actions UI
- **Scheduled runs** for E2E tests (weekdays at 2 AM)

## Workflow Steps

### Main Workflow

The main workflow runs the following jobs in sequence:

1. **Lint**: Runs code linters to check style and formatting

   ```yaml
   lint:
     name: Linting
     runs-on: ubuntu-latest
     steps:
       # Setup and run linters
   ```

2. **Backend Tests**: Runs Django unit tests with pytest

   ```yaml
   backend-tests:
     name: Backend Tests
     runs-on: ubuntu-latest
     needs: lint
     services:
       postgres:
         # PostgreSQL service container configuration
     steps:
       # Run backend tests with coverage
   ```

3. **Frontend Tests**: Runs React component tests with Jest

   ```yaml
   frontend-tests:
     name: Frontend Tests
     runs-on: ubuntu-latest
     needs: lint
     steps:
       # Run frontend tests with coverage
   ```

4. **Contract Tests**: Runs Pact contract verification

   ```yaml
   contract-tests:
     name: Contract Tests
     runs-on: ubuntu-latest
     needs: [backend-tests, frontend-tests]
     steps:
       # Run Pact consumer tests and provider verification
   ```

5. **Coverage Report**: Combines coverage from frontend and backend

   ```yaml
   coverage-report:
     name: Combined Coverage Report
     runs-on: ubuntu-latest
     needs: [backend-tests, frontend-tests]
     steps:
       # Merge and publish coverage reports
   ```

### E2E Workflow

The end-to-end workflow runs the following jobs:

1. **Cypress Tests**: Starts servers and runs Cypress tests

   ```yaml
   cypress-tests:
     name: Cypress E2E Tests
     runs-on: ubuntu-latest
     services:
       postgres:
         # PostgreSQL service container configuration
     steps:
       # Start servers and run Cypress tests
   ```

## Requirements

The CI/CD workflows require the following:

### Repository Secrets

Add these secrets in GitHub repository settings:

- `PACT_BROKER_URL`: URL to your Pact broker (if using one)
- `PACT_BROKER_TOKEN`: Authentication token for the Pact broker
- `CYPRESS_RECORD_KEY`: Record key for Cypress Dashboard (optional)

### Test Database

The tests use a PostgreSQL database with the following configuration:

```
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres
POSTGRES_DB: ledgerlink_test
```

## Test Artifacts

The CI/CD workflows generate the following artifacts:

- **Coverage Reports**: HTML, LCOV, and text coverage reports
- **Pact Files**: Contract definition files
- **Cypress Videos/Screenshots**: Recordings of failed E2E tests

Access these artifacts through the GitHub Actions UI after workflow completion.

## Adding Tests to CI

When adding new tests, ensure they are compatible with the CI environment:

1. **Backend Tests**: Ensure tests use the correct settings and dependencies
2. **Frontend Tests**: Make sure tests don't depend on browser-specific features
3. **E2E Tests**: Use stable selectors and handle async operations properly

## Customizing CI Workflow

### Adding New Jobs

To add a new test job to the workflow:

1. Edit the appropriate workflow file (`.github/workflows/main.yml` or `.github/workflows/e2e-tests.yml`)
2. Add a new job section with required steps
3. Define dependencies on other jobs with `needs:`

Example:

```yaml
security-tests:
  name: Security Tests
  runs-on: ubuntu-latest
  needs: [lint]
  steps:
    - uses: actions/checkout@v3
    - name: Run security scans
      run: npm run security-scan
```

### Changing Test Runner Configuration

To modify test runner settings:

1. For backend tests, update `run_tests.sh` or pass additional flags
2. For frontend tests, modify Jest configuration
3. For Cypress tests, update Cypress configuration

## Troubleshooting CI Issues

### Common Problems

1. **Tests Pass Locally But Fail in CI**:
   - Check for environment differences
   - Verify database setup in CI
   - Look for timing issues in tests

2. **Cypress Tests Flaking in CI**:
   - Check for race conditions
   - Add explicit waits for API responses
   - Use network interception instead of timers

3. **Slow CI Pipeline**:
   - Use caching for dependencies
   - Run tests in parallel when possible
   - Skip unnecessary tests in certain situations

### Viewing Logs

1. Navigate to the GitHub Actions tab in your repository
2. Select the workflow run
3. Expand the job with issues
4. Click on the failing step to view logs

## Best Practices

1. **Keep CI Fast**: Optimize test suites to run quickly in CI
2. **Fail Early**: Run fast-failing tests first (like linting)
3. **Independence**: Ensure tests don't depend on each other
4. **Idempotence**: Tests should be repeatable without side effects
5. **Branch Protection**: Require passing tests before merging

## Future Enhancements

Consider the following enhancements to the CI/CD pipeline:

1. **Parallel Testing**: Split test suites to run in parallel
2. **Matrix Testing**: Test across multiple Node.js/Python versions
3. **Deployment Integration**: Add automatic deployment on successful tests
4. **Performance Testing**: Add load testing to CI pipeline
5. **Notifications**: Configure Slack/email notifications for test failures
