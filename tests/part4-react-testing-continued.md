# React Frontend Testing (Continued)

## Form Testing (continued)

Let's continue with the `TaskForm` component and its tests:

```jsx
// src/components/TaskForm/TaskForm.jsx (continued)
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onAddTask(formData);
      
      // Reset form if not editing
      if (!initialValues.id) {
        setFormData({
          title: '',
          description: '',
          due_date: '',
          status: 'pending'
        });
      }
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="task-form" data-testid="task-form">
      <div className="form-group">
        <label htmlFor="title">
          Title <span className="required">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          data-testid="title-input"
          className={errors.title ? 'error' : ''}
        />
        {errors.title && (
          <div className="error-message" data-testid="title-error">
            {errors.title}
          </div>
        )}
      </div>
      
      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          data-testid="description-input"
          rows={4}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="due_date">Due Date</label>
        <input
          type="date"
          id="due_date"
          name="due_date"
          value={formData.due_date}
          onChange={handleChange}
          data-testid="due-date-input"
          className={errors.due_date ? 'error' : ''}
        />
        {errors.due_date && (
          <div className="error-message" data-testid="due-date-error">
            {errors.due_date}
          </div>
        )}
      </div>
      
      <div className="form-group">
        <label htmlFor="status">Status</label>
        <select
          id="status"
          name="status"
          value={formData.status}
          onChange={handleChange}
          data-testid="status-input"
        >
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      <button type="submit" data-testid="submit-button">
        {initialValues.id ? 'Update Task' : 'Add Task'}
      </button>
    </form>
  );
};

export default TaskForm;
```

Now let's write tests for this form component:

```jsx
// src/components/TaskForm/TaskForm.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import TaskForm from './TaskForm';

describe('TaskForm Component', () => {
  const mockAddTask = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders form with empty values', () => {
    render(<TaskForm onAddTask={mockAddTask} />);
    
    // Check form elements exist
    expect(screen.getByLabelText(/Title/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Due Date/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Status/)).toBeInTheDocument();
    expect(screen.getByTestId('submit-button')).toHaveTextContent('Add Task');
    
    // Check initial values
    expect(screen.getByTestId('title-input')).toHaveValue('');
    expect(screen.getByTestId('description-input')).toHaveValue('');
    expect(screen.getByTestId('due-date-input')).toHaveValue('');
    expect(screen.getByTestId('status-input')).toHaveValue('pending');
  });
  
  test('renders form with initial values for editing', () => {
    const initialValues = {
      id: 1,
      title: 'Test Task',
      description: 'Test Description',
      due_date: '2023-12-31',
      status: 'in_progress'
    };
    
    render(<TaskForm onAddTask={mockAddTask} initialValues={initialValues} />);
    
    // Check pre-populated values
    expect(screen.getByTestId('title-input')).toHaveValue('Test Task');
    expect(screen.getByTestId('description-input')).toHaveValue('Test Description');
    expect(screen.getByTestId('due-date-input')).toHaveValue('2023-12-31');
    expect(screen.getByTestId('status-input')).toHaveValue('in_progress');
    
    // Button should show "Update" instead of "Add"
    expect(screen.getByTestId('submit-button')).toHaveTextContent('Update Task');
  });
  
  test('validates required fields', async () => {
    render(<TaskForm onAddTask={mockAddTask} />);
    
    // Submit with empty title
    fireEvent.click(screen.getByTestId('submit-button'));
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByTestId('title-error')).toBeInTheDocument();
      expect(screen.getByTestId('title-error')).toHaveTextContent('Title is required');
    });
    
    // Check that onAddTask was not called
    expect(mockAddTask).not.toHaveBeenCalled();
  });
  
  test('validates title length', async () => {
    render(<TaskForm onAddTask={mockAddTask} />);
    
    // Enter too short title
    userEvent.type(screen.getByTestId('title-input'), 'AB');
    fireEvent.click(screen.getByTestId('submit-button'));
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByTestId('title-error')).toBeInTheDocument();
      expect(screen.getByTestId('title-error')).toHaveTextContent('Title must be at least 3 characters');
    });
    
    // Check that onAddTask was not called
    expect(mockAddTask).not.toHaveBeenCalled();
  });
  
  test('validates due date not in the past', async () => {
    render(<TaskForm onAddTask={mockAddTask} />);
    
    // Set title to valid value
    userEvent.type(screen.getByTestId('title-input'), 'Valid Task');
    
    // Set due date to yesterday
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const formattedDate = yesterday.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    
    // Need to use fireEvent for date input as userEvent doesn't work well with date inputs
    fireEvent.change(screen.getByTestId('due-date-input'), {
      target: { value: formattedDate }
    });
    
    fireEvent.click(screen.getByTestId('submit-button'));
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByTestId('due-date-error')).toBeInTheDocument();
      expect(screen.getByTestId('due-date-error')).toHaveTextContent('Due date cannot be in the past');
    });
    
    // Check that onAddTask was not called
    expect(mockAddTask).not.toHaveBeenCalled();
  });
  
  test('submits form with valid data', async () => {
    render(<TaskForm onAddTask={mockAddTask} />);
    
    // Fill out form
    userEvent.type(screen.getByTestId('title-input'), 'New Test Task');
    userEvent.type(screen.getByTestId('description-input'), 'This is a test task');
    
    // Set due date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const formattedDate = tomorrow.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    
    fireEvent.change(screen.getByTestId('due-date-input'), {
      target: { value: formattedDate }
    });
    
    // Change status
    userEvent.selectOptions(screen.getByTestId('status-input'), 'in_progress');
    
    // Submit form
    fireEvent.click(screen.getByTestId('submit-button'));
    
    // Check that onAddTask was called with correct data
    expect(mockAddTask).toHaveBeenCalledTimes(1);
    expect(mockAddTask).toHaveBeenCalledWith({
      title: 'New Test Task',
      description: 'This is a test task',
      due_date: formattedDate,
      status: 'in_progress'
    });
    
    // Form should be reset
    await waitFor(() => {
      expect(screen.getByTestId('title-input')).toHaveValue('');
      expect(screen.getByTestId('description-input')).toHaveValue('');
    });
  });
  
  test('does not reset form after submit when editing', async () => {
    const initialValues = {
      id: 1,
      title: 'Test Task',
      description: 'Initial Description',
      status: 'pending'
    };
    
    render(<TaskForm onAddTask={mockAddTask} initialValues={initialValues} />);
    
    // Update description
    userEvent.clear(screen.getByTestId('description-input'));
    userEvent.type(screen.getByTestId('description-input'), 'Updated Description');
    
    // Submit form
    fireEvent.click(screen.getByTestId('submit-button'));
    
    // Check that onAddTask was called with correct data
    expect(mockAddTask).toHaveBeenCalledTimes(1);
    expect(mockAddTask).toHaveBeenCalledWith({
      title: 'Test Task',
      description: 'Updated Description',
      due_date: '',
      status: 'pending'
    });
    
    // Form should not be reset
    await waitFor(() => {
      expect(screen.getByTestId('title-input')).toHaveValue('Test Task');
      expect(screen.getByTestId('description-input')).toHaveValue('Updated Description');
    });
  });
  
  test('clears errors on input change', async () => {
    render(<TaskForm onAddTask={mockAddTask} />);
    
    // Submit with empty title to trigger error
    fireEvent.click(screen.getByTestId('submit-button'));
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByTestId('title-error')).toBeInTheDocument();
    });
    
    // Now type in the title field
    userEvent.type(screen.getByTestId('title-input'), 'New Title');
    
    // Error should be cleared
    expect(screen.queryByTestId('title-error')).not.toBeInTheDocument();
  });
});
```

## Route Testing

Route tests verify that your React Router configuration works correctly, showing the right components for each route.

Let's create a simple routing setup and test it:

```jsx
// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './redux/store';
import TaskList from './components/TaskList/TaskList';
import TaskDetail from './components/TaskDetail/TaskDetail';
import TaskForm from './components/TaskForm/TaskForm';
import TaskDashboard from './components/TaskDashboard/TaskDashboard';
import Navbar from './components/Navbar/Navbar';
import LoginPage from './components/LoginPage/LoginPage';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import './App.css';

const App = () => {
  return (
    <Provider store={store}>
      <Router>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Navigate to="/tasks" />} />
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <TaskDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/tasks"
                element={
                  <ProtectedRoute>
                    <TaskList />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/tasks/new"
                element={
                  <ProtectedRoute>
                    <TaskForm />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/tasks/:id"
                element={
                  <ProtectedRoute>
                    <TaskDetail />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/tasks/:id/edit"
                element={
                  <ProtectedRoute>
                    <TaskForm />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<div>Page not found</div>} />
            </Routes>
          </main>
        </div>
      </Router>
    </Provider>
  );
};

export default App;

// src/components/ProtectedRoute/ProtectedRoute.jsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated } from '../../redux/slices/authSlice';

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const location = useLocation();
  
  if (!isAuthenticated) {
    // Redirect to login but save the current location they tried to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
};

export default ProtectedRoute;
```

Now let's test our routing:

```jsx
// src/App.test.jsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import App from './App';

// Mock all components used in routes
jest.mock('./components/TaskList/TaskList', () => () => <div data-testid="task-list">Task List</div>);
jest.mock('./components/TaskDetail/TaskDetail', () => () => <div data-testid="task-detail">Task Detail</div>);
jest.mock('./components/TaskForm/TaskForm', () => () => <div data-testid="task-form">Task Form</div>);
jest.mock('./components/TaskDashboard/TaskDashboard', () => () => <div data-testid="task-dashboard">Dashboard</div>);
jest.mock('./components/LoginPage/LoginPage', () => () => <div data-testid="login-page">Login Page</div>);
jest.mock('./components/Navbar/Navbar', () => () => <div data-testid="navbar">Navbar</div>);

// Create mock store
const mockStore = configureStore();

describe('App Routing', () => {
  // Test when user is authenticated
  describe('When authenticated', () => {
    let store;
    
    beforeEach(() => {
      store = mockStore({
        auth: {
          isAuthenticated: true,
          user: { id: 1, username: 'testuser' }
        }
      });
    });
    
    test('renders TaskList for /tasks route', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/tasks']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
      expect(screen.getByTestId('task-list')).toBeInTheDocument();
    });
    
    test('renders TaskDetail for /tasks/:id route', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/tasks/1']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('task-detail')).toBeInTheDocument();
    });
    
    test('renders TaskForm for /tasks/new route', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/tasks/new']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('task-form')).toBeInTheDocument();
    });
    
    test('renders TaskForm for /tasks/:id/edit route', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/tasks/1/edit']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('task-form')).toBeInTheDocument();
    });
    
    test('renders Dashboard for /dashboard route', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/dashboard']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('task-dashboard')).toBeInTheDocument();
    });
    
    test('redirects from / to /tasks', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('task-list')).toBeInTheDocument();
    });
    
    test('renders not found page for unknown routes', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/unknown-route']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByText('Page not found')).toBeInTheDocument();
    });
  });
  
  // Test when user is not authenticated
  describe('When not authenticated', () => {
    let store;
    
    beforeEach(() => {
      store = mockStore({
        auth: {
          isAuthenticated: false,
          user: null
        }
      });
    });
    
    test('redirects to login from protected route', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/tasks']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      // Should redirect to login
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
      expect(screen.queryByTestId('task-list')).not.toBeInTheDocument();
    });
    
    test('allows access to login page', () => {
      render(
        <Provider store={store}>
          <MemoryRouter initialEntries={['/login']}>
            <App />
          </MemoryRouter>
        </Provider>
      );
      
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });
  });
});
```

### Testing Route Parameters

Let's also test a component that uses route parameters:

```jsx
// src/components/TaskDetail/TaskDetail.jsx
import React, { useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchTaskById,
  deleteTask,
  updateTask,
  selectCurrentTask,
  selectTasksStatus,
  selectTasksError
} from '../../redux/slices/tasksSlice';
import './TaskDetail.css';

const TaskDetail = () => {
  const { id } = useParams();
  const taskId = parseInt(id, 10);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const task = useSelector(selectCurrentTask);
  const status = useSelector(selectTasksStatus);
  const error = useSelector(selectTasksError);
  
  useEffect(() => {
    if (taskId) {
      dispatch(fetchTaskById(taskId));
    }
  }, [taskId, dispatch]);
  
  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      dispatch(deleteTask(taskId))
        .then((resultAction) => {
          if (!resultAction.error) {
            navigate('/tasks');
          }
        });
    }
  };
  
  const handleToggleComplete = () => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    dispatch(updateTask({
      taskId,
      updates: { status: newStatus }
    }));
  };
  
  if (status === 'loading') {
    return <div data-testid="loading">Loading task...</div>;
  }
  
  if (error) {
    return <div data-testid="error">Error: {error}</div>;
  }
  
  if (!task) {
    return <div data-testid="not-found">Task not found</div>;
  }
  
  return (
    <div className="task-detail" data-testid="task-detail">
      <div className="task-header">
        <h1>{task.title}</h1>
        <div className={`status-badge ${task.status}`} data-testid="status-badge">
          {task.status}
        </div>
      </div>
      
      {task.description && (
        <div className="task-description">
          <h3>Description</h3>
          <p>{task.description}</p>
        </div>
      )}
      
      {task.due_date && (
        <div className="task-due-date">
          <h3>Due Date</h3>
          <p data-testid="due-date">
            {new Date(task.due_date).toLocaleDateString()}
          </p>
        </div>
      )}
      
      <div className="task-metadata">
        <p>Created: {new Date(task.created_at).toLocaleString()}</p>
        <p>Last Updated: {new Date(task.updated_at).toLocaleString()}</p>
      </div>
      
      <div className="task-actions">
        <button
          onClick={handleToggleComplete}
          className={`toggle-button ${task.status}`}
          data-testid="toggle-button"
        >
          {task.status === 'completed' ? 'Mark Incomplete' : 'Mark Complete'}
        </button>
        
        <Link
          to={`/tasks/${taskId}/edit`}
          className="edit-button"
          data-testid="edit-link"
        >
          Edit Task
        </Link>
        
        <button
          onClick={handleDelete}
          className="delete-button"
          data-testid="delete-button"
        >
          Delete Task
        </button>
      </div>
      
      <Link to="/tasks" className="back-link" data-testid="back-link">
        Back to Tasks
      </Link>
    </div>
  );
};

export default TaskDetail;
```

Now let's test this component:

```jsx
// src/components/TaskDetail/TaskDetail.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import TaskDetail from './TaskDetail';
import { 
  fetchTaskById, 
  updateTask, 
  deleteTask 
} from '../../redux/slices/tasksSlice';

// Mock the action creators
jest.mock('../../redux/slices/tasksSlice', () => {
  const actual = jest.requireActual('../../redux/slices/tasksSlice');
  return {
    ...actual,
    fetchTaskById: jest.fn(),
    updateTask: jest.fn(),
    deleteTask: jest.fn()
  };
});

// Mock the window.confirm method
window.confirm = jest.fn();

const mockStore = configureStore([thunk]);

describe('TaskDetail Component', () => {
  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'This is a test task',
    status: 'pending',
    due_date: '2023-12-31',
    created_at: '2023-01-01T12:00:00Z',
    updated_at: '2023-01-02T12:00:00Z'
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    fetchTaskById.mockReturnValue({ type: 'tasks/fetchTaskById/fulfilled', payload: mockTask });
    updateTask.mockReturnValue({ type: 'tasks/updateTask/fulfilled', payload: { ...mockTask, status: 'completed' } });
    deleteTask.mockReturnValue({ type: 'tasks/deleteTask/fulfilled', payload: 1 });
    window.confirm.mockReturnValue(true);
  });
  
  test('fetches task on mount and displays task details', () => {
    const store = mockStore({
      tasks: {
        currentTask: mockTask,
        status: 'succeeded',
        error: null
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/1']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    // Check if fetchTaskById was called with the correct ID
    expect(fetchTaskById).toHaveBeenCalledWith(1);
    
    // Check if task details are displayed
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('This is a test task')).toBeInTheDocument();
    expect(screen.getByTestId('status-badge')).toHaveTextContent('pending');
    expect(screen.getByTestId('due-date')).toBeInTheDocument();
    
    // Check if action buttons are present
    expect(screen.getByTestId('toggle-button')).toHaveTextContent('Mark Complete');
    expect(screen.getByTestId('edit-link')).toHaveAttribute('href', '/tasks/1/edit');
    expect(screen.getByTestId('delete-button')).toBeInTheDocument();
    expect(screen.getByTestId('back-link')).toHaveAttribute('href', '/tasks');
  });
  
  test('displays loading state', () => {
    const store = mockStore({
      tasks: {
        currentTask: null,
        status: 'loading',
        error: null
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/1']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });
  
  test('displays error state', () => {
    const store = mockStore({
      tasks: {
        currentTask: null,
        status: 'failed',
        error: 'Failed to fetch task'
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/1']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    expect(screen.getByTestId('error')).toBeInTheDocument();
    expect(screen.getByText(/Failed to fetch task/)).toBeInTheDocument();
  });
  
  test('displays not found when task is missing', () => {
    const store = mockStore({
      tasks: {
        currentTask: null,
        status: 'succeeded',
        error: null
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/999']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    expect(screen.getByTestId('not-found')).toBeInTheDocument();
  });
  
  test('handles toggle complete action', () => {
    const store = mockStore({
      tasks: {
        currentTask: mockTask,
        status: 'succeeded',
        error: null
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/1']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    // Click the toggle button
    fireEvent.click(screen.getByTestId('toggle-button'));
    
    // Check if updateTask was called with the correct data
    expect(updateTask).toHaveBeenCalledWith({
      taskId: 1,
      updates: { status: 'completed' }
    });
  });
  
  test('handles delete action with confirmation', () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate
    }));
    
    const store = mockStore({
      tasks: {
        currentTask: mockTask,
        status: 'succeeded',
        error: null
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/1']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    // Click the delete button
    fireEvent.click(screen.getByTestId('delete-button'));
    
    // Check if confirmation was shown
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this task?');
    
    // Check if deleteTask was called with the correct ID
    expect(deleteTask).toHaveBeenCalledWith(1);
  });
  
  test('does not delete when confirmation is canceled', () => {
    window.confirm.mockReturnValueOnce(false);
    
    const store = mockStore({
      tasks: {
        currentTask: mockTask,
        status: 'succeeded',
        error: null
      }
    });
    
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/tasks/1']}>
          <Routes>
            <Route path="/tasks/:id" element={<TaskDetail />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    );
    
    // Click the delete button
    fireEvent.click(screen.getByTestId('delete-button'));
    
    // Check if confirmation was shown
    expect(window.confirm).toHaveBeenCalled();
    
    // Check that deleteTask was not called
    expect(deleteTask).not.toHaveBeenCalled();
  });
});
```

## Accessibility Testing

Accessibility tests ensure your React components are usable by people with disabilities.

Let's test our `TaskForm` component for accessibility:

```jsx
// src/components/TaskForm/TaskForm.a11y.test.jsx
import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import TaskForm from './TaskForm';

// Add the custom matcher to Jest
expect.extend(toHaveNoViolations);

describe('TaskForm Accessibility', () => {
  test('should not have accessibility violations', async () => {
    const mockAddTask = jest.fn();
    const { container } = render(<TaskForm onAddTask={mockAddTask} />);
    
    // Run the accessibility tests
    const results = await axe(container);
    
    // Check for violations
    expect(results).toHaveNoViolations();
  });
  
  test('form with errors should still be accessible', async () => {
    const mockAddTask = jest.fn();
    const { container, getByTestId } = render(<TaskForm onAddTask={mockAddTask} />);
    
    // Submit the form without filling required fields to trigger errors
    const submitButton = getByTestId('submit-button');
    submitButton.click();
    
    // Run the accessibility tests
    const results = await axe(container);
    
    // Even with validation errors, the form should still be accessible
    expect(results).toHaveNoViolations();
  });
});
```

For more thorough accessibility testing, let's create a common set of accessibility tests for components:

```jsx
// src/tests/a11y.js
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';

export async function testComponentA11y(Component, props = {}) {
  const { container } = render(<Component {...props} />);
  const results = await axe(container);
  return results;
}

// src/tests/a11y.test.jsx
import React from 'react';
import { toHaveNoViolations } from 'jest-axe';
import { testComponentA11y } from './a11y';
import TaskForm from '../components/TaskForm/TaskForm';
import Task from '../components/Task/Task';
import Navbar from '../components/Navbar/Navbar';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('TaskForm is accessible', async () => {
    const results = await testComponentA11y(TaskForm, {
      onAddTask: jest.fn()
    });
    expect(results).toHaveNoViolations();
  });
  
  test('Task component is accessible', async () => {
    const mockTask = {
      id: 1,
      title: 'Test Task',
      description: 'This is a test task',
      status: 'pending',
      due_date: '2023-12-31'
    };
    
    const results = await testComponentA11y(Task, {
      task: mockTask,
      onToggleComplete: jest.fn(),
      onDelete: jest.fn()
    });
    expect(results).toHaveNoViolations();
  });
  
  test('Navbar is accessible', async () => {
    const results = await testComponentA11y(Navbar);
    expect(results).toHaveNoViolations();
  });
});
```

## Visual Regression Testing

Visual regression tests catch unexpected visual changes to components.

Let's set up Jest Image Snapshot for visual regression testing:

```jsx
// src/setupTests.js (add to existing file)
import { toMatchImageSnapshot } from 'jest-image-snapshot';

// Configure the custom matcher
expect.extend({ toMatchImageSnapshot });

// src/components/Task/Task.visual.test.jsx
import React from 'react';
import { render } from '@testing-library/react';
import Task from './Task';

// Mock function to "take screenshot" - in a real setup, this would use Puppeteer or similar
const mockTakeScreenshot = async (element) => {
  // This is a simplified mock - in a real implementation,
  // you would use Puppeteer or another tool to capture a real screenshot
  return Buffer.from('mock screenshot data');
};

describe('Task Visual Regression', () => {
  // Skip these tests in CI environments that don't support screenshots
  const itif = process.env.CI ? it.skip : it;
  
  itif('matches the snapshot for a pending task', async () => {
    const mockTask = {
      id: 1,
      title: 'Pending Task',
      description: 'This is a pending task',
      status: 'pending',
      due_date: '2023-12-31'
    };
    
    const { container } = render(
      <Task
        task={mockTask}
        onToggleComplete={jest.fn()}
        onDelete={jest.fn()}
      />
    );
    
    const screenshot = await mockTakeScreenshot(container);
    expect(screenshot).toMatchImageSnapshot();
  });
  
  itif('matches the snapshot for a completed task', async () => {
    const mockTask = {
      id: 1,
      title: 'Completed Task',
      description: 'This is a completed task',
      status: 'completed',
      due_date: '2023-12-31'
    };
    
    const { container } = render(
      <Task
        task={mockTask}
        onToggleComplete={jest.fn()}
        onDelete={jest.fn()}
      />
    );
    
    const screenshot = await mockTakeScreenshot(container);
    expect(screenshot).toMatchImageSnapshot();
  });
  
  itif('matches the snapshot for an overdue task', async () => {
    // Create a task with due date in the past
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 2); // 2 days ago
    
    const mockTask = {
      id: 1,
      title: 'Overdue Task',
      description: 'This is an overdue task',
      status: 'pending',
      due_date: pastDate.toISOString().split('T')[0]
    };
    
    const { container } = render(
      <Task
        task={mockTask}
        onToggleComplete={jest.fn()}
        onDelete={jest.fn()}
      />
    );
    
    const screenshot = await mockTakeScreenshot(container);
    expect(screenshot).toMatchImageSnapshot();
  });
});
```

For a more realistic setup, you'd typically use a tool like Puppeteer or Playwright with a custom Jest environment.

Here's how to set up Storybook with Storyshots, a popular approach for visual regression testing:

```jsx
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.mdx', '../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/preset-create-react-app'
  ]
};

// src/components/Task/Task.stories.jsx
import React from 'react';
import Task from './Task';

export default {
  title: 'Components/Task',
  component: Task,
  argTypes: {
    onToggleComplete: { action: 'toggled' },
    onDelete: { action: 'deleted' }
  }
};

const Template = (args) => <Task {...args} />;

export const PendingTask = Template.bind({});
PendingTask.args = {
  task: {
    id: 1,
    title: 'Pending Task',
    description: 'This is a pending task',
    status: 'pending',
    due_date: '2023-12-31'
  }
};

export const CompletedTask = Template.bind({});
CompletedTask.args = {
  task: {
    id: 2,
    title: 'Completed Task',
    description: 'This is a completed task',
    status: 'completed',
    due_date: '2023-12-31'
  }
};

export const OverdueTask = Template.bind({});
OverdueTask.args = {
  task: {
    id: 3,
    title: 'Overdue Task',
    description: 'This is an overdue task',
    status: 'pending',
    due_date: '2023-01-01' // Past date
  }
};

export const TaskWithoutDueDate = Template.bind({});
TaskWithoutDueDate.args = {
  task: {
    id: 4,
    title: 'No Due Date',
    description: 'This task has no due date',
    status: 'pending'
  }
};

// src/storybook.test.js
import initStoryshots from '@storybook/addon-storyshots';
import { imageSnapshot } from '@storybook/addon-storyshots-puppeteer';

initStoryshots({
  test: imageSnapshot({
    storybookUrl: 'http://localhost:6006', // Storybook must be running
    customizePage: page => page.setViewport({ width: 1200, height: 800 })
  })
});
```

## Advanced Testing Techniques

### 1. Component Memoization Testing

Testing that your memoized components only re-render when needed:

```jsx
// src/components/MemoizedTask/MemoizedTask.jsx
import React, { memo } from 'react';
import PropTypes from 'prop-types';

const MemoizedTask = memo(({ task, onToggleComplete, onDelete }) => {
  console.log(`Rendering task ${task.id}`);
  
  return (
    <div className={`task ${task.status}`} data-testid={`task-${task.id}`}>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
      <div className="task-actions">
        <button
          onClick={() => onToggleComplete(task.id)}
          data-testid={`toggle-${task.id}`}
        >
          {task.status === 'completed' ? 'Mark Incomplete' : 'Mark Complete'}
        </button>
        <button
          onClick={() => onDelete(task.id)}
          data-testid={`delete-${task.id}`}
        >
          Delete
        </button>
      </div>
    </div>
  );
});

MemoizedTask.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    status: PropTypes.string.isRequired
  }).isRequired,
  onToggleComplete: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired
};

export default MemoizedTask;

// src/components/MemoizedTask/MemoizedTask.test.jsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import MemoizedTask from './MemoizedTask';

describe('MemoizedTask Component', () => {
  // Spy on console.log to check renders
  beforeEach(() => {
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });
  
  afterEach(() => {
    console.log.mockRestore();
  });
  
  test('only re-renders when props change', () => {
    const task = {
      id: 1,
      title: 'Test Task',
      description: 'Description',
      status: 'pending'
    };
    
    const onToggleComplete = jest.fn();
    const onDelete = jest.fn();
    
    const { rerender } = render(
      <MemoizedTask
        task={task}
        onToggleComplete={onToggleComplete}
        onDelete={onDelete}
      />
    );
    
    // First render
    expect(console.log).toHaveBeenCalledWith('Rendering task 1');
    console.log.mockClear();
    
    // Re-render with same props
    rerender(
      <MemoizedTask
        task={task}
        onToggleComplete={onToggleComplete}
        onDelete={onDelete}
      />
    );
    
    // Should not log (no re-render)
    expect(console.log).not.toHaveBeenCalled();
    
    // Re-render with different task
    rerender(
      <MemoizedTask
        task={{ ...task, title: 'Updated Task' }}
        onToggleComplete={onToggleComplete}
        onDelete={onDelete}
      />
    );
    
    // Should log (props changed)
    expect(console.log).toHaveBeenCalledWith('Rendering task 1');
    console.log.mockClear();
    
    // Re-render with new function references
    rerender(
      <MemoizedTask
        task={task}
        onToggleComplete={() => {}}
        onDelete={() => {}}
      />
    );
    
    // Should log (function references changed)
    expect(console.log).toHaveBeenCalledWith('Rendering task 1');
  });
});
```

### 2. Custom Hooks with Context Testing

Testing a custom hook that uses React Context:

```jsx
// src/contexts/ThemeContext.js
import React, { createContext, useState, useContext, useCallback } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children, initialTheme = 'light' }) => {
  const [theme, setTheme] = useState(initialTheme);
  
  const toggleTheme = useCallback(() => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  }, []);
  
  const value = {
    theme,
    toggleTheme
  };
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// src/contexts/ThemeContext.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react-hooks';
import { ThemeProvider, useTheme } from './ThemeContext';

describe('ThemeContext', () => {
  test('useTheme throws error when used outside provider', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.error).toEqual(Error('useTheme must be used within a ThemeProvider'));
  });
  
  test('provides the default theme value', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => <ThemeProvider>{children}</ThemeProvider>
    });
    
    expect(result.current.theme).toBe('light');
  });
  
  test('provides custom initial theme value', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => (
        <ThemeProvider initialTheme="dark">{children}</ThemeProvider>
      )
    });
    
    expect(result.current.theme).toBe('dark');
  });
  
  test('toggleTheme switches between light and dark', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => <ThemeProvider>{children}</ThemeProvider>
    });
    
    // Initial theme is light
    expect(result.current.theme).toBe('light');
    
    // Toggle to dark
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('dark');
    
    // Toggle back to light
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('light');
  });
  
  test('components can consume the theme context', () => {
    const TestComponent = () => {
      const { theme, toggleTheme } = useTheme();
      return (
        <div>
          <span data-testid="theme-value">{theme}</span>
          <button onClick={toggleTheme} data-testid="toggle-button">
            Toggle Theme
          </button>
        </div>
      );
    };
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    // Check initial theme
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    
    // Toggle theme
    fireEvent.click(screen.getByTestId('toggle-button'));
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
  });
});
```

### 3. Asynchronous Actions Testing

Testing complex asynchronous actions in Redux:

```jsx
// src/redux/slices/asyncTasksSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Complex async thunk with multiple API calls and conditions
export const processBatchTasks = createAsyncThunk(
  'tasks/processBatch',
  async (taskIds, { dispatch, getState, rejectWithValue }) => {
    try {
      // First fetch all tasks
      const response = await fetch(`/api/tasks/batch?ids=${taskIds.join(',')}`);
      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }
      
      const tasks = await response.json();
      
      // Process each task
      const results = [];
      for (const task of tasks) {
        // Skip completed tasks
        if (task.status === 'completed') {
          results.push({ id: task.id, skipped: true, message: 'Already completed' });
          continue;
        }
        
        // Process task
        const processResponse = await fetch(`/api/tasks/${task.id}/process`, {
          method: 'POST'
        });
        
        if (processResponse.ok) {
          const result = await processResponse.json();
          results.push({ id: task.id, success: true, result });
        } else {
          results.push({ id: task.id, success: false, error: 'Processing failed' });
        }
      }
      
      return results;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const asyncTasksSlice = createSlice({
  name: 'asyncTasks',
  initialState: {
    batchResults: [],
    status: 'idle',
    error: null
  },
  reducers: {
    clearBatchResults: (state) => {
      state.batchResults = [];
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(processBatchTasks.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(processBatchTasks.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.batchResults = action.payload;
      })
      .addCase(processBatchTasks.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { clearBatchResults } = asyncTasksSlice.actions;
export default asyncTasksSlice.reducer;

// src/redux/slices/asyncTasksSlice.test.js
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import fetchMock from 'jest-fetch-mock';
import asyncTasksReducer, { processBatchTasks, clearBatchResults } from './asyncTasksSlice';

// Enable fetch mocks
fetchMock.enableMocks();

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

describe('Async Tasks Slice', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });
  
  describe('processBatchTasks thunk', () => {
    test('handles successful processing of all tasks', async () => {
      // Mock API responses
      fetchMock.mockResponses(
        // First fetch for all tasks
        [
          JSON.stringify([
            { id: 1, title: 'Task 1', status: 'pending' },
            { id: 2, title: 'Task 2', status: 'in_progress' },
            { id: 3, title: 'Task 3', status: 'completed' }
          ]),
          { status: 200 }
        ],
        // Process Task 1
        [
          JSON.stringify({ id: 1, processed: true }),
          { status: 200 }
        ],
        // Process Task 2
        [
          JSON.stringify({ id: 2, processed: true }),
          { status: 200 }
        ]
      );
      
      const expectedActions = [
        { type: processBatchTasks.pending.type },
        {
          type: processBatchTasks.fulfilled.type,
          payload: [
            { id: 1, success: true, result: { id: 1, processed: true } },
            { id: 2, success: true, result: { id: 2, processed: true } },
            { id: 3, skipped: true, message: 'Already completed' }
          ]
        }
      ];
      
      const store = mockStore({ asyncTasks: { batchResults: [], status: 'idle', error: null } });
      await store.dispatch(processBatchTasks([1, 2, 3]));
      
      // Check that fetch was called with the correct URLs
      expect(fetchMock.mock.calls[0][0]).toEqual('/api/tasks/batch?ids=1,2,3');
      expect(fetchMock.mock.calls[1][0]).toEqual('/api/tasks/1/process');
      expect(fetchMock.mock.calls[2][0]).toEqual('/api/tasks/2/process');
      
      // Check actions
      const actions = store.getActions();
      expect(actions[0].type).toEqual(expectedActions[0].type);
      expect(actions[1].type).toEqual(expectedActions[1].type);
      expect(actions[1].payload).toEqual(expectedActions[1].payload);
    });
    
    test('handles a failed batch fetch', async () => {
      // Mock failed API response
      fetchMock.mockReject(new Error('Network error'));
      
      const expectedActions = [
        { type: processBatchTasks.pending.type },
        {
          type: processBatchTasks.rejected.type,
          payload: 'Network error'
        }
      ];
      
      const store = mockStore({ asyncTasks: { batchResults: [], status: 'idle', error: null } });
      await store.dispatch(processBatchTasks([1, 2, 3]));
      
      // Check actions
      const actions = store.getActions();
      expect(actions[0].type).toEqual(expectedActions[0].type);
      expect(actions[1].type).toEqual(expectedActions[1].type);
      expect(actions[1].payload).toEqual(expectedActions[1].payload);
    });
    
    test('handles a failed task processing', async () => {
      // Mock API responses
      fetchMock.mockResponses(
        // First fetch for all tasks
        [
          JSON.stringify([
            { id: 1, title: 'Task 1', status: 'pending' },
            { id: 2, title: 'Task 2', status: 'pending' }
          ]),
          { status: 200 }
        ],
        // Process Task 1 - success
        [
          JSON.stringify({ id: 1, processed: true }),
          { status: 200 }
        ],
        // Process Task 2 - failure
        [
          'Processing failed',
          { status: 500 }
        ]
      );
      
      const expectedActions = [
        { type: processBatchTasks.pending.type },
        {
          type: processBatchTasks.fulfilled.type,
          payload: [
            { id: 1, success: true, result: { id: 1, processed: true } },
            { id: 2, success: false, error: 'Processing failed' }
          ]
        }
      ];
      
      const store = mockStore({ asyncTasks: { batchResults: [], status: 'idle', error: null } });
      await store.dispatch(processBatchTasks([1, 2]));
      
      // Check actions
      const actions = store.getActions();
      expect(actions[0].type).toEqual(expectedActions[0].type);
      expect(actions[1].type).toEqual(expectedActions[1].type);
      expect(actions[1].payload).toEqual(expectedActions[1].payload);
    });
  });
  
  describe('reducer', () => {
    test('should return the initial state', () => {
      expect(asyncTasksReducer(undefined, { type: undefined })).toEqual({
        batchResults: [],
        status: 'idle',
        error: null
      });
    });
    
    test('should handle clearBatchResults', () => {
      const initialState = {
        batchResults: [{ id: 1, success: true }],
        status: 'succeeded',
        error: null
      };
      
      expect(asyncTasksReducer(initialState, clearBatchResults())).toEqual({
        batchResults: [],
        status: 'succeeded',
        error: null
      });
    });
    
    test('should handle processBatchTasks.pending', () => {
      const initialState = {
        batchResults: [],
        status: 'idle',
        error: 'Previous error'
      };
      
      expect(asyncTasksReducer(initialState, { type: processBatchTasks.pending.type })).toEqual({
        batchResults: [],
        status: 'loading',
        error: null
      });
    });
    
    test('should handle processBatchTasks.fulfilled', () => {
      const initialState = {
        batchResults: [],
        status: 'loading',
        error: null
      };
      
      const results = [
        { id: 1, success: true, result: { id: 1, processed: true } }
      ];
      
      expect(
        asyncTasksReducer(initialState, {
          type: processBatchTasks.fulfilled.type,
          payload: results
        })
      ).toEqual({
        batchResults: results,
        status: 'succeeded',
        error: null
      });
    });
    
    test('should handle processBatchTasks.rejected', () => {
      const initialState = {
        batchResults: [],
        status: 'loading',
        error: null
      };
      
      expect(
        asyncTasksReducer(initialState, {
          type: processBatchTasks.rejected.type,
          payload: 'Error message'
        })
      ).toEqual({
        batchResults: [],
        status: 'failed',
        error: 'Error message'
      });
    });
  });
});
```

### 4. Testing Client-Side Search and Filtering

Testing a component with search and filter functionality:

```jsx
// src/components/TaskSearch/TaskSearch.jsx
import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import './TaskSearch.css';

const TaskSearch = ({ tasks, onSelectTask }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      // Apply search term filter
      const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            (task.description && task.description.toLowerCase().includes(searchTerm.toLowerCase()));
      
      // Apply status filter
      const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  }, [tasks, searchTerm, statusFilter]);
  
  return (
    <div className="task-search" data-testid="task-search">
      <div className="search-controls">
        <input
          type="text"
          placeholder="Search tasks..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          data-testid="search-input"
          className="search-input"
        />
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          data-testid="status-filter"
          className="status-filter"
        >
          <option value="all">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      <div className="search-results" data-testid="search-results">
        <h3>Results ({filteredTasks.length})</h3>
        
        {filteredTasks.length === 0 ? (
          <p className="no-results" data-testid="no-results">No tasks found matching your search</p>
        ) : (
          <ul className="task-list">
            {filteredTasks.map(task => (
              <li key={task.id} data-testid={`task-item-${task.id}`}>
                <button
                  onClick={() => onSelectTask(task)}
                  className={`task-item ${task.status}`}
                >
                  <span className="task-title">{task.title}</span>
                  <span className="task-status">{task.status}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

TaskSearch.propTypes = {
  tasks: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    status: PropTypes.string.isRequired
  })).isRequired,
  onSelectTask: PropTypes.func.isRequired
};

export default TaskSearch;

// src/components/TaskSearch/TaskSearch.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskSearch from './TaskSearch';

describe('TaskSearch Component', () => {
  const mockTasks = [
    {
      id: 1,
      title: 'Complete project',
      description: 'Finish the React project',
      status: 'pending'
    },
    {
      id: 2,
      title: 'Review code',
      description: 'Review team code',
      status: 'in_progress'
    },
    {
      id: 3,
      title: 'Fix bugs',
      description: 'Fix reported issues',
      status: 'completed'
    },
    {
      id: 4,
      title: 'Project planning',
      description: 'Plan next sprint',
      status: 'cancelled'
    }
  ];
  
  const mockSelectTask = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders all tasks initially', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Should show all tasks
    expect(screen.getByTestId('search-results')).toBeInTheDocument();
    expect(screen.getByText('Results (4)')).toBeInTheDocument();
    
    // Check that all tasks are displayed
    mockTasks.forEach(task => {
      expect(screen.getByTestId(`task-item-${task.id}`)).toBeInTheDocument();
      expect(screen.getByText(task.title)).toBeInTheDocument();
    });
  });
  
  test('filters tasks by search term', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Search for "project"
    fireEvent.change(screen.getByTestId('search-input'), {
      target: { value: 'project' }
    });
    
    // Should show only tasks with "project" in title or description
    expect(screen.getByText('Results (2)')).toBeInTheDocument();
    expect(screen.getByTestId('task-item-1')).toBeInTheDocument(); // "Complete project"
    expect(screen.getByTestId('task-item-4')).toBeInTheDocument(); // "Project planning"
    expect(screen.queryByTestId('task-item-2')).not.toBeInTheDocument();
    expect(screen.queryByTestId('task-item-3')).not.toBeInTheDocument();
  });
  
  test('filters tasks by status', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Filter by "completed" status
    fireEvent.change(screen.getByTestId('status-filter'), {
      target: { value: 'completed' }
    });
    
    // Should show only completed tasks
    expect(screen.getByText('Results (1)')).toBeInTheDocument();
    expect(screen.getByTestId('task-item-3')).toBeInTheDocument(); // "Fix bugs"
    expect(screen.queryByTestId('task-item-1')).not.toBeInTheDocument();
    expect(screen.queryByTestId('task-item-2')).not.toBeInTheDocument();
    expect(screen.queryByTestId('task-item-4')).not.toBeInTheDocument();
  });
  
  test('combines search term and status filters', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Search for "code" and filter by "in_progress"
    fireEvent.change(screen.getByTestId('search-input'), {
      target: { value: 'code' }
    });
    
    fireEvent.change(screen.getByTestId('status-filter'), {
      target: { value: 'in_progress' }
    });
    
    // Should show only in-progress tasks with "code" in title or description
    expect(screen.getByText('Results (1)')).toBeInTheDocument();
    expect(screen.getByTestId('task-item-2')).toBeInTheDocument(); // "Review code"
    expect(screen.queryByTestId('task-item-1')).not.toBeInTheDocument();
    expect(screen.queryByTestId('task-item-3')).not.toBeInTheDocument();
    expect(screen.queryByTestId('task-item-4')).not.toBeInTheDocument();
  });
  
  test('shows no results message when no tasks match', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Search for something that doesn't exist
    fireEvent.change(screen.getByTestId('search-input'), {
      target: { value: 'nonexistent' }
    });
    
    // Should show no results message
    expect(screen.getByText('Results (0)')).toBeInTheDocument();
    expect(screen.getByTestId('no-results')).toBeInTheDocument();
    expect(screen.getByText('No tasks found matching your search')).toBeInTheDocument();
  });
  
  test('calls onSelectTask when a task is clicked', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Click on a task
    fireEvent.click(screen.getByText('Review code'));
    
    // Check that onSelectTask was called with the correct task
    expect(mockSelectTask).toHaveBeenCalledTimes(1);
    expect(mockSelectTask).toHaveBeenCalledWith(mockTasks[1]);
  });
  
  test('search is case-insensitive', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Search with mixed case
    fireEvent.change(screen.getByTestId('search-input'), {
      target: { value: 'PrOjEcT' }
    });
    
    // Should still find tasks with "project"
    expect(screen.getByText('Results (2)')).toBeInTheDocument();
    expect(screen.getByTestId('task-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('task-item-4')).toBeInTheDocument();
  });
  
  test('clears search and resets results', () => {
    render(<TaskSearch tasks={mockTasks} onSelectTask={mockSelectTask} />);
    
    // Search for something
    fireEvent.change(screen.getByTestId('search-input'), {
      target: { value: 'code' }
    });
    
    // Should filter results
    expect(screen.getByText('Results (1)')).toBeInTheDocument();
    
    // Clear search
    fireEvent.change(screen.getByTestId('search-input'), {
      target: { value: '' }
    });
    
    // Should show all tasks again
    expect(screen.getByText('Results (4)')).toBeInTheDocument();
    mockTasks.forEach(task => {
      expect(screen.getByTestId(`task-item-${task.id}`)).toBeInTheDocument();
    });
  });
});
```

These sections provide a comprehensive guide to testing your React frontend components. By implementing these testing strategies, you'll have a robust set of tests that help ensure your application works correctly and remains stable as you continue development.
