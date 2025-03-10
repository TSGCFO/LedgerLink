#!/bin/bash
set -e

# Setup script for billing app testing environment
# This script sets up the necessary testing infrastructure for the billing app

echo "Setting up billing app testing environment..."

# Create necessary directories if they don't exist
mkdir -p billing/tests/test_models
mkdir -p billing/tests/test_serializers
mkdir -p billing/tests/test_views
mkdir -p billing/tests/test_integration
mkdir -p .github/pre-commit-hooks

# Make sure the pre-commit hook is executable
if [ -f .github/pre-commit-hooks/billing-tests.sh ]; then
  chmod +x .github/pre-commit-hooks/billing-tests.sh
  echo "✅ Pre-commit hook executable permission set"
else
  echo "❌ Pre-commit hook file not found"
fi

# Check if Docker is available
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
  echo "✅ Docker and Docker Compose are installed"
else
  echo "⚠️ Docker and/or Docker Compose not found - they are required for Docker-based testing"
fi

# Check if npm is available for frontend tests
if command -v npm >/dev/null 2>&1; then
  echo "✅ npm is installed"
else
  echo "⚠️ npm not found - it is required for frontend testing"
fi

# Check for Python environment
if command -v python >/dev/null 2>&1; then
  python_version=$(python --version 2>&1)
  echo "✅ Python is installed: $python_version"
else
  echo "❌ Python not found - it is required for running tests"
  exit 1
fi

# Check for pytest
if python -c "import pytest" 2>/dev/null; then
  echo "✅ pytest is installed"
else
  echo "⚠️ pytest not found - installing..."
  pip install pytest pytest-django pytest-cov
fi

# Set up pre-commit hook if desired
read -p "Do you want to set up the pre-commit hook for billing tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  if [ -d .git/hooks ]; then
    cp .github/pre-commit-hooks/billing-tests.sh .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook installed successfully"
  else
    git config core.hookspath .github/pre-commit-hooks
    echo "✅ Git configured to use hooks from .github/pre-commit-hooks"
  fi
fi

# Mark test scripts as executable
if [ -f run_billing_tests.sh ]; then
  chmod +x run_billing_tests.sh
  echo "✅ run_billing_tests.sh is now executable"
fi

if [ -f run_billing_coverage.sh ]; then
  chmod +x run_billing_coverage.sh
  echo "✅ run_billing_coverage.sh is now executable"
fi

# Run a basic check to ensure tests can be found
echo "Checking that pytest can find the billing tests..."
python -m pytest billing --collect-only -q

echo -e "\n✅ Billing test environment setup complete!"
echo -e "You can now run tests with:"
echo -e "  - ./run_billing_tests.sh           (Docker-based tests)"
echo -e "  - ./run_billing_coverage.sh        (Coverage report)"
echo -e "  - python -m pytest billing/        (Direct tests)"
echo -e "  - cd frontend && npm test -- --testPathPattern=src/components/billing"
echo -e "\nSee billing/TESTING_AUTOMATION.md for more details."