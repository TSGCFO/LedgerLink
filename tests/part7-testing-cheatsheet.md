# Testing Cheatsheet and Quick Reference

This cheatsheet provides a quick reference for testing your Django and React application. Use it as a go-to resource when writing tests.

## Django Testing Quick Reference

### Setting Up Tests

```python
# Basic TestCase
from django.test import TestCase

class MyModelTests(TestCase):
    def setUp(self):
        # Setup code runs before each test
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
    
    def tearDown(self):
        # Cleanup code runs after each test
        pass
    
    def test_something(self):
        # Test code here
        self.assertEqual(1 + 1, 2)
```

### Factory Boy Examples

```python
# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='pending')
    due_date = models.DateField(null=True, blank=True)

# factories.py
import factory
import factory.fuzzy
from django.utils import timezone
from factory.django import DjangoModelFactory
from datetime import timedelta
from .models import User, Project, Task

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project
    
    name = factory.Sequence(lambda n: f'Project {n}')
    owner = factory.SubFactory(UserFactory)
    is_public = factory.Faker('boolean', chance_of_getting_true=25)

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
    
    title = factory.Sequence(lambda n: f'Task {n}')
    description = factory.Faker('paragraph')
    project = factory.SubFactory(ProjectFactory)
    assigned_to = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(['pending', 'in_progress', 'completed'])
    
    # Use traits for special cases
    class Params:
        overdue = factory.Trait(
            due_date=factory.LazyFunction(
                lambda: timezone.now().date() - timedelta(days=1)
            )
        )
        due_soon = factory.Trait(
            due_date=factory.LazyFunction(
                lambda: timezone.now().date() + timedelta(days=1)
            )
        )
        completed = factory.Trait(
            status='completed'
        )
```

### Common Django Test Assertions

```python
# Basic assertions
self.assertEqual(a, b)
self.assertNotEqual(a, b)
self.assertTrue(x)
self.assertFalse(x)
self.assertIsNone(x)
self.assertIsNotNone(x)
self.assertIn(a, b)  # b contains a
self.assertNotIn(a, b)

# Django-specific assertions
self.assertRedirects(response, '/expected/url/')
self.assertContains(response, 'Expected text')
self.assertNotContains(response, 'Unexpected text')
self.assertTemplateUsed(response, 'template_name.html')
self.assertFormError(response, 'form_name', 'field_name', 'error message')
self.assertQuerysetEqual(qs1, qs2)
```

### Testing Views

```python
# Function-based view test
def test_task_list_view(self):
    # Login if needed
    self.client.login(username='testuser', password='password123')
    
    # Request the page
    url = reverse('task_list')
    response = self.client.get(url)
    
    # Check response
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'tasks/task_list.html')
    self.assertContains(response, 'Task List')
    
    # Check context
    tasks = response.context['tasks']
    self.assertEqual(tasks.count(), 3)

# Test form submission
def test_task_create_view(self):
    self.client.login(username='testuser', password='password123')
    
    # Submit form data
    url = reverse('task_create')
    form_data = {
        'title': 'New Task',
        'description': 'Task description',
        'project': 1,
        'assigned_to': 1,
        'status': 'pending'
    }
    response = self.client.post(url, form_data)
    
    # Check redirect
    self.assertRedirects(response, reverse('task_detail', args=[1]))
    
    # Check object was created
    self.assertTrue(Task.objects.filter(title='New Task').exists())
```

### Testing APIs

```python
# DRF API test
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.task = TaskFactory(assigned_to=self.user)
        self.url = reverse('api:task-list')
    
    def test_get_task_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_task(self):
        data = {
            'title': 'API Test Task',
            'project': self.task.project.id,
            'status': 'pending'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
```

### Mocking in Django Tests

```python
from unittest.mock import patch, MagicMock

# Mock a function
@patch('myapp.services.external_api.get_data')
def test_api_integration(self, mock_get_data):
    mock_get_data.return_value = {'key': 'value'}
    
    result = process_external_data()
    
    self.assertEqual(result, 'Processed: value')
    mock_get_data.assert_called_once()

# Mock a class
@patch('myapp.services.PaymentGateway')
def test_payment_processing(self, MockGateway):
    # Configure the mock
    mock_gateway = MockGateway.return_value
    mock_gateway.process_payment.return_value = {'status': 'success'}
    
    payment = Payment(amount=100)
    result = payment.process()
    
    self.assertEqual(result, 'success')
    mock_gateway.process_payment.assert_called_with(100)
```

### Testing Permissions

```python
def test_permission_denied(self):
    # Create users with different roles
    user1 = UserFactory()
    user2 = UserFactory()
    
    # Create object owned by user1
    project = ProjectFactory(owner=user1)
    
    # Login as user2
    self.client.force_login(user2)
    
    # Try to access user1's project
    url = reverse('project_edit', args=[project.id])
    response = self.client.get(url)
    
    # Should be forbidden
    self.assertEqual(response.status_code, 403)
```

### Running Specific Django Tests

```bash
# Run all tests
python manage.py test

# Run tests in a specific app
python manage.py test myapp

# Run a specific test class
python manage.py test myapp.tests.TestClassName

# Run a specific test method
python manage.py test myapp.tests.TestClassName.test_method_name

# With pytest
pytest myapp/tests/test_views.py::TestClass::test_method -v
```

## React Testing Quick Reference

### Setting Up Tests

```javascript
// Basic component test
import React from 'react';
import { render, screen } from '@testing-library/react';
import Button from './Button';

describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
```

### Common React Test Queries

```javascript
// Finding elements
screen.getByText('Hello world');  // Find by text content
screen.getByRole('button');  // Find by ARIA role
screen.getByRole('button', { name: 'Submit' });  // Find button with specific text
screen.getByLabelText('Username');  // Find form element by label
screen.getByPlaceholderText('Enter username');  // Find by placeholder
screen.getByTestId('submit-button');  // Find by data-testid attribute

// Variations
screen.queryByText('Not in DOM');  // Returns null if not found
screen.findByText('Async Text');  // Returns promise, for async content
screen.getAllByRole('listitem');  // Returns array of all matches
```

### User Event Simulation

```javascript
import userEvent from '@testing-library/user-event';

// Clicking
userEvent.click(screen.getByRole('button'));

// Typing
userEvent.type(screen.getByLabelText('Username'), 'testuser');

// Select dropdown
userEvent.selectOptions(screen.getByLabelText('Country'), 'Canada');

// Checkbox
userEvent.click(screen.getByLabelText('Accept terms'));

// Advanced keyboard interaction
userEvent.tab();  // Press Tab key
userEvent.keyboard('{Shift>}Hello{/Shift}');  // Type with Shift key held
```

### Common React Test Assertions

```javascript
// Element presence
expect(element).toBeInTheDocument();
expect(element).not.toBeInTheDocument();

// Visibility
expect(element).toBeVisible();
expect(element).not.toBeVisible();

// Element attributes
expect(element).toHaveAttribute('href', '/home');
expect(element).toHaveClass('active');
expect(element).toBeDisabled();
expect(element).toBeEnabled();
expect(element).toBeChecked();  // For checkboxes

// Form values
expect(element).toHaveValue('test input');
expect(element).toHaveDisplayValue('Test');

// Text content
expect(element).toHaveTextContent('Hello world');
expect(element).not.toHaveTextContent('Error');

// Focus state
expect(element).toHaveFocus();

// Style
expect(element).toHaveStyle({ color: 'red' });
```

### Testing Forms

```javascript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from './LoginForm';

describe('LoginForm', () => {
  test('submits form with user data', () => {
    const handleSubmit = jest.fn();
    render(<LoginForm onSubmit={handleSubmit} />);
    
    // Fill out form
    userEvent.type(screen.getByLabelText(/username/i), 'testuser');
    userEvent.type(screen.getByLabelText(/password/i), 'password123');
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /log in/i }));
    
    // Check that submit handler was called with correct data
    expect(handleSubmit).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123'
    });
  });
  
  test('shows validation error for empty username', () => {
    const handleSubmit = jest.fn();
    render(<LoginForm onSubmit={handleSubmit} />);
    
    // Submit without filling username
    userEvent.type(screen.getByLabelText(/password/i), 'password123');
    fireEvent.click(screen.getByRole('button', { name: /log in/i }));
    
    // Check for error message
    expect(screen.getByText(/username is required/i)).toBeInTheDocument();
    
    // Should not call submit handler
    expect(handleSubmit).not.toHaveBeenCalled();
  });
});
```

### Testing API Calls

```javascript
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskList from './TaskList';

// Mock fetch globally
global.fetch = jest.fn();

describe('TaskList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('loads and displays tasks', async () => {
    const mockTasks = [
      { id: 1, title: 'Task 1', status: 'pending' },
      { id: 2, title: 'Task 2', status: 'completed' }
    ];
    
    // Mock successful fetch
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks
    });
    
    render(<TaskList />);
    
    // Should show loading initially
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
    
    // Should display tasks
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
    
    // Check fetch was called
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks');
  });
  
  test('handles error state', async () => {
    // Mock failed fetch
    global.fetch.mockRejectedValueOnce(new Error('API error'));
    
    render(<TaskList />);
    
    // Wait for error
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

### Testing Hooks

```javascript
import { renderHook, act } from '@testing-library/react-hooks';
import useCounter from './useCounter';

describe('useCounter', () => {
  test('initial value starts at 0 by default', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });
  
  test('can specify initial value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });
  
  test('increment increases count by 1', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
  
  test('decrement decreases count by 1', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });
});
```

### Testing Redux

```javascript
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import { fetchTasks, addTask } from './taskActions';

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock fetch API
global.fetch = jest.fn();

describe('Task Actions', () => {
  let store;
  
  beforeEach(() => {
    store = mockStore({
      tasks: {
        items: [],
        loading: false,
        error: null
      }
    });
    
    jest.clearAllMocks();
  });
  
  test('fetchTasks creates FETCH_TASKS_SUCCESS when fetching tasks succeeds', async () => {
    const mockTasks = [{ id: 1, title: 'Task 1' }];
    
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks
    });
    
    const expectedActions = [
      { type: 'FETCH_TASKS_REQUEST' },
      { type: 'FETCH_TASKS_SUCCESS', payload: mockTasks }
    ];
    
    await store.dispatch(fetchTasks());
    
    const actualActions = store.getActions();
    expect(actualActions[0].type).toEqual(expectedActions[0].type);
    expect(actualActions[1].type).toEqual(expectedActions[1].type);
    expect(actualActions[1].payload).toEqual(expectedActions[1].payload);
  });
  
  test('fetchTasks creates FETCH_TASKS_FAILURE when fetching tasks fails', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    
    const expectedActions = [
      { type: 'FETCH_TASKS_REQUEST' },
      { type: 'FETCH_TASKS_FAILURE', payload: 'Network error' }
    ];
    
    await store.dispatch(fetchTasks());
    
    const actualActions = store.getActions();
    expect(actualActions[0].type).toEqual(expectedActions[0].type);
    expect(actualActions[1].type).toEqual(expectedActions[1].type);
    expect(actualActions[1].payload).toEqual(expectedActions[1].payload);
  });
});
```

### Testing Context

```javascript
import React, { useContext } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeContext, ThemeProvider } from './ThemeContext';

// Component that uses context
const ThemedButton = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  return (
    <button 
      onClick={toggleTheme}
      style={{ 
        backgroundColor: theme === 'dark' ? '#333' : '#fff',
        color: theme === 'dark' ? '#fff' : '#333'
      }}
    >
      Current theme: {theme}
    </button>
  );
};

describe('ThemeContext', () => {
  test('provides default theme value', () => {
    render(
      <ThemeProvider>
        <ThemedButton />
      </ThemeProvider>
    );
    
    expect(screen.getByRole('button')).toHaveTextContent('Current theme: light');
  });
  
  test('can toggle theme', () => {
    render(
      <ThemeProvider>
        <ThemedButton />
      </ThemeProvider>
    );
    
    const button = screen.getByRole('button');
    
    // Initial theme is light
    expect(button).toHaveTextContent('Current theme: light');
    
    // Click to toggle theme
    userEvent.click(button);
    expect(button).toHaveTextContent('Current theme: dark');
    
    // Click again to toggle back
    userEvent.click(button);
    expect(button).toHaveTextContent('Current theme: light');
  });
});
```

### Running React Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- Button.test.js

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

## Cypress End-to-End Testing Quick Reference

### Basic Cypress Test

```javascript
// cypress/e2e/login.spec.js
describe('Login', () => {
  beforeEach(() => {
    // Visit the login page before each test
    cy.visit('/login');
  });
  
  it('successfully logs in with valid credentials', () => {
    // Fill out login form
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    
    // Submit form
    cy.get('form').submit();
    
    // Verify user is logged in and redirected to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="welcome-message"]').should('contain', 'Welcome, testuser');
  });
  
  it('shows error message with invalid credentials', () => {
    // Fill out form with invalid credentials
    cy.get('input[name="username"]').type('wronguser');
    cy.get('input[name="password"]').type('wrongpass');
    
    // Submit form
    cy.get('form').submit();
    
    // Verify error message is shown
    cy.get('[data-testid="login-error"]').should('be.visible');
    cy.get('[data-testid="login-error"]').should('contain', 'Invalid credentials');
    
    // Verify URL is still login page
    cy.url().should('include', '/login');
  });
});
```

### Common Cypress Commands

```javascript
// Navigation
cy.visit('/about');  // Visit page
cy.go('back');  // Navigate back
cy.reload();  // Reload page

// Finding elements
cy.get('button');  // CSS selector
cy.get('[data-testid="submit"]');  // By test ID
cy.contains('Submit');  // By text content
cy.contains('button', 'Submit');  // By tag and text

// Actions
cy.get('button').click();  // Click
cy.get('input').type('Hello');  // Type text
cy.get('input').clear();  // Clear input
cy.get('form').submit();  // Submit form
cy.get('select').select('Option 1');  // Select dropdown
cy.get('input[type="checkbox"]').check();  // Check checkbox
cy.get('input[type="checkbox"]').uncheck();  // Uncheck checkbox

// Assertions
cy.get('button').should('be.visible');
cy.get('button').should('contain', 'Submit');
cy.get('button').should('have.class', 'primary');
cy.get('input').should('have.value', 'test');
cy.get('p').should('have.css', 'color', 'rgb(255, 0, 0)');
cy.url().should('include', '/dashboard');

// Multiple assertions
cy.get('button').should('be.visible').and('contain', 'Submit');

// Wait for elements
cy.get('button', { timeout: 10000 });  // Increase timeout (default 4000ms)
cy.get('button').should('exist');  // Wait for element to exist
```

### Custom Cypress Commands

```javascript
// cypress/support/commands.js
// Login command
Cypress.Commands.add('login', (username = 'testuser', password = 'password123') => {
  cy.visit('/login');
  cy.get('input[name="username"]').type(username);
  cy.get('input[name="password"]').type(password);
  cy.get('form').submit();
  cy.url().should('include', '/dashboard');
});

// Create task command
Cypress.Commands.add('createTask', (title = 'Test Task') => {
  cy.visit('/tasks/new');
  cy.get('input[name="title"]').type(title);
  cy.get('button[type="submit"]').click();
});

// Usage in tests
it('creates a new task', () => {
  cy.login();  // Use custom login command
  cy.createTask('My New Task');  // Use custom task creation command
  
  // Verify task was created
  cy.get('[data-testid="task-list"]').should('contain', 'My New Task');
});
```

### API Mocking with Cypress

```javascript
// Mock API response
it('displays tasks from API', () => {
  // Intercept API call and return mock data
  cy.intercept('GET', '/api/tasks', {
    statusCode: 200,
    body: [
      { id: 1, title: 'Mocked Task 1', status: 'pending' },
      { id: 2, title: 'Mocked Task 2', status: 'completed' }
    ]
  }).as('getTasks');
  
  // Visit the page
  cy.visit('/tasks');
  
  // Wait for API call to complete
  cy.wait('@getTasks');
  
  // Verify tasks are displayed
  cy.contains('Mocked Task 1').should('be.visible');
  cy.contains('Mocked Task 2').should('be.visible');
});

// Spy on actual API call
it('makes the correct API call', () => {
  // Intercept without mocking response
  cy.intercept('POST', '/api/tasks').as('createTask');
  
  // Create a task
  cy.visit('/tasks/new');
  cy.get('input[name="title"]').type('New Task');
  cy.get('button[type="submit"]').click();
  
  // Verify API call was made with correct data
  cy.wait('@createTask').its('request.body').should('deep.include', {
    title: 'New Task'
  });
});
```

### Cypress Test Organization

```javascript
// Typical test structure
describe('Task Management', () => {
  beforeEach(() => {
    // Setup common to all tests
    cy.login();
  });
  
  context('Task List', () => {
    beforeEach(() => {
      // Setup specific to task list tests
      cy.visit('/tasks');
    });
    
    it('displays all tasks', () => {
      // Test code
    });
    
    it('can filter tasks by status', () => {
      // Test code
    });
  });
  
  context('Task Creation', () => {
    beforeEach(() => {
      // Setup specific to task creation tests
      cy.visit('/tasks/new');
    });
    
    it('can create a task', () => {
      // Test code
    });
    
    it('validates required fields', () => {
      // Test code
    });
  });
});
```

### Running Cypress Tests

```bash
# Open Cypress Test Runner
npx cypress open

# Run tests headlessly
npx cypress run

# Run specific test file
npx cypress run --spec "cypress/e2e/login.spec.js"

# Run tests in a specific browser
npx cypress run --browser chrome
```

## Common Testing Patterns

### Testing Authentication

```javascript
// Cypress
describe('Protected Routes', () => {
  it('redirects to login when not authenticated', () => {
    // Try to access protected page
    cy.visit('/dashboard');
    
    // Should redirect to login
    cy.url().should('include', '/login');
  });
  
  it('allows access when authenticated', () => {
    // Login first
    cy.login();
    
    // Try to access protected page
    cy.visit('/dashboard');
    
    // Should not redirect
    cy.url().should('include', '/dashboard');
  });
});

// React Component Test
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from './AuthContext';
import PrivateRoute from './PrivateRoute';

test('redirects to login when not authenticated', () => {
  const mockNavigate = jest.fn();
  jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate
  }));
  
  render(
    <AuthContext.Provider value={{ isAuthenticated: false }}>
      <BrowserRouter>
        <PrivateRoute>
          <div>Protected Content</div>
        </PrivateRoute>
      </BrowserRouter>
    </AuthContext.Provider>
  );
  
  expect(mockNavigate).toHaveBeenCalledWith('/login');
  expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
});
```

### Testing Forms

```javascript
// React form validation test
test('validates required fields', () => {
  render(<TaskForm onSubmit={mockSubmit} />);
  
  // Submit without filling required fields
  fireEvent.click(screen.getByRole('button', { name: /submit/i }));
  
  // Check for error messages
  expect(screen.getByText(/title is required/i)).toBeInTheDocument();
  
  // Fill in a field
  userEvent.type(screen.getByLabelText(/title/i), 'Test Task');
  
  // Error should be cleared
  expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
});

// Django form test
def test_task_form_validation(self):
    form = TaskForm(data={})  # Empty data
    
    # Form should not be valid
    self.assertFalse(form.is_valid())
    
    # Should have error for required fields
    self.assertIn('title', form.errors)
    
    # Partial data
    form = TaskForm(data={'title': 'Test Task'})
    
    # Still invalid without project
    self.assertFalse(form.is_valid())
    self.assertIn('project', form.errors)
```

### Testing Asynchronous Code

```javascript
// Testing promises
test('async function returns correct data', async () => {
  // Mock API
  jest.spyOn(api, 'fetchData').mockResolvedValue({ result: 'success' });
  
  // Call async function
  const result = await processData();
  
  // Verify result
  expect(result).toEqual({ processed: 'success' });
});

// Testing loading states
test('shows loading state while fetching data', async () => {
  // Mock slow API
  jest.spyOn(api, 'fetchData').mockImplementation(() => {
    return new Promise(resolve => {
      setTimeout(() => resolve({ data: 'test' }), 100);
    });
  });
  
  render(<DataComponent />);
  
  // Should show loading initially
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  // Should eventually show data
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    expect(screen.getByText('test')).toBeInTheDocument();
  });
});
```

### Testing Error Handling

```javascript
// React error test
test('shows error message when API fails', async () => {
  // Mock API error
  jest.spyOn(api, 'fetchData').mockRejectedValue(new Error('API Error'));
  
  render(<DataComponent />);
  
  // Should show error
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument();
    expect(screen.getByText(/API Error/i)).toBeInTheDocument();
  });
});

// Django error test
def test_handle_invalid_data(self):
    # Invalid JSON data
    url = reverse('api:task-list')
    response = self.client.post(
        url,
        data='{"invalid": json',
        content_type='application/json'
    )
    
    # Should return 400 Bad Request
    self.assertEqual(response.status_code, 400)
```

This cheatsheet covers the most common testing patterns and commands you'll need when testing your Django and React application. Keep it handy as a quick reference when writing tests.
