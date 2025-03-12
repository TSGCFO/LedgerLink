# Billing App Testing Automation

This document describes the automated testing setup for the LedgerLink Billing application.

## CI/CD Integration

The billing app has a dedicated GitHub Actions workflow that automates various test suites. This workflow is defined in `.github/workflows/billing-tests.yml` and runs whenever changes are made to the billing module or its testing infrastructure.

### Workflow Jobs

The workflow consists of several jobs that run in sequence:

1. **billing-tests**: Runs all backend unit tests and integration tests for the billing app
   - Model tests
   - Serializer tests
   - View tests
   - Integration tests
   - Billing calculator tests
   - Services and utility tests
   - Generates coverage reports

2. **billing-docker-tests**: Runs tests in a Docker environment to ensure compatibility
   - Uses Docker Compose to set up a complete test environment
   - Executes the `run_billing_tests.sh` script
   - Generates and stores coverage reports

3. **billing-frontend-tests**: Tests the React frontend components for the billing module
   - Component tests
   - Accessibility tests
   - Generates coverage reports

4. **billing-e2e-tests**: End-to-end testing with Cypress
   - Sets up both backend and frontend servers
   - Runs the Cypress E2E tests specific to billing workflows
   - Captures and stores screenshots and videos for debugging

## How to Use

### Running Locally

To run the tests locally, you can use the provided scripts:

```bash
# Run all billing tests in Docker (recommended)
./run_billing_tests.sh

# Generate coverage reports
./run_billing_coverage.sh

# Run specific test types
python -m pytest billing/tests/test_models/ -v
python -m pytest billing/tests/test_serializers/ -v
python -m pytest billing/tests/test_views/ -v
python -m pytest billing/tests/test_integration/ -v

# Run frontend tests
cd frontend
npm test -- --testPathPattern=src/components/billing
```

### Triggering in CI

The workflow will automatically run on:
- Push to master/develop branches that include changes to billing files
- Pull requests to master/develop that include billing changes
- Manual trigger via GitHub Actions interface (workflow_dispatch event)

## Coverage Reports

Coverage reports are generated in multiple formats:
- XML for Codecov integration
- HTML for local viewing (in the `htmlcov/` directory)
- Markdown summary in `billing/COVERAGE_REPORT.md`

## Artifacts

The workflow stores several artifacts that can be downloaded from the GitHub Actions interface:
- Coverage reports
- Cypress screenshots (on test failure)
- Cypress videos of test runs

## Extending the Tests

### Adding Backend Tests

1. Place new test files in the appropriate directory:
   - `billing/tests/test_models/` for model tests
   - `billing/tests/test_serializers/` for serializer tests
   - `billing/tests/test_views/` for view tests
   - `billing/tests/test_integration/` for integration tests

2. The CI workflow will automatically discover and run these tests.

### Adding Frontend Tests

1. Add component tests in `frontend/src/components/billing/__tests__/`
2. For E2E tests, add or update `frontend/cypress/e2e/billing.cy.js`

## Pre-commit Hooks

A pre-commit hook script is provided to run relevant billing tests before each commit. This helps catch issues early in the development process.

### Setup

1. Make the script executable:
   ```bash
   chmod +x .github/pre-commit-hooks/billing-tests.sh
   ```

2. Either:
   - Copy the script to your `.git/hooks` directory:
     ```bash
     cp .github/pre-commit-hooks/billing-tests.sh .git/hooks/pre-commit
     ```
   - Or configure Git to use the hooks directory:
     ```bash
     git config core.hookspath .github/pre-commit-hooks
     ```

### Behavior

The hook will:
- Only run when files in the billing module are modified
- Run a subset of tests relevant to the specific changes
- Block commits if tests fail (can be bypassed with `--no-verify` if needed)

### Skipping the Hook

If needed, you can bypass the hook with:
```bash
git commit --no-verify
```

## Monitoring

The testing status is visible in GitHub:
- Pull request status checks
- GitHub Actions workflow runs
- Codecov coverage reports and comments on PRs