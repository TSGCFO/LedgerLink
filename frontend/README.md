# LedgerLink Frontend

## Overview
This is the frontend application for LedgerLink, built with React, Vite, and Material UI. It provides a user interface for managing customers, orders, products, and billing for a fulfillment or logistics business.

## Technologies
- React 18
- Vite
- Material UI v5
- React Router v6
- Axios for API requests
- Cypress for testing
- Jest for unit testing

## Getting Started

### Installation
```bash
# Install dependencies
npm install
```

### Development
```bash
# Start development server
npm run dev
```
The development server will start at http://localhost:5175

### Building for Production
```bash
# Build production bundle
npm run build

# Preview production build
npm run preview
```

## Testing

### Running Tests
```bash
# Unit tests with Jest
npm test
npm run test:watch
npm run test:coverage

# Accessibility tests
npm run test:a11y

# Cypress component tests
npm run cypress:open --component

# Cypress E2E tests
npm run cypress:open
npm run cypress:run
npm run e2e
npm run e2e:headless
```

### Cypress Tests
Cypress tests are organized in two categories:
- **Component Tests**: Located in `cypress/component/`
- **E2E Tests**: Located in `cypress/e2e/`

For more details, see the [Cypress README](./cypress/README.md).

## Project Structure
```
frontend/
├── cypress/                  # Cypress tests
├── public/                   # Public assets
├── src/
│   ├── components/           # React components organized by feature
│   │   ├── auth/             # Authentication components
│   │   ├── billing/          # Billing components
│   │   ├── bulk-operations/  # Bulk operations components
│   │   ├── common/           # Shared components
│   │   ├── customer-services/# Customer services components
│   │   ├── customers/        # Customer management components
│   │   ├── inserts/          # Insert management components 
│   │   ├── materials/        # Materials management components
│   │   ├── orders/           # Order management components
│   │   ├── products/         # Product management components
│   │   ├── rules/            # Business rules components
│   │   ├── services/         # Service management components
│   │   └── shipping/         # Shipping components
│   ├── services/             # API services
│   ├── utils/                # Utility functions
│   ├── App.jsx               # Main application component
│   ├── main.jsx              # Application entry point
│   └── index.css             # Global styles
└── package.json              # Package configuration
```

## API Integration
The application communicates with the Django backend API. API configuration can be found in:
- `src/utils/apiClient.js` - Axios configuration with token handling
- `src/services/` - Service modules for API calls

## Recent Updates

### Billing V2 Implementation
- Added new Billing V2 module for improved reporting
- Fixed import paths and API endpoint URLs
- Enhanced error handling and user feedback
- Updated API client to support proper endpoint handling
- Added defensive coding to handle various API response scenarios

### Testing Improvements
- Fixed and improved Cypress E2E tests
- Made tests more resilient to timing issues and UI changes
- Simplified complex tests to focus on core functionality
- Added more comprehensive test documentation
- Improved error handling in tests

### Bulk Operations Module
- Added comprehensive tests for all workflow steps
- Implemented proper mocking for API responses
- Added validation and error handling
- Fixed accessibility issues

## Testing Coverage and Roadmap

### Current Test Coverage Status
The application has varying levels of test coverage:

- **Very Comprehensive (90%+)**: Customer Services, Customers, Rules
- **Comprehensive (70-90%)**: Auth, Bulk Operations, Orders, Products, Services 
- **Moderate (40-70%)**: Billing
- **Missing (0%)**: Inserts, Materials, Shipping

### Priority Testing Improvements
1. **Add Missing E2E Tests**:
   - Create E2E tests for Inserts, Materials, and Shipping components
   - Implement basic CRUD operation testing for each module

2. **Enhance Existing Test Coverage**:
   - Improve Billing module tests to handle error cases and complex pricing
   - Add Auth tests for password reset and session management
   - Extend Orders tests to cover complex order scenarios

3. **Restore Proper Accessibility Testing**:
   - Implement comprehensive accessibility testing across all components
   - Fix identified accessibility issues

For a detailed breakdown of test coverage status, see the [Cypress README](./cypress/README.md).
For the complete implementation plan and timeline, see the [Testing Roadmap](./cypress/TESTING_ROADMAP.md).

## Contributing
1. Install dependencies with `npm install`
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request

## License
Proprietary - All rights reserved