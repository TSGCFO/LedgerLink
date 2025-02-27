# LedgerLink Project Documentation

## Project Overview
LedgerLink is a web application built with Django REST Framework and React with Material UI. It provides a system for managing customers, orders, products, and billing for a fulfillment or logistics business.

## Linting and Code Quality
The project uses an AI-powered fullstack linting system based on Claude. These scripts analyze code across the Django backend and React frontend to catch issues that traditional linters miss:

- `npm run lint` - Run a complete fullstack analysis
- `npm run lint:watch` - Run the linter in watch mode
- `npm run lint:claude` - Run raw Claude analysis

The lint scripts detect critical issues like:
- API endpoint mismatches between backend and frontend
- Data structure inconsistencies between Django models and React components
- Security vulnerabilities and performance issues
- Other common bugs and logic errors

For more details, see LINTING.md.

## Important Commands
```bash
# Backend (Django)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # Backend server (http://localhost:8000)

# Frontend (React)
cd frontend
npm install
npm run dev  # Frontend server (http://localhost:5175)
npm run build  # Build for production
npm run lint  # Run ESLint
```

## Code Style and Conventions
- Django apps follow standard Django structure
- PEP 8 standards for Python code
- React components use functional components with hooks
- React Router for navigation
- Material UI for component library
- API endpoints are RESTful

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
- RESTful API endpoints for CRUD operations
- JWT authentication
- Custom error handling and response formatting
- API client with token refresh
- Comprehensive error logging

## Notes
- The application appears to be a fulfillment/logistics management system
- Billing uses a complex rule system to calculate charges based on order attributes
- Rules can be simple or advanced with different calculation methods (flat fee, percentage, tiered, etc.)
- The frontend uses a proxy setup to forward API requests to the backend during development