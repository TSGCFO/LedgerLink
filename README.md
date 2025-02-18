# LedgerLink

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
- `npm run lint` - Run ESLint

## Best Practices

1. Code Style:
   - Follow PEP 8 for Python code
   - Use ESLint for JavaScript/React code
   - Maintain consistent naming conventions

2. Git Workflow:
   - Create feature branches
   - Write meaningful commit messages
   - Review code before merging

3. Testing:
   - Write unit tests for new features
   - Maintain good test coverage
   - Test API endpoints thoroughly

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