# Changelog

All notable changes to the LedgerLink project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Comprehensive Billing Tests**: Added extensive test suite with 28+ test cases for the billing system
- **Standalone Tests**: Created standalone test files for billing system that don't require Django environment
- **Case-Based Tier Tests**: Added specialized tests for case-based tier calculations and boundary conditions
- **Rule Integration Tests**: Added tests for the integration between rule system and billing calculator

### Changed
- **Testing Infrastructure**: Enhanced the testing framework with standalone and integrated test components
- **Test Coverage**: Expanded test coverage to include all rule operators and edge cases

### Fixed
- **Critical Bug Fix**: Fixed the "not equals" (`ne`) operator in rule evaluation. The `evaluate_condition` function was previously looking for `neq` instead of `ne`, causing incorrect evaluation of rules using this operator. This could have affected billing calculations and business logic decisions. The fix supports both `ne` and `neq` for backward compatibility.
- **Critical Bug Fix**: Fixed the "not contains" (`ncontains`) operator in rule evaluation. The `evaluate_condition` function was previously looking for `not_contains` instead of `ncontains`, causing incorrect evaluation of rules using this operator. This affected string field and JSON field evaluations. The fix supports both `ncontains` and `not_contains` for backward compatibility.
- **Billing System Fix**: Updated the billing calculator's RuleEvaluator class to handle both `ne`/`neq` and `ncontains`/`not_contains` operator variants consistently with the main rule system. This ensures correct service application and cost calculation in billing reports.
- **SKU Normalization**: Fixed inconsistencies in SKU normalization across different parts of the system
- **Rule Group Logic**: Enhanced testing of different rule group logic operators (AND, OR, NOT)

### Security

## [2.1.0] - 2025-02-15

### Added
- Comprehensive logging system with client and server components
- Advanced rule testing interface with sample data input
- Bulk operations for data import/export functionality

### Changed
- Improved rule group management with enhanced UI
- Updated billing report generation for better performance
- Enhanced error handling in API client with automatic token refresh

### Fixed
- Connection issue in API client with retry mechanism
- Path conversion for WSL integration
- Rule group deletion cascade issues

### Security
- Added token verification endpoint
- Improved CSRF protection for API routes
- Enhanced permission checks for sensitive operations