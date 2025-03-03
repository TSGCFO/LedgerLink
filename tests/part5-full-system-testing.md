# Full-System Testing

This section focuses on testing the entire application from end to end, ensuring that the Django backend and React frontend work together seamlessly. Full-system testing simulates real user interactions and verifies that the complete application behaves as expected.

## Table of Contents

1. [End-to-End Testing with Cypress](#end-to-end-testing-with-cypress)
2. [API Contract Testing](#api-contract-testing)
3. [Load and Performance Testing](#load-and-performance-testing)
4. [Cross-Browser Testing](#cross-browser-testing)
5. [Monitoring and Real User Testing](#monitoring-and-real-user-testing)

## End-to-End Testing with Cypress

Cypress is a powerful tool for end-to-end testing that allows you to write tests that simulate user interactions with your application.

### Setting Up Cypress

First, let's set up Cypress for our project:

```bash
# Navigate to your project root
cd your-project

# Install Cypress
npm install --save-dev cypress cypress-file-upload
```

Initialize Cypress:

```bash
npx cypress open
```

This will create a `cypress` directory in your project with example tests and configuration.

Now, let's configure Cypress for our project. Create or update the `cypress.config.js` file:

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    chromeWebSecurity: false,
    defaultCommandTimeout: 10000,
    video: false,
    screenshotOnRunFailure: true
  },
});
```

### Writing End-to-End Tests

Let's create some Cypress tests for our task management application:

```javascript
// cypress/e2e/auth.cy.js
describe('Authentication', () => {
  beforeEach(() => {
    // Clear cookies and local storage before each test
    cy.clearCookies();
    cy.clearLocalStorage();
    
    // Visit the home page
    cy.visit('/');
  });
  
  it('redirects to login when not authenticated', () => {
    // Should be redirected to login page
    cy.url().should('include', '/login');
    cy.get('h1').should('contain', 'Login');
  });
  
  it('shows error message for invalid credentials', () => {
    // Try to login with invalid credentials
    cy.get('input[name="username"]').type('wronguser');
    cy.get('input[name="password"]').type('wrongpass');
    cy.get('form').submit();
    
    // Should show error message
    cy.get('[data-testid="login-error"]').should('be.visible');
    cy.get('[data-testid="login-error"]').should('contain', 'Invalid credentials');
    
    // Should still be on login page
    cy.url().should('include', '/login');
  });
  
  it('successfully logs in with valid credentials', () => {
    // Login with valid credentials
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('form').submit();
    
    // Should be redirected to tasks page
    cy.url().should('include', '/tasks');
    
    // Navbar should show logged in user
    cy.get('[data-testid="navbar-username"]').should('contain', 'testuser');
  });
  
  it('successfully logs out', () => {
    // Login first
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('form').submit();
    
    // Wait for login to complete
    cy.url().should('include', '/tasks');
    
    // Click logout button
    cy.get('[data-testid="logout-button"]').click();
    
    // Should be redirected to login page
    cy.url().should('include', '/login');
    
    // Try to access protected page
    cy.visit('/tasks');
    
    // Should be redirected to login again
    cy.url().should('include', '/login');
  });
});

// cypress/e2e/tasks.cy.js
describe('Task Management', () => {
  beforeEach(() => {
    // Login before each test
    cy.visit('/login');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('password123');
    cy.get('form').submit();
    
    // Wait for login to complete
    cy.url().should('include', '/tasks');
  });
  
  it('displays the task list', () => {
    // Should show task list heading
    cy.get('h1').should('contain', 'Your Tasks');
    
    // Should have tasks in the list
    cy.get('[data-testid="task-list"]').should('exist');
    cy.get('[data-testid="task-item"]').should('have.length.at.least', 1);
  });
  
  it('creates a new task', () => {
    // Click new task button
    cy.get('[data-testid="new-task-button"]').click();
    
    // Should navigate to task form
    cy.url().should('include', '/tasks/new');
    
    // Fill out the form
    const taskTitle = `Test Task ${Date.now()}`;
    cy.get('input[name="title"]').type(taskTitle);
    cy.get('textarea[name="description"]').type('This is a test task created by Cypress');
    
    // Set due date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const formattedDate = tomorrow.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    cy.get('input[name="due_date"]').type(formattedDate);
    
    // Select a status
    cy.get('select[name="status"]').select('in_progress');
    
    // Submit the form
    cy.get('form').submit();
    
    // Should be redirected to the task list
    cy.url().should('include', '/tasks');
    
    // New task should be in the list
    cy.get('[data-testid="task-item"]').contains(taskTitle).should('exist');
  });
  
  it('views task details', () => {
    // Click on the first task
    cy.get('[data-testid="task-item"]').first().click();
    
    // Should navigate to task detail page
    cy.url().should('include', '/tasks/');
    
    // Should show task details
    cy.get('[data-testid="task-detail"]').should('exist');
    cy.get('h1').should('exist'); // Task title
    cy.get('[data-testid="status-badge"]').should('exist');
    
    // Should have action buttons
    cy.get('[data-testid="toggle-button"]').should('exist');
    cy.get('[data-testid="edit-link"]').should('exist');
    cy.get('[data-testid="delete-button"]').should('exist');
  });
  
  it('edits a task', () => {
    // Click on the first task
    cy.get('[data-testid="task-item"]').first().click();
    
    // Click edit button
    cy.get('[data-testid="edit-link"]').click();
    
    // Should navigate to edit page
    cy.url().should('include', '/edit');
    
    // Update the title
    const updatedTitle = `Updated Task ${Date.now()}`;
    cy.get('input[name="title"]').clear().type(updatedTitle);
    
    // Submit the form
    cy.get('form').submit();
    
    // Should be redirected to task detail
    cy.url().should('include', '/tasks/');
    cy.url().should('not.include', '/edit');
    
    // Should show updated title
    cy.get('h1').should('contain', updatedTitle);
  });
  
  it('marks a task as complete', () => {
    // Find a pending task
    cy.get('[data-testid="task-item"]').not('.completed').first().click();
    
    // Check initial status
    cy.get('[data-testid="status-badge"]').then(($badge) => {
      const initialStatus = $badge.text().trim();
      
      // Click the toggle button
      cy.get('[data-testid="toggle-button"]').click();
      
      // Status should change
      cy.get('[data-testid="status-badge"]').should('not.have.text', initialStatus);
      
      if (initialStatus === 'pending' || initialStatus === 'in_progress') {
        cy.get('[data-testid="status-badge"]').should('have.text', 'completed');
        cy.get('[data-testid="toggle-button"]').should('contain', 'Mark Incomplete');
      } else {
        cy.get('[data-testid="status-badge"]').should('have.text', 'pending');
        cy.get('[data-testid="toggle-button"]').should('contain', 'Mark Complete');
      }
    });
  });
  
  it('deletes a task', () => {
    // Get count of tasks before deleting
    cy.get('[data-testid="task-item"]').then(($items) => {
      const initialCount = $items.length;
      
      // Click on the first task
      cy.get('[data-testid="task-item"]').first().click();
      
      // Get the task title for verification
      cy.get('h1').invoke('text').then((title) => {
        // Click delete button
        cy.get('[data-testid="delete-button"]').click();
        
        // Confirm delete in the dialog
        cy.on('window:confirm', () => true);
        
        // Should be redirected to task list
        cy.url().should('include', '/tasks');
        cy.url().should('not.include', '/tasks/');
        
        // Should have one less task
        cy.get('[data-testid="task-item"]').should('have.length', initialCount - 1);
        
        // Deleted task should not be in the list
        cy.get('[data-testid="task-item"]').contains(title).should('not.exist');
      });
    });
  });
  
  it('filters tasks by status', () => {
    // Go to dashboard or task list with filters
    cy.visit('/dashboard');
    
    // Select completed filter
    cy.get('[data-testid="status-filter"]').select('completed');
    
    // All visible tasks should have completed status
    cy.get('[data-testid="task-item"]').each(($task) => {
      cy.wrap($task).find('[data-testid="task-status"]').should('contain', 'completed');
    });
    
    // Select pending filter
    cy.get('[data-testid="status-filter"]').select('pending');
    
    // All visible tasks should have pending status
    cy.get('[data-testid="task-item"]').each(($task) => {
      cy.wrap($task).find('[data-testid="task-status"]').should('contain', 'pending');
    });
  });
});
```

### Creating Custom Cypress Commands

Let's create some custom commands to simplify our tests:

```javascript
// cypress/support/commands.js
// ***********************************************
// Custom commands for the task management app
// ***********************************************

// Login command
Cypress.Commands.add('login', (username = 'testuser', password = 'password123') => {
  cy.visit('/login');
  cy.get('input[name="username"]').type(username);
  cy.get('input[name="password"]').type(password);
  cy.get('form').submit();
  cy.url().should('include', '/tasks');
});

// Create task command
Cypress.Commands.add('createTask', (taskData = {}) => {
  const defaultData = {
    title: `Test Task ${Date.now()}`,
    description: 'This is a test task created by Cypress',
    status: 'pending',
    dueDate: (() => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      return tomorrow.toISOString().split('T')[0];
    })()
  };
  
  const data = { ...defaultData, ...taskData };
  
  cy.visit('/tasks/new');
  cy.get('input[name="title"]').type(data.title);
  cy.get('textarea[name="description"]').type(data.description);
  cy.get('input[name="due_date"]').type(data.dueDate);
  cy.get('select[name="status"]').select(data.status);
  cy.get('form').submit();
  cy.url().should('include', '/tasks');
  
  return cy.wrap(data);
});

// Delete all tasks command (useful for cleanup)
Cypress.Commands.add('deleteAllTasks', () => {
  cy.visit('/tasks');
  
  // Check if there are any tasks
  cy.get('body').then(($body) => {
    if ($body.find('[data-testid="task-item"]').length > 0) {
      // Click on each task and delete it
      cy.get('[data-testid="task-item"]').each(($task, index) => {
        // Need to re-query elements after each deletion to avoid stale references
        cy.get('[data-testid="task-item"]').first().click();
        cy.get('[data-testid="delete-button"]').click();
        cy.on('window:confirm', () => true);
        cy.url().should('include', '/tasks');
      });
    }
  });
});
```

Now let's refactor our task test using these custom commands:

```javascript
// cypress/e2e/tasks-improved.cy.js
describe('Task Management (Improved)', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
  });
  
  afterEach(() => {
    // Clean up tasks after tests
    cy.deleteAllTasks();
  });
  
  it('creates, views, edits, and deletes a task (full lifecycle)', () => {
    // Create a new task
    const taskTitle = `Lifecycle Test ${Date.now()}`;
    cy.createTask({
      title: taskTitle,
      description: 'This task will go through a complete lifecycle',
      status: 'pending'
    });
    
    // Verify task was created and click on it
    cy.get('[data-testid="task-item"]').contains(taskTitle).click();
    
    // Verify task details
    cy.get('h1').should('contain', taskTitle);
    cy.get('[data-testid="status-badge"]').should('contain', 'pending');
    
    // Edit the task
    cy.get('[data-testid="edit-link"]').click();
    const updatedTitle = `${taskTitle} - Updated`;
    cy.get('input[name="title"]').clear().type(updatedTitle);
    cy.get('select[name="status"]').select('in_progress');
    cy.get('form').submit();
    
    // Verify task was updated
    cy.get('h1').should('contain', updatedTitle);
    cy.get('[data-testid="status-badge"]').should('contain', 'in_progress');
    
    // Mark as complete
    cy.get('[data-testid="toggle-button"]').click();
    cy.get('[data-testid="status-badge"]').should('contain', 'completed');
    
    // Delete the task
    cy.get('[data-testid="delete-button"]').click();
    cy.on('window:confirm', () => true);
    
    // Verify redirected to task list
    cy.url().should('include', '/tasks');
    cy.url().should('not.include', '/tasks/');
    
    // Verify task was deleted
    cy.get('[data-testid="task-item"]').contains(updatedTitle).should('not.exist');
  });
});
```

### Running Cypress Tests

Add scripts to your `package.json` file:

```json
"scripts": {
  "cypress:open": "cypress open",
  "cypress:run": "cypress run",
  "test:e2e": "start-server-and-test start 3000 cypress:run"
}
```

To run the tests:

```bash
# Open Cypress interactive mode
npm run cypress:open

# Run Cypress tests headlessly
npm run cypress:run

# Start the app and run tests
npm run test:e2e
```

## API Contract Testing

API contract testing ensures that your frontend and backend communicate correctly according to a defined API contract. Pact is a popular tool for contract testing.

### Setting Up Pact

First, install Pact:

```bash
npm install --save-dev @pact-foundation/pact
```

### Writing Consumer Tests (Frontend)

Let's write a contract test for the frontend:

```javascript
// src/api/taskApi.pact.test.js
import { Pact } from '@pact-foundation/pact';
import { api } from './taskApi';
import path from 'path';

const mockPort = 8080;
const mockServer = `http://localhost:${mockPort}`;

// Configure the provider
const provider = new Pact({
  port: mockPort,
  log: path.resolve(process.cwd(), 'logs', 'pact.log'),
  dir: path.resolve(process.cwd(), 'pacts'),
  consumer: 'TaskManagerFrontend',
  provider: 'TaskManagerBackend'
});

describe('Task API', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  afterEach(() => provider.verify());
  
  describe('get all tasks', () => {
    // Define the expected interaction
    beforeEach(() => {
      return provider.addInteraction({
        state: 'tasks exist',
        uponReceiving: 'a request for all tasks',
        withRequest: {
          method: 'GET',
          path: '/api/tasks/',
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: [
            {
              id: 1,
              title: 'Test Task 1',
              description: 'Test Description 1',
              status: 'pending',
              due_date: '2023-12-31',
              created_at: '2023-01-01T00:00:00Z',
              updated_at: '2023-01-01T00:00:00Z'
            },
            {
              id: 2,
              title: 'Test Task 2',
              description: 'Test Description 2',
              status: 'completed',
              due_date: null,
              created_at: '2023-01-02T00:00:00Z',
              updated_at: '2023-01-02T00:00:00Z'
            }
          ]
        }
      });
    });
    
    test('returns all tasks', async () => {
      // Configure API to use mock server
      api.setBaseUrl(mockServer);
      
      // Call API method
      const tasks = await api.getTasks('valid-token');
      
      // Verify response
      expect(tasks).toHaveLength(2);
      expect(tasks[0].id).toEqual(1);
      expect(tasks[0].title).toEqual('Test Task 1');
      expect(tasks[1].id).toEqual(2);
      expect(tasks[1].title).toEqual('Test Task 2');
    });
  });
  
  describe('get task by id', () => {
    beforeEach(() => {
      return provider.addInteraction({
        state: 'a task with ID 1 exists',
        uponReceiving: 'a request for a task by ID',
        withRequest: {
          method: 'GET',
          path: '/api/tasks/1/',
          headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 1,
            title: 'Test Task 1',
            description: 'Test Description 1',
            status: 'pending',
            due_date: '2023-12-31',
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z'
          }
        }
      });
    });
    
    test('returns the specific task', async () => {
      api.setBaseUrl(mockServer);
      
      const task = await api.getTaskById(1, 'valid-token');
      
      expect(task.id).toEqual(1);
      expect(task.title).toEqual('Test Task 1');
      expect(task.status).toEqual('pending');
    });
  });
  
  describe('create a task', () => {
    const newTask = {
      title: 'New Task',
      description: 'New Task Description',
      status: 'pending',
      due_date: '2023-12-31'
    };
    
    beforeEach(() => {
      return provider.addInteraction({
        state: 'task can be created',
        uponReceiving: 'a request to create a task',
        withRequest: {
          method: 'POST',
          path: '/api/tasks/',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer valid-token'
          },
          body: newTask
        },
        willRespondWith: {
          status: 201,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 3,
            title: 'New Task',
            description: 'New Task Description',
            status: 'pending',
            due_date: '2023-12-31',
            created_at: '2023-01-03T00:00:00Z',
            updated_at: '2023-01-03T00:00:00Z'
          }
        }
      });
    });
    
    test('creates a new task', async () => {
      api.setBaseUrl(mockServer);
      
      const createdTask = await api.createTask(newTask, 'valid-token');
      
      expect(createdTask.id).toEqual(3);
      expect(createdTask.title).toEqual('New Task');
      expect(createdTask.status).toEqual('pending');
    });
  });
});
```

### Writing Provider Tests (Backend)

Now let's write the provider verification tests in Django:

```python
# tests/test_pact.py
import os
import json
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from pact_python.verifier import Verifier
from tasks.models import Task

User = get_user_model()

class PactVerifyTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create test tasks
        Task.objects.create(
            id=1,
            title='Test Task 1',
            description='Test Description 1',
            status='pending',
            due_date='2023-12-31',
            created_by=cls.user,
            assigned_to=cls.user
        )
        
        Task.objects.create(
            id=2,
            title='Test Task 2',
            description='Test Description 2',
            status='completed',
            created_by=cls.user,
            assigned_to=cls.user
        )
    
    def test_verify_pacts(self):
        # Path to the Pact file created by consumer
        pact_file = os.path.join(os.getcwd(), 'pacts', 'taskmanagerfrontend-taskmanagerbackend.json')
        
        # Verify the provider against the Pact file
        verifier = Verifier(
            provider='TaskManagerBackend',
            provider_base_url='http://localhost:8000',
            pact_files=[pact_file],
            provider_states_setup_url='http://localhost:8000/pact-provider-states',
            verbose=True
        )
        
        # Setup provider states
        with open(pact_file) as f:
            pact_content = json.load(f)
            
        # Create a special endpoint to handle provider states
        @classmethod
        def setup_provider_state(cls, state):
            if state == 'tasks exist':
                # Already set up in setUpClass
                pass
            elif state == 'a task with ID 1 exists':
                # Already set up in setUpClass
                pass
            elif state == 'task can be created':
                # No specific setup needed
                pass
        
        # Run the verification
        result = verifier.verify()
        
        # Check verification result
        assert result, "Pact verification failed"
```

Create a provider state endpoint in Django:

```python
# tasks/views.py (add this endpoint)
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def pact_provider_state(request):
    """
    Endpoint to handle provider states for Pact testing
    """
    state = request.data.get('state')
    
    # Handle different provider states
    if state == 'tasks exist':
        # Already set up in test case
        pass
    elif state == 'a task with ID 1 exists':
        # Already set up in test case
        pass
    elif state == 'task can be created':
        # No specific setup needed
        pass
    
    return Response({'state': state, 'setup': True})

# tasks/urls.py (add this URL)
from django.urls import path
from .views import pact_provider_state

urlpatterns = [
    # ... other URLs
    path('pact-provider-states', pact_provider_state, name='pact_provider_states'),
]
```

### Running Pact Tests

For the consumer (frontend):

```bash
jest src/api/taskApi.pact.test.js
```

For the provider (backend):

```bash
python manage.py test tests.test_pact
```

## Load and Performance Testing

Load testing ensures your application can handle the expected load and identifies performance bottlenecks.

### Using k6 for Load Testing

Let's set up k6 for load testing your API:

```bash
# Install k6
# For Windows: choco install k6
# For Mac: brew install k6
# For Linux: See https://k6.io/docs/getting-started/installation/
```

Create a load test script:

```javascript
// load-tests/task-api-load-test.js
import http from 'k6/http';
import { sleep, check } from 'k6';
import { Counter } from 'k6/metrics';

// Define metrics
const errors = new Counter('errors');

// Test configuration
export const options = {
  vus: 10, // 10 virtual users
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    'http_req_duration{type:static}': ['p(95)<100'], // 95% of static requests should be below 100ms
    errors: ['count<10'] // Error count should be less than 10
  }
};

// Login function to get token
function login() {
  const loginUrl = 'http://localhost:8000/api/auth/login/';
  const payload = JSON.stringify({
    username: 'testuser',
    password: 'password123'
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  const loginRes = http.post(loginUrl, payload, params);
  
  if (loginRes.status !== 200) {
    errors.add(1);
    return null;
  }
  
  return JSON.parse(loginRes.body).token;
}

// Main test function
export default function() {
  // Login to get token
  const token = login();
  
  if (!token) {
    console.log('Login failed, skipping requests');
    sleep(1);
    return;
  }
  
  // Set headers for authenticated requests
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  };
  
  // Test 1: Get all tasks
  const tasksRes = http.get('http://localhost:8000/api/tasks/', params);
  check(tasksRes, {
    'tasks status is 200': (r) => r.status === 200,
    'tasks response has data': (r) => r.json().length > 0
  });
  
  // Test 2: Get single task (assuming task ID 1 exists)
  const taskDetailRes = http.get('http://localhost:8000/api/tasks/1/', params);
  check(taskDetailRes, {
    'task detail status is 200': (r) => r.status === 200,
    'task has correct ID': (r) => r.json().id === 1
  });
  
  // Test 3: Create a new task
  const newTask = {
    title: `Load Test Task ${Date.now()}`,
    description: 'This is a task created during load testing',
    status: 'pending',
    due_date: '2023-12-31',
    assigned_to: 1 // Assuming user ID 1 exists
  };
  
  const createTaskRes = http.post(
    'http://localhost:8000/api/tasks/',
    JSON.stringify(newTask),
    params
  );
  
  check(createTaskRes, {
    'create task status is 201': (r) => r.status === 201,
    'created task has title': (r) => r.json().title.includes('Load Test Task')
  });
  
  // Short sleep between iterations
  sleep(1);
}
```

Run the load test:

```bash
k6 run load-tests/task-api-load-test.js
```

### Using Lighthouse for Frontend Performance Testing

Google Lighthouse can be used to analyze frontend performance:

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run Lighthouse audit
lighthouse http://localhost:3000 --view
```

## Cross-Browser Testing

Cross-browser testing ensures your application works correctly in different browsers.

### Using Cypress for Cross-Browser Testing

Cypress supports testing in different browsers:

```bash
# Run tests in Chrome
npx cypress run --browser chrome

# Run tests in Firefox
npx cypress run --browser firefox

# Run tests in Edge
npx cypress run --browser edge
```

### Using BrowserStack or Sauce Labs

For more comprehensive cross-browser testing, you can use services like BrowserStack or Sauce Labs.

Here's how to set up Cypress with BrowserStack:

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    // BrowserStack config
    browserstack: {
      username: process.env.BROWSERSTACK_USERNAME,
      accessKey: process.env.BROWSERSTACK_ACCESS_KEY,
      buildName: 'Task-Manager-Build',
      projectName: 'Task Manager App',
      debug: true,
      video: true,
      networkLogs: true
    }
  },
});
```

Add BrowserStack configuration file:

```json
// browserstack.json
{
  "browsers": [
    {
      "browser": "chrome",
      "os": "Windows 10",
      "versions": ["latest", "latest-1"]
    },
    {
      "browser": "firefox",
      "os": "Windows 10",
      "versions": ["latest"]
    },
    {
      "browser": "edge",
      "os": "Windows 10",
      "versions": ["latest"]
    },
    {
      "browser": "safari",
      "os": "OS X Monterey",
      "versions": ["latest"]
    }
  ]
}
```

Install the BrowserStack plugin:

```bash
npm install -D browserstack-cypress-cli
```

Run the tests on BrowserStack:

```bash
browserstack-cypress run --sync
```

## Monitoring and Real User Testing

Monitoring your application in production provides insights into real-world performance and issues.

### Setting Up Application Monitoring

You can use tools like Sentry for error tracking:

```javascript
// src/index.js (React)
import React from 'react';
import ReactDOM from 'react-dom';
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import App from './App';

// Initialize Sentry
Sentry.init({
  dsn: "https://your-sentry-dsn.ingest.sentry.io/project-id",
  integrations: [new BrowserTracing()],
  tracesSampleRate: 1.0, // Capture 100% of transactions in development
});

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
```

For Django:

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn.ingest.sentry.io/project-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0, # Capture 100% of transactions in development
    send_default_pii=True
)
```

### User Session Recording

For understanding how real users interact with your application, you can use tools like LogRocket or FullStory.

Integration with LogRocket:

```javascript
// src/index.js (React)
import LogRocket from 'logrocket';
LogRocket.init('your-app/your-project');

// Identify users
LogRocket.identify('user-id', {
  name: 'User Name',
  email: 'user@example.com',
});
```

### User Feedback Collection

You can collect user feedback using in-app surveys:

```javascript
// src/components/FeedbackWidget.jsx
import React, { useState } from 'react';

const FeedbackWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [rating, setRating] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Send feedback to backend
    await fetch('/api/feedback/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        rating,
        feedback
      })
    });
    
    setSubmitted(true);
    setTimeout(() => {
      setIsOpen(false);
      setSubmitted(false);
      setFeedback('');
      setRating(0);
    }, 3000);
  };
  
  return (
    <div className="feedback-widget">
      <button 
        className="feedback-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        Feedback
      </button>
      
      {isOpen && (
        <div className="feedback-form-container">
          {submitted ? (
            <div className="success-message">
              Thank you for your feedback!
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="feedback-form">
              <h3>How are we doing?</h3>
              
              <div className="rating-container">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    type="button"
                    className={`rating-button ${rating === value ? 'selected' : ''}`}
                    onClick={() => setRating(value)}
                  >
                    {value}
                  </button>
                ))}
              </div>
              
              <textarea
                placeholder="Your feedback (optional)"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={4}
              />
              
              <button type="submit" disabled={rating === 0}>
                Submit Feedback
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
};

export default FeedbackWidget;
```

## Combining All Testing Approaches

To ensure comprehensive testing coverage, you should integrate all these approaches into your development workflow:

### Test Strategy

1. **Continuous Testing**:
   - Unit and integration tests run on every commit
   - End-to-end tests run nightly or before deployments
   - Performance tests run weekly or before major releases

2. **Test Coverage Goals**:
   - Unit tests: 80%+ coverage
   - Integration tests: Cover all critical flows
   - E2E tests: Cover main user journeys
   - Performance tests: Meet defined performance SLAs

3. **Testing Hierarchy**:
   
   ```
   Production Monitoring
           ↑
   User Acceptance Testing
           ↑
   Cross-Browser Testing
           ↑
   End-to-End Testing
           ↑
   Performance Testing
           ↑
   API Contract Testing
           ↑
   Integration Testing
           ↑
   Unit Testing
   ```

### Sample CI/CD Pipeline

Here's a GitHub Actions workflow that integrates all testing approaches:

```yaml
# .github/workflows/full-test-pipeline.yml
name: Full Test Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # Unit and Integration Tests
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-django coverage
    
    - name: Run tests with coverage
      run: |
        coverage run -m pytest
        coverage report
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
  
  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run tests with coverage
      working-directory: ./frontend
      run: npm test -- --coverage --watchAll=false
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        directory: ./frontend
  
  # Contract Tests
  contract-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run Pact tests
      working-directory: ./frontend
      run: npm run test:pact
    
    - name: Upload Pact contracts
      uses: actions/upload-artifact@v3
      with:
        name: pact-contracts
        path: ./frontend/pacts/
  
  # End-to-End Tests
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [contract-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install backend dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Start backend server
      run: |
        python manage.py migrate
        python manage.py loaddata test_data.json
        python manage.py runserver &
        sleep 5  # Give the server time to start
    
    - name: Start frontend server
      working-directory: ./frontend
      run: |
        npm start &
        sleep 10  # Give the server time to start
    
    - name: Run Cypress tests
      working-directory: ./frontend
      run: npx cypress run
  
  # Performance Tests
  performance-tests:
    runs-on: ubuntu-latest
    needs: [e2e-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install k6
      run: |
        curl -L https://github.com/loadimpact/k6/releases/download/v0.33.0/k6-v0.33.0-linux-amd64.tar.gz | tar xzf -
        sudo cp k6-v0.33.0-linux-amd64/k6 /usr/local/bin
    
    - name: Start backend server
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        python manage.py migrate
        python manage.py loaddata test_data.json
        python manage.py runserver &
        sleep 5  # Give the server time to start
    
    - name: Run load tests
      run: k6 run load-tests/task-api-load-test.js
  
  # Lighthouse Performance Tests
  lighthouse-tests:
    runs-on: ubuntu-latest
    needs: [e2e-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start backend server
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        python manage.py migrate
        python manage.py loaddata test_data.json
        python manage.py runserver &
        sleep 5  # Give the server time to start
    
    - name: Start frontend server
      working-directory: ./frontend
      run: |
        npm ci
        npm start &
        sleep 10  # Give the server time to start
    
    - name: Run Lighthouse CI
      run: |
        npm install -g @lhci/cli@0.8.x
        lhci autorun
```

By implementing this comprehensive testing strategy, you'll ensure that your Django and React application is thoroughly tested at all levels, from individual components to the full system, resulting in a high-quality, reliable application.
