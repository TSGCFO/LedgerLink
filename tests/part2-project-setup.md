# Setting Up Your Project for Testing

Before you can start writing effective tests, you need to configure your Django backend and React frontend properly. This section will walk you through the setup process step by step.

## Django Backend Setup

Django has built-in testing capabilities, but we'll enhance them with additional tools to make our testing more efficient and comprehensive.

### 1. Install Testing Dependencies

First, let's install the necessary packages:

```bash
# Create a virtual environment if you haven't already
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install testing packages
pip install pytest pytest-django factory-boy coverage

# Save dependencies to requirements file
pip freeze > requirements.txt
```

These packages serve the following purposes:

- **pytest**: A more powerful testing framework than Django's default
- **pytest-django**: Integrates pytest with Django
- **factory-boy**: Creates test data easily
- **coverage**: Measures how much of your code is tested

### 2. Configure pytest

Create a file named `pytest.ini` in your project root (where `manage.py` is located):

```ini
[pytest]
DJANGO_SETTINGS_MODULE = yourproject.settings.test
python_files = test_*.py *_test.py *_tests.py tests.py
python_classes = Test* *Test *Tests
python_functions = test_*
addopts = --strict-markers -v
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

This configuration:
- Tells pytest which files contain tests (any files starting with `test_` or ending with `_test.py`, `_tests.py`, or named `tests.py`)
- Defines custom markers to categorize tests
- Sets verbosity to show more details
- Specifies which Django settings module to use for tests

### 3. Create Test Settings

Create a dedicated settings file for tests. This keeps your test environment separate from development and production:

```python
# yourproject/settings/test.py
from .base import *  # Import your base settings

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use an in-memory SQLite database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for tests to run faster
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Set media directory for test uploads
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Set testing flag
TESTING = True
```

These settings optimize Django for testing:
- Using an in-memory database speeds up tests significantly
- Disabling migrations makes tests start faster
- Using a simple password hasher speeds up user creation

### 4. Create a Basic Test Structure

Organize your tests in a logical structure. For each Django app, you might have:

```
your_app/
├── tests/
│   ├── __init__.py
│   ├── factories.py        # Test data factories
│   ├── test_models.py      # Model tests
│   ├── test_views.py       # View tests
│   ├── test_forms.py       # Form tests
│   ├── test_api.py         # API tests
│   ├── test_utils.py       # Utility function tests
│   └── test_integration.py # Integration tests
```

Set up a basic test factories file:

```python
# your_app/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from your_app.models import YourModel

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True

class YourModelFactory(DjangoModelFactory):
    class Meta:
        model = YourModel
    
    name = factory.Sequence(lambda n: f'Object {n}')
    created_by = factory.SubFactory(UserFactory)
```

### 5. Set Up Coverage

Create a `.coveragerc` file in your project root to configure coverage reporting:

```ini
[run]
source = .
omit =
    */migrations/*
    */tests/*
    */venv/*
    */settings/*
    manage.py
    wsgi.py
    asgi.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if settings.DEBUG
    pass
    raise ImportError
```

This configuration excludes files you don't need to test and ignores common lines that don't need coverage.

### 6. Set Up a Test Command

Create a script to run all your tests with coverage:

```bash
# scripts/test.sh
#!/bin/bash
set -e

# Run tests with coverage
coverage run -m pytest "$@"

# Generate coverage report
coverage report -m

# Generate HTML coverage report
coverage html

echo "Coverage report generated in htmlcov/"
```

Make the script executable:

```bash
chmod +x scripts/test.sh
```

## React Frontend Setup

Now let's set up the React frontend for testing.

### 1. Install Testing Dependencies

If you used Create React App, many testing packages are already installed. Otherwise, install:

```bash
# Navigate to your React project
cd frontend

# Install testing packages
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event msw jest-environment-jsdom
```

These packages provide:
- **@testing-library/react**: Tools for testing React components
- **@testing-library/jest-dom**: Custom DOM element matchers for Jest
- **@testing-library/user-event**: Simulates user events like clicks and typing
- **msw**: Mock Service Worker for API mocking
- **jest-environment-jsdom**: DOM environment for Jest

### 2. Configure Jest

Create or update your Jest configuration in `package.json`:

```json
"jest": {
  "moduleNameMapper": {
    "^@/(.*)$": "<rootDir>/src/$1"
  },
  "setupFilesAfterEnv": [
    "<rootDir>/src/setupTests.js"
  ],
  "testEnvironment": "jsdom",
  "transform": {
    "^.+\\.[t|j]sx?$": "babel-jest"
  },
  "collectCoverageFrom": [
    "src/**/*.{js,jsx,ts,tsx}",
    "!src/**/*.d.ts",
    "!src/index.tsx",
    "!src/serviceWorker.ts",
    "!src/reportWebVitals.ts"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 70,
      "functions": 70,
      "lines": 70,
      "statements": 70
    }
  }
}
```

This configuration:
- Sets up module path aliases
- Specifies a setup file for tests
- Uses the JSDOM environment for testing
- Configures Babel for transpilation
- Sets coverage collection paths
- Defines coverage thresholds (70% is a good starting point)

### 3. Create a Test Setup File

Create or update `src/setupTests.js`:

```javascript
// Import Jest DOM matchers
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Silence console errors we expect in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (/Warning.*not wrapped in act/.test(args[0]) ||
        /Warning.*Cannot update a component/.test(args[0])) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Setting up a global fetch mock reset
global.fetch = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
});
```

This setup file:
- Adds Jest DOM matchers for assertions like `toBeInTheDocument()`
- Mocks `window.matchMedia` (often needed for components that use media queries)
- Silences certain expected React warnings in tests
- Sets up global fetch mocking

### 4. Set Up Mock Service Worker

Create API mocks using Mock Service Worker:

```javascript
// src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  // Mock GET /api/tasks
  rest.get('/api/tasks', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, title: 'Mock Task 1', completed: false },
        { id: 2, title: 'Mock Task 2', completed: true }
      ])
    );
  }),
  
  // Mock POST /api/tasks
  rest.post('/api/tasks', async (req, res, ctx) => {
    const { title, description } = await req.json();
    return res(
      ctx.status(201),
      ctx.json({
        id: Date.now(),
        title,
        description,
        completed: false
      })
    );
  }),
  
  // Add more API mocks here...
];

// src/mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Set up MSW server
export const server = setupServer(...handlers);
```

Update your `setupTests.js` to include the MSW server:

```javascript
// Add to setupTests.js
import { server } from './mocks/server';

// Start server before all tests
beforeAll(() => server.listen());

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Close server after all tests
afterAll(() => server.close());
```

### 5. Create a Test Utilities File

Create a file with common test utilities:

```javascript
// src/test-utils.js
import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import rootReducer from './redux/reducers';

// Create a custom render function that includes providers
export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    store = configureStore({ reducer: rootReducer, preloadedState }),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <Provider store={store}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </Provider>
    );
  }
  
  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

// Helper to wait for a condition
export async function waitForCondition(condition, timeout = 1000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (condition()) return true;
    await new Promise(r => setTimeout(r, 10));
  }
  throw new Error('Condition not met within timeout');
}
```

### 6. Create Component Test Structure

Organize your React tests alongside your components:

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.test.jsx
│   │   └── index.js
│   ├── TaskList/
│   │   ├── TaskList.jsx
│   │   ├── TaskList.test.jsx
│   │   └── index.js
```

### 7. Set Up a Test Script

Add test scripts to your `package.json`:

```json
"scripts": {
  "test": "react-scripts test",
  "test:coverage": "react-scripts test --coverage --watchAll=false",
  "test:ci": "CI=true react-scripts test --coverage"
}
```

## Setting Up End-to-End Testing with Cypress

End-to-end tests verify your entire application works together. Let's set up Cypress for this:

### 1. Install Cypress

```bash
cd frontend
npm install --save-dev cypress cypress-file-upload
```

### 2. Initialize Cypress

```bash
npx cypress open
```

This will create a `cypress` directory with example tests.

### 3. Configure Cypress

Update `cypress.json` in your project root:

```json
{
  "baseUrl": "http://localhost:3000",
  "viewportWidth": 1280,
  "viewportHeight": 720,
  "video": false,
  "chromeWebSecurity": false,
  "defaultCommandTimeout": 10000,
  "integrationFolder": "cypress/e2e",
  "testFiles": "**/*.spec.js"
}
```

### 4. Create a Basic E2E Test

```javascript
// cypress/e2e/authentication.spec.js
describe('Authentication', () => {
  beforeEach(() => {
    // Visit the home page before each test
    cy.visit('/');
  });
  
  it('should allow a user to log in', () => {
    // Intercept the login API call
    cy.intercept('POST', '/api/auth/login').as('loginRequest');
    
    // Click the login button
    cy.contains('Login').click();
    
    // Fill out the login form
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for the login request to complete
    cy.wait('@loginRequest');
    
    // Verify the user is logged in
    cy.contains('Welcome, testuser').should('be.visible');
    cy.url().should('include', '/dashboard');
  });
});
```

### 5. Add Cypress Scripts

Add Cypress scripts to your `package.json`:

```json
"scripts": {
  "cypress:open": "cypress open",
  "cypress:run": "cypress run",
  "test:e2e": "start-server-and-test start 3000 cypress:run"
}
```

Install the helper package:

```bash
npm install --save-dev start-server-and-test
```

## Integrating Testing into Your Development Workflow

Now that you've set up testing for both your Django backend and React frontend, let's integrate it into your development workflow:

### 1. Create a Pre-Commit Hook

Install pre-commit:

```bash
pip install pre-commit
```

Create a `.pre-commit-config.yaml` file:

```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: local
    hooks:
    -   id: django-tests
        name: Django Tests
        entry: python manage.py test
        language: system
        pass_filenames: false
        types: [python]
        files: ^yourapp/
```

Install the pre-commit hooks:

```bash
pre-commit install
```

### 2. Create a Test Script for Your Entire Project

Create a script that runs all tests:

```bash
# scripts/run-all-tests.sh
#!/bin/bash
set -e

echo "Running Django backend tests..."
cd /path/to/your/django/project
python manage.py test

echo "Running React frontend tests..."
cd /path/to/your/react/project
npm test -- --watchAll=false

echo "Running end-to-end tests..."
npm run test:e2e

echo "All tests passed!"
```

Make the script executable:

```bash
chmod +x scripts/run-all-tests.sh
```

## Next Steps

Now that your testing environment is set up, you're ready to start writing actual tests. In the next sections, we'll explore how to write effective tests for your Django models, views, and APIs, and for your React components and state management.

Remember, setting up a good testing environment takes time, but pays huge dividends in the long run. With this foundation in place, you'll be able to develop with confidence and ensure your application remains stable and reliable as it grows.
