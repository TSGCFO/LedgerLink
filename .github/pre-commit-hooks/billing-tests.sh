#!/bin/bash
set -e

# Pre-commit hook for running billing tests
#
# Place this file in .git/hooks/pre-commit to enable it
# or run: git config core.hookspath .github/pre-commit-hooks
#
# You can skip this hook with: git commit --no-verify

# Check if any staged files are in the billing module
# Only run tests if there are changes to billing files
if git diff --cached --name-only | grep -q "^billing/"; then
  echo "🔍 Billing changes detected, running billing tests..."
  
  # Function to check for failing tests
  run_tests() {
    if ! eval "$1"; then
      echo "❌ Billing tests failed. Fix the issues before committing or use --no-verify to skip checks."
      exit 1
    fi
  }
  
  # Run core billing calculator tests (these are fast)
  echo "⚙️ Running billing calculator tests..."
  run_tests "python -m pytest billing/test_billing_calculator.py -v"
  
  # Run model tests (these are usually fast)
  if [ -d "billing/tests/test_models" ]; then
    echo "📊 Running billing model tests..."
    run_tests "python -m pytest billing/tests/test_models -v"
  fi
  
  # If changes are in serializers, run serializer tests
  if git diff --cached --name-only | grep -q "billing/serializers"; then
    echo "📦 Running billing serializer tests..."
    if [ -d "billing/tests/test_serializers" ]; then
      run_tests "python -m pytest billing/tests/test_serializers -v"
    fi
  fi
  
  # If changes are in views, run view tests
  if git diff --cached --name-only | grep -q "billing/views"; then
    echo "🌐 Running billing view tests..."
    if [ -d "billing/tests/test_views" ]; then
      run_tests "python -m pytest billing/tests/test_views -v"
    fi
  fi
  
  echo "✅ All billing tests passed!"
else
  echo "⏩ No billing changes detected, skipping billing tests."
fi

exit 0