# LedgerLink Linting Tools

This document describes the linting tools available in the LedgerLink project.

## Claude AI-Powered Linting

LedgerLink uses Claude AI to provide intelligent code analysis that goes beyond traditional linting tools. Our custom linting scripts analyze both syntax and semantic relationships between frontend and backend code.

### Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| Standard lint | `npm run lint` | Performs a complete analysis of the codebase, finding issues across the full stack |
| Watch mode | `npm run lint:watch` | Continuously monitors files and runs the linter when changes are detected |
| Claude-only analysis | `npm run lint:claude` | Runs a full analysis using Claude AI without additional processing |

### Benefits of the Fullstack Linter

Our fullstack linter provides several advantages over traditional linting tools:

1. **Cross-stack Analysis**: Detects inconsistencies between Django backend and React frontend
2. **API Endpoint Validation**: Ensures backend endpoints match frontend API calls
3. **Data Structure Validation**: Checks that Django models are properly represented in React components
4. **Semantic Analysis**: Identifies logical issues that typical linters miss
5. **Dependency Tracking**: Maps relationships between files to identify the impact of changes

### Pre-commit Hook

A pre-commit hook is installed to run the linter automatically before each commit. This ensures that code quality issues are caught before they enter the repository.

### Usage Tips

- Run `npm run lint:watch` during active development for real-time feedback
- The linter provides specific line numbers and suggested fixes for each issue
- Issues are sorted by severity (Critical, High, Medium, Low)
- For large projects, consider limiting analysis to specific directories

### Customizing the Linter

The linting scripts are located in the project root:
- `claude-lint-fullstack.js` - Main linting script with fullstack capabilities
- `claude-lint-script.js` - Basic linting script
- `claude-lint-watch.js` - Watch-mode implementation

These scripts can be modified to adjust the linting rules or add additional checks as needed.