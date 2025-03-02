# Changelog

All notable changes to the LedgerLink project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed
- **Critical Bug Fix**: Fixed the "not equals" (`ne`) operator in rule evaluation. The `evaluate_condition` function was previously looking for `neq` instead of `ne`, causing incorrect evaluation of rules using this operator. This could have affected billing calculations and business logic decisions. The fix supports both `ne` and `neq` for backward compatibility.
- **Critical Bug Fix**: Fixed the "not contains" (`ncontains`) operator in rule evaluation. The `evaluate_condition` function was previously looking for `not_contains` instead of `ncontains`, causing incorrect evaluation of rules using this operator. This affected string field and JSON field evaluations. The fix supports both `ncontains` and `not_contains` for backward compatibility.

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