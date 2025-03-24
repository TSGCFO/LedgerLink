# Makefile for testing Bash scripts

.PHONY: test lint fix setup clean all

# Script to test
SCRIPT := scripts/file-validator-optimized.sh

# Test file
TEST_FILE := test_file_validator.bats

# Testing tools
SHELLCHECK := shellcheck
BATS := bats

# Help function - display available commands
help:
	@echo "Available commands:"
	@echo "  make lint    - Run ShellCheck static analysis"
	@echo "  make test    - Run BATS functional tests"
	@echo "  make setup   - Set up testing environment"
	@echo "  make fix     - Show ShellCheck fixing suggestions"
	@echo "  make all     - Run lint and test"
	@echo "  make clean   - Clean up test artifacts"
	@echo "  make help    - Show this help message"

# Run ShellCheck static analysis
lint:
	@echo "Running ShellCheck on $(SCRIPT)..."
	@$(SHELLCHECK) $(SCRIPT) || { echo "ShellCheck found issues"; exit 1; }
	@echo "ShellCheck passed!"

# Run BATS tests
test:
	@echo "Running BATS tests..."
	@$(BATS) $(TEST_FILE)

# Show ShellCheck fixing suggestions
fix:
	@echo "Running ShellCheck with fixing suggestions..."
	@$(SHELLCHECK) -f diff $(SCRIPT)

# Run all tests
all: lint test

# Set up testing environment
setup:
	@echo "Setting up test environment..."
	@command -v $(SHELLCHECK) >/dev/null 2>&1 || { echo "Error: ShellCheck not found. Please install it first."; exit 1; }
	@command -v $(BATS) >/dev/null 2>&1 || { echo "Error: BATS not found. Please install it first."; exit 1; }
	@mkdir -p bats-test/test_helper
	@if [ ! -d "bats-test/test_helper/bats-support" ]; then \
		echo "Installing bats-support..."; \
		git clone https://github.com/bats-core/bats-support.git bats-test/test_helper/bats-support; \
	else \
		echo "bats-support already installed."; \
	fi
	@if [ ! -d "bats-test/test_helper/bats-assert" ]; then \
		echo "Installing bats-assert..."; \
		git clone https://github.com/bats-core/bats-assert.git bats-test/test_helper/bats-assert; \
	else \
		echo "bats-assert already installed."; \
	fi
	@if [ ! -d "bats-test/test_helper/bats-file" ]; then \
		echo "Installing bats-file..."; \
		git clone https://github.com/bats-core/bats-file.git bats-test/test_helper/bats-file; \
	else \
		echo "bats-file already installed."; \
	fi
	@echo "Test environment setup complete!"

# Clean up test artifacts
clean:
	@echo "Cleaning up test artifacts..."
	@find . -name "*.log" -type f -delete
	@find . -name "*.tmp" -type f -delete
	@find . -name "*~" -type f -delete
	@echo "Cleanup complete!"

# Default target
default: help
