# LedgerLink Project Documentation

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
SKIP_MATERIALIZED_VIEWS=True python -m pytest app_name/tests/ -v  # With pytest
./run_docker_tests.sh  # Run tests in Docker (recommended for DB tests)
./run_testcontainers_tests.sh  # Run tests with TestContainers

# Frontend (React)
cd frontend
npm install
npm run dev  # Frontend server (http://localhost:5175)
npm run build  # Build for production
npm run lint  # Run ESLint
```

## Code Style Guidelines
- **Python**: Follow PEP 8 with 4-space indentation
  - Use absolute imports with Django app structure
  - Type hints required for function parameters and returns
  - Follow Django's model->serializer->view pattern
  - Error handling with custom exceptions (api/exceptions.py)
  - Naming: snake_case for variables/functions, PascalCase for classes
  
- **JavaScript/React**: 
  - Use functional components with hooks, avoid class components
  - Material UI v5 for component library (Material React Table for lists)
  - Props destructuring and PropTypes validation
  - Clear error boundaries and fallbacks
  - Prefer named exports over default exports

## Development Constraints (from Cursor Rules)
- **Django Settings**: Don't modify existing settings.py, only add to it
- **Models**: Don't modify existing models or relationships without approval
- **Security**: Don't implement security features during development
- **Frontend Organization**: Place components in frontend folder, one per file
- **UI Requirements**: Use Material UI, Material React Table for all lists
- **Component Design**: Ensure responsive design, consistency, error handling

## Project Structure
- **Backend**: Django REST Framework with PostgreSQL database
  - **customers/**, **orders/**, **products/**, **services/**, **billing/**
  - **rules/**: Business logic for pricing and conditions
  - **inserts/**, **shipping/**, **materials/**, **bulk_operations/**
  
- **Frontend**: React with Material UI
  - **components/**: Organized by feature
  - **utils/**: Auth, API client, logger
  - State management with hooks, React Router v6, JWT auth

## API Structure
- RESTful endpoints with Django REST Framework
- JWT authentication with token refresh
- Custom exceptions in api/exceptions.py
- API client with auto token refresh in frontend/src/utils/apiClient.js

## Testing Requirements
- Unit, integration, security, contract, and performance tests
- Test all components in development server
- Verify responsive behavior across devices
- Test all interactive features and data display
- Validate edge cases and error handling
- Ensure appearance consistency across browsers

## Materialized Views
```bash
# Refresh all materialized views
python manage.py refresh_all_views
# With concurrent mode (minimal locking)
python manage.py refresh_all_views --concurrent
```

## Rules System
- BasicRule: Simple condition-based rules (field, operator, value)
- AdvancedRule: Complex with JSON conditions and calculations
- Supports case-based tiers with min/max ranges in tier_config
- Validate in frontend (AdvancedRuleBuilder.jsx) and backend (validators.py)