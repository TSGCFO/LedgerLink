# LedgerLink Project Documentation

## Project Overview
LedgerLink is a web application built with Django REST Framework and React with Material UI. It provides a system for managing customers, orders, products, and billing for a fulfillment or logistics business.

## Build, Lint, and Test Commands
```bash
# Backend (Django)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # Backend server (http://localhost:8000)

# Testing
python manage.py test  # Run all tests
python manage.py test <app_name>  # Test specific app
python manage.py test <app_name>.tests.<TestClass>.<test_method>  # Run single test

# Frontend (React)
cd frontend
npm install
npm run dev  # Frontend server (http://localhost:5175)
npm run build  # Build for production
npm run lint  # Run ESLint

# AI-Powered Fullstack Linting
npm run lint  # Complete fullstack analysis with Claude AI
npm run lint:watch  # Claude linter in watch mode
npm run lint:claude  # Claude-only analysis without additional processing
```

## Code Style Guidelines
- **Python**: Follow PEP 8 standards with 4-space indentation
  - Use absolute imports with Django app structure
  - Type hints encouraged for function parameters and returns
  - Follow Django's model->serializer->view pattern
  - Error handling with custom exceptions defined in api/exceptions.py
  - Naming: snake_case for variables/functions, PascalCase for classes
  
- **JavaScript/React**: 
  - Use ESLint with configured rules (strictNullChecks: true)
  - Functional components with hooks, avoid class components
  - Material UI for component library (v5)
  - Props destructuring and PropTypes validation
  - Clear error boundaries and fallbacks
  - Prefer named exports over default exports

## Linting Framework
- **AI-Powered Analysis**: Uses Claude AI for intelligent code scanning
- **Cross-stack Validation**: Checks consistency between Django and React
- **API Endpoint Validation**: Ensures backend endpoints match frontend calls
- **Pre-commit Hook**: Runs automatically before each commit
- **Custom Linting Scripts**: Located in project root (`claude-lint-*.js`)

## Project Structure
### Backend (Django)
- **customers/** - Customer management
- **orders/** - Order management
- **products/** - Product catalog
- **services/** - Service offerings
- **billing/** - Billing and invoicing
- **rules/** - Business rules for pricing and conditions
- **inserts/** - Insertable material management
- **shipping/** - Shipping and logistics
- **materials/** - Raw materials tracking
- **ai_core/** - AI components for automation
- **bulk_operations/** - Bulk import/export functionality
- **customer_services/** - Customer-specific service configurations

### Frontend (React)
- **src/**
  - **components/** - React components organized by feature
  - **utils/** - Utility functions (auth, API client, logger)
  - **App.jsx** - Main application component with routing
  - **main.jsx** - Application entry point

## Frontend Architecture
- **Component Structure**: Organized by feature (customers, orders, billing, etc.)
- **State Management**: Local React state with hooks (useState, useEffect)
- **Routing**: React Router v6 with protected routes
- **API Integration**: Custom API client with token-based authentication
- **UI Framework**: Material UI v5 with custom theme
- **Tables**: Material React Table for data tables
- **Forms**: Material UI form components
- **Build Tool**: Vite for development and production builds
- **Authentication**: JWT tokens stored in localStorage

## Key Models
- **Customer**: Basic customer information (company_name, contact details, etc.)
- **Order**: Transaction details with shipping information and SKU quantities
- **Rule/RuleGroup**: Business logic for determining service pricing
  - **BasicRule**: Simple condition-based rules (field, operator, value)
  - **AdvancedRule**: Complex rules with JSON-based conditions and calculations
    - Supports case-based tiers with min/max ranges and values in tier_config
- **BillingReport**: Generated billing reports for customers

## Database
- PostgreSQL database hosted on Supabase
- Contains views for specialized data access like OrderSKUView

### Data Import Scripts
The following scripts are available for importing data:

```bash
# Import orders from CSV file
python import_orders.py orders_order_rows.csv

# Import shipping data (CAD or US)
python import_shipping.py shipping_cadshipping_rows.csv
python import_shipping.py shipping_usshipping_rows.csv us

# Import products
python import_products.py products_product.csv

# Check imported data
python check_order_data.py
python check_shipping_data.py
python check_product_data.py
```

### Materialized View Maintenance

Materialized views (`orders_sku_view` and `customer_services_customerserviceview`) should be refreshed regularly:

```bash
# Refresh all materialized views (standard mode)
python manage.py refresh_all_views

# Refresh with concurrent mode (for minimal locking when views are already populated)
python manage.py refresh_all_views --concurrent
```

### Database Alignment

The database schema should be aligned with Django models. If you find issues, use:

```bash
# Check for schema issues
python manage.py check

# Fix database alignment issues (if needed)
python fix_db_alignment.py
```

## API Structure
- RESTful API endpoints for CRUD operations following Django REST Framework conventions
- JWT authentication with token refresh mechanism
- Custom exception classes in api/exceptions.py
- Consistent response format with error handling
- API client with automatic token refresh in frontend/src/utils/apiClient.js
- Comprehensive request/response logging

## Logging System

### Client-Side Logging
- Implemented in `frontend/src/utils/logger.js`
- Captures all console logs (debug, info, warn, error) automatically
- Stores logs in localStorage with timestamp and contextual data
- Maximum storage of 10,000 logs with automatic rotation

#### Usage
```javascript
// Import in components
import logger from '../utils/logger';

// Log at different levels
logger.debug('Debug message', { optional: 'data' });
logger.info('Info message');
logger.warn('Warning message');
logger.error('Error message', error); // Optional error object

// API logging (used by apiClient.js)
logger.logApiRequest(method, url, options);
logger.logApiResponse(method, url, response, data);
logger.logApiError(method, url, error);

// Log management
const logs = logger.getLogs();  // Get all stored logs
logger.clearLogs();             // Clear all logs
logger.exportLogs();            // Download logs as JSON file
await logger.saveLogsToServer(); // Save logs to server
```

#### Log Viewer
- Access the log viewer by clicking the bug icon in the app header
- View, filter, search and export logs
- Save logs to server for admin access

### Server-Side Logging
- Django logging configured in `LedgerLink/logging_settings.py`
- Client logs saved in `logs/client/` directory
- System logs in `logs/` directory:
  - `debug_YYYYMMDD.log` - All levels
  - `error_YYYYMMDD.log` - Error level only
  - `api_YYYYMMDD.log` - API requests and responses

#### API Endpoints
```
# Save client logs
POST /api/v1/logs/client/

# List client log files (admin only)
GET /api/v1/logs/client/list/ 

# Get client log file content (admin only)
GET /api/v1/logs/client/<filename>/
```

#### Decorator Usage
```python
from api.utils.logging_utils import log_view_access, log_model_access

# Log view access with timing info
@log_view_access(logger=customers_logger)
def my_view(request):
    # View code here

# Log model operations
@log_model_access(logger=orders_logger)
def create_order(self):
    # Model method code here
```

## Testing the Logging System
- Use `logging_test.html` to test client-side logging
- Use `test_logging.js` for scripted test cases
- Use `test_server_logging.py` to test server-side API

## Development Best Practices
- Run linting in watch mode during active development
- Always run tests before committing changes
- Follow existing code patterns for consistency
- Use the logging system for debugging
- Refresh materialized views after data changes
- Use server-side validation for all form inputs
- Follow existing rules pattern for new business logic
- Remember to update both frontend and backend components when changing models

## Rules System Testing
- **Case-Based Tiers**: Test with various min/max ranges to ensure proper calculation
  - Use `case_based_tier` field type in the frontend
  - Ensure `tier_config` is included at the root level of the rule JSON
  - Validate proper tier progression (min/max shouldn't overlap)
  - Test edge cases at tier boundaries
- **Server-Side Validation**: Always matches client-side validation constraints
  - Validate both in frontend (AdvancedRuleBuilder.jsx) and backend (validators.py)
  - Check for proper error messages and validation logic consistency
- **Rule Execution**: Test rule evaluation with real SKU and order data
  - Create comprehensive test cases for each rule type
  - Verify calculation accuracy especially with decimal values
  - Validate complex nested conditions and rule groups

## Project Architecture Summary
- Django REST Framework backend with PostgreSQL database
- React frontend with Material UI components
- JWT authentication for API security
- Complex rule system for business logic and pricing
- Comprehensive logging at all levels
- Bulk operations for data import/export