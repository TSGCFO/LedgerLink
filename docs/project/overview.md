# LedgerLink

> **Updated Testing Framework: March 2025**  
> We've implemented Docker-based and TestContainers-based testing frameworks for consistent and reliable test environments. See the [DOCKER_TESTING_SOLUTION.md](DOCKER_TESTING_SOLUTION.md) document for details.

A modern web application built with Django REST Framework and React with Material UI.

## Project Structure

```
LedgerLink/
├── backend/
│   ├── api/                 # Core API functionality
│   ├── customers/           # Customer management
│   ├── orders/             # Order management
│   ├── products/           # Product management
│   └── ...
└── frontend/
    ├── src/
    │   ├── components/     # React components
    │   ├── utils/          # Utility functions
    │   └── ...
    └── ...
```

## Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Apply migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at http://localhost:8000

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## API Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/docs/swagger/
- ReDoc: http://localhost:8000/docs/redoc/

## Features

### Backend
- RESTful API with Django REST Framework
- JWT Authentication
- Swagger/OpenAPI documentation
- CORS configuration
- Modular app structure
- Comprehensive test coverage

### Frontend
- Material UI components
- React Router for navigation
- Form validation
- Error handling
- Responsive design
- API client utility

## Development Workflow

1. Backend Development:
   - Create models in appropriate Django apps
   - Implement serializers and views
   - Add URL patterns
   - Write tests
   - Update API documentation

2. Frontend Development:
   - Create new components in `frontend/src/components`
   - Update routing in `App.jsx`
   - Use Material UI components for consistent design
   - Implement form validation
   - Handle API integration

## Available Scripts

### Backend
- `python manage.py test` - Run tests
- `python manage.py makemigrations` - Create new migrations
- `python manage.py migrate` - Apply migrations
- `python manage.py createsuperuser` - Create admin user

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint (in frontend directory)

### Project-level Scripts
- `npm run lint` - Run fullstack AI-powered linter (analyzes backend and frontend)
- `npm run lint:watch` - Run fullstack linter in watch mode
- `npm run lint:claude` - Run raw Claude AI analysis

See [LINTING.md](LINTING.md) for more details on our advanced linting capabilities.

## Testing with Docker

We've implemented a comprehensive Docker-based testing framework that ensures consistent and reliable test environments. This framework allows you to run tests for:

- The entire application
- Specific apps (customers, orders, etc.)
- Integration tests

### Setting Up Test Scripts

Make all test scripts executable:

```bash
./setup_test_scripts.sh
```

### Running Tests

Run all tests:
```bash
./run_docker_tests.sh
```

Run tests for a specific app:
```bash
./run_materials_tests.sh  # Materials app
./run_orders_tests.sh     # Orders app
./run_rules_tests.sh      # Rules app
# ... and others
```

For more details, see [DOCKER_TESTING_SOLUTION.md](DOCKER_TESTING_SOLUTION.md).

## Best Practices

1. Code Style:
   - Follow PEP 8 for Python code
   - Use ESLint for JavaScript/React code
   - Maintain consistent naming conventions
   - Use our AI-powered linter for cross-stack issues

2. Git Workflow:
   - Create feature branches
   - Write meaningful commit messages
   - Review code before merging
   - Pre-commit hooks will run linting automatically

3. Testing:
   - Write unit tests for new features
   - Use Docker testing environment for consistency
   - Run app-specific tests with `./run_<app>_tests.sh`
   - Maintain good test coverage
   - Test API endpoints thoroughly
   - Check [DOCKER_TESTING_SOLUTION.md](DOCKER_TESTING_SOLUTION.md) for Docker test setup

4. Documentation:
   - Keep API documentation up to date
   - Document complex functions and components
   - Update README as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential.

## Recent Important Changes

### Testing Framework Update - March 2025
We've implemented a Docker-based and TestContainers-based testing framework for consistent and reliable test environments. This update enables running tests with isolated PostgreSQL databases.

### Critical Bug Fix - March 2025
We've fixed a critical bug in the rule evaluation system where the "not equals" (`ne`) operator was not being evaluated correctly. This could have affected billing calculations and business logic decisions.

- See [CHANGELOG.md](CHANGELOG.md) for details on recent changes
- See [docs/RULE_OPERATORS.md](docs/RULE_OPERATORS.md) for comprehensive documentation on rule operators
- See [TODO.md](TODO.md) for the testing plan for this fix