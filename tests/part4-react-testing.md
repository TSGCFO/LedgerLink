# React Frontend Testing

This section covers comprehensive testing strategies for your React frontend, focusing on components, hooks, state management, API interactions, and more. We'll examine each aspect of React testing with detailed examples.

## Table of Contents

1. [Component Testing](#component-testing)
2. [Hook Testing](#hook-testing)
3. [State Management Testing](#state-management-testing)
4. [API Interaction Testing](#api-interaction-testing)
5. [Form Testing](#form-testing)
6. [Route Testing](#route-testing)
7. [Accessibility Testing](#accessibility-testing)
8. [Visual Regression Testing](#visual-regression-testing)
9. [Advanced Testing Techniques](#advanced-testing-techniques)

## Component Testing

Component tests verify that your React components render correctly and behave as expected when users interact with them.

### Basic Component Testing

Let's start with a simple Task component for our task management app:

```jsx
// src/components/Task/Task.jsx
import React from 'react';
import PropTypes from 'prop-types';
import './Task.css';

const Task = ({ task, onToggleComplete, onDelete }) => {
  const { id, title, description, status, due_date } = task;
  
  const isOverdue = () => {
    if (!due_date || status === 'completed') return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const dueDate = new Date(due_date);
    return dueDate < today;
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  return (
    <div
      className={`task ${status} ${isOverdue() ? 'overdue' : ''}`}
      data-testid={`task-${id}`}
    >
      <div className="task-header">
        <h3 className="task-title">{title}</h3>
        <div className="task-status">{status}</div>
      </div>
      
      {description && (
        <div className="task-description">{description}</div>
      )}
      
      {due_date && (
        <div className="task-due-date">
          Due: {formatDate(due_date)}
        </div>
      )}
      
      <div className="task-actions">
        {status !== 'completed' ? (
          <button
            onClick={() => onToggleComplete(id)}
            className="complete-button"
            data-testid={`complete-button-${id}`}
          >
            Mark Complete
          </button>
        ) : (
          <button
            onClick={() => onToggleComplete(id)}
            className="incomplete-button"
            data-testid={`incomplete-button-${id}`}
          >
            Mark Incomplete
          </button>
        )}
        
        <button
          onClick={() => onDelete(id)}
          className="delete-button"
          data-testid={`delete-button-${id}`}
        >
          Delete
        </button>
      </div>
    </div>
  );
};

Task.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    status: PropTypes.string.isRequired,
    due_date: PropTypes.string
  }).isRequired,
  onToggleComplete: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired
};

export default Task;
```

Now let's write tests for this component:

```jsx
// src/components/Task/Task.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Task from './Task';

describe('Task Component', () => {
  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'This is a test task',
    status: 'pending',
    due_date: '2023-12-31'
  };
  
  const mockToggleComplete = jest.fn();
  const mockDelete = jest.fn();
  
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });
  
  test('renders task with correct content', () => {
    render(
      <Task
        task={mockTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Check title and description
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('This is a test task')).toBeInTheDocument();
    
    // Check status
    expect(screen.getByText('pending')).toBeInTheDocument();
    
    // Check due date (formatted)
    expect(screen.getByText(/Due:/)).toBeInTheDocument();
    
    // Check buttons
    expect(screen.getByText('Mark Complete')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });
  
  test('calls onToggleComplete when complete button is clicked', () => {
    render(
      <Task
        task={mockTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Click the complete button
    const completeButton = screen.getByTestId('complete-button-1');
    fireEvent.click(completeButton);
    
    // Check if the function was called with the task id
    expect(mockToggleComplete).toHaveBeenCalledTimes(1);
    expect(mockToggleComplete).toHaveBeenCalledWith(1);
  });
  
  test('calls onDelete when delete button is clicked', () => {
    render(
      <Task
        task={mockTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Click the delete button
    const deleteButton = screen.getByTestId('delete-button-1');
    fireEvent.click(deleteButton);
    
    // Check if the function was called with the task id
    expect(mockDelete).toHaveBeenCalledTimes(1);
    expect(mockDelete).toHaveBeenCalledWith(1);
  });
  
  test('shows mark incomplete button for completed tasks', () => {
    const completedTask = {
      ...mockTask,
      status: 'completed'
    };
    
    render(
      <Task
        task={completedTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Check for Mark Incomplete button
    expect(screen.getByText('Mark Incomplete')).toBeInTheDocument();
    expect(screen.queryByText('Mark Complete')).not.toBeInTheDocument();
  });
  
  test('displays overdue class for overdue tasks', () => {
    // Create a task with due date in the past
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 2); // 2 days ago
    
    const overdueTask = {
      ...mockTask,
      due_date: pastDate.toISOString().split('T')[0] // Format as YYYY-MM-DD
    };
    
    render(
      <Task
        task={overdueTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Check that the task has the overdue class
    const taskElement = screen.getByTestId('task-1');
    expect(taskElement).toHaveClass('overdue');
  });
  
  test('does not display overdue class for completed tasks with past due date', () => {
    // Create a completed task with due date in the past
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 2); // 2 days ago
    
    const completedOverdueTask = {
      ...mockTask,
      status: 'completed',
      due_date: pastDate.toISOString().split('T')[0]
    };
    
    render(
      <Task
        task={completedOverdueTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Check that the task does not have the overdue class
    const taskElement = screen.getByTestId('task-1');
    expect(taskElement).not.toHaveClass('overdue');
  });
  
  test('handles missing optional props gracefully', () => {
    // Create task without description and due date
    const minimalTask = {
      id: 1,
      title: 'Minimal Task',
      status: 'pending'
    };
    
    render(
      <Task
        task={minimalTask}
        onToggleComplete={mockToggleComplete}
        onDelete={mockDelete}
      />
    );
    
    // Check that the component renders without errors
    expect(screen.getByText('Minimal Task')).toBeInTheDocument();
    
    // Ensure optional elements are not rendered
    expect(screen.queryByText(/Description/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Due:/)).not.toBeInTheDocument();
  });
});
```

### Testing a Container Component

Now let's create and test a TaskList component that manages multiple tasks:

```jsx
// src/components/TaskList/TaskList.jsx
import React, { useState, useEffect } from 'react';
import Task from '../Task/Task';
import './TaskList.css';

const TaskList = ({ initialTasks = [] }) => {
  const [tasks, setTasks] = useState(initialTasks);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // If initialTasks are provided, use them
    if (initialTasks.length > 0) {
      setTasks(initialTasks);
      setLoading(false);
      return;
    }
    
    // Otherwise fetch from API
    const fetchTasks = async () => {
      try {
        const response = await fetch('/api/tasks/');
        if (!response.ok) {
          throw new Error('Failed to fetch tasks');
        }
        
        const data = await response.json();
        setTasks(data);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };
    
    fetchTasks();
  }, [initialTasks]);
  
  const handleToggleComplete = async (taskId) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      const newStatus = task.status === 'completed' ? 'pending' : 'completed';
      
      const response = await fetch(`/api/tasks/${taskId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (!response.ok) {
        throw new Error('Failed to update task');
      }
      
      const updatedTask = await response.json();
      
      setTasks(tasks.map(t => 
        t.id === taskId ? updatedTask : t
      ));
    } catch (error) {
      setError(error.message);
    }
  };
  
  const handleDeleteTask = async (taskId) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete task');
      }
      
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (error) {
      setError(error.message);
    }
  };
  
  if (loading) return <div data-testid="loading">Loading tasks...</div>;
  if (error) return <div data-testid="error">Error: {error}</div>;
  
  return (
    <div className="task-list" data-testid="task-list">
      <h2>Your Tasks</h2>
      
      {tasks.length === 0 ? (
        <p data-testid="no-tasks-message">No tasks found</p>
      ) : (
        <div className="tasks-container">
          {tasks.map(task => (
            <Task
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDeleteTask}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;
```

Now, let's test this component:

```jsx
// src/components/TaskList/TaskList.test.jsx
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskList from './TaskList';

// Mock the Task component to simplify testing
jest.mock('../Task/Task', () => {
  return function MockTask({ task, onToggleComplete, onDelete }) {
    return (
      <div data-testid={`task-${task.id}`} className={`task ${task.status}`}>
        <h3>{task.title}</h3>
        <button 
          onClick={() => onToggleComplete(task.id)}
          data-testid={`toggle-${task.id}`}
        >
          Toggle
        </button>
        <button 
          onClick={() => onDelete(task.id)}
          data-testid={`delete-${task.id}`}
        >
          Delete
        </button>
      </div>
    );
  };
});

// Mock fetch API
global.fetch = jest.fn();

describe('TaskList Component', () => {
  const mockTasks = [
    {
      id: 1,
      title: 'Task 1',
      description: 'Description 1',
      status: 'pending',
      due_date: '2023-12-31'
    },
    {
      id: 2,
      title: 'Task 2',
      description: 'Description 2',
      status: 'completed',
      due_date: '2023-11-30'
    }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders loading state initially when no initialTasks provided', () => {
    // Mock fetch to never resolve during this test
    global.fetch.mockImplementation(() => new Promise(() => {}));
    
    render(<TaskList />);
    
    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });
  
  test('renders tasks when initialTasks are provided', () => {
    render(<TaskList initialTasks={mockTasks} />);
    
    // Should render both tasks
    expect(screen.getByTestId('task-1')).toBeInTheDocument();
    expect(screen.getByTestId('task-2')).toBeInTheDocument();
    
    // Should not show loading or error state
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
  });
  
  test('renders tasks from API when no initialTasks provided', async () => {
    // Mock successful fetch
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks
    });
    
    render(<TaskList />);
    
    // Should show loading initially
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    
    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });
    
    // Should render both tasks
    expect(screen.getByTestId('task-1')).toBeInTheDocument();
    expect(screen.getByTestId('task-2')).toBeInTheDocument();
  });
  
  test('renders error state when API fetch fails', async () => {
    // Mock failed fetch
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    
    render(<TaskList />);
    
    // Wait for error to display
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });
    
    expect(screen.getByTestId('error')).toBeInTheDocument();
    expect(screen.getByText(/Network error/)).toBeInTheDocument();
  });
  
  test('handles task completion toggle', async () => {
    // Mock initial tasks
    render(<TaskList initialTasks={mockTasks} />);
    
    // Mock successful PATCH request
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ...mockTasks[0],
        status: 'completed'
      })
    });
    
    // Toggle the first task
    fireEvent.click(screen.getByTestId('toggle-1'));
    
    // Check that fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'completed' })
    });
    
    // Wait for the task to update
    await waitFor(() => {
      // Check that the task's class has been updated
      const taskElement = screen.getByTestId('task-1');
      expect(taskElement).toHaveClass('completed');
      expect(taskElement).not.toHaveClass('pending');
    });
  });
  
  test('handles task deletion', async () => {
    // Mock initial tasks
    render(<TaskList initialTasks={mockTasks} />);
    
    // Mock successful DELETE request
    global.fetch.mockResolvedValueOnce({
      ok: true
    });
    
    // Delete the first task
    fireEvent.click(screen.getByTestId('delete-1'));
    
    // Check that fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
      method: 'DELETE'
    });
    
    // Wait for the task to be removed
    await waitFor(() => {
      expect(screen.queryByTestId('task-1')).not.toBeInTheDocument();
    });
    
    // The second task should still be there
    expect(screen.getByTestId('task-2')).toBeInTheDocument();
  });
  
  test('renders no tasks message when there are no tasks', async () => {
    // Mock successful fetch with empty array
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    });
    
    render(<TaskList />);
    
    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });
    
    // Should show no tasks message
    expect(screen.getByTestId('no-tasks-message')).toBeInTheDocument();
    expect(screen.getByText('No tasks found')).toBeInTheDocument();
  });
  
  test('shows error message when toggle fails', async () => {
    // Mock initial tasks
    render(<TaskList initialTasks={mockTasks} />);
    
    // Mock failed PATCH request
    global.fetch.mockRejectedValueOnce(new Error('Update failed'));
    
    // Toggle the first task
    fireEvent.click(screen.getByTestId('toggle-1'));
    
    // Wait for error to display
    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
      expect(screen.getByText(/Update failed/)).toBeInTheDocument();
    });
  });
});
```

## Hook Testing

Hook tests verify that your custom React hooks manage state and side effects correctly.

Let's create and test a custom hook for task management:

```jsx
// src/hooks/useTaskManager.js
import { useState, useEffect, useCallback } from 'react';

export const useTaskManager = (initialTasks = []) => {
  const [tasks, setTasks] = useState(initialTasks);
  const [loading, setLoading] = useState(initialTasks.length === 0);
  const [error, setError] = useState(null);
  
  const fetchTasks = useCallback(async () => {
    // Skip fetching if initialTasks are provided
    if (initialTasks.length > 0) {
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/tasks/');
      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.statusText}`);
      }
      
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [initialTasks]);
  
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);
  
  const addTask = useCallback(async (newTask) => {
    try {
      setError(null);
      
      const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newTask)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to add task: ${response.statusText}`);
      }
      
      const addedTask = await response.json();
      setTasks(prevTasks => [...prevTasks, addedTask]);
      return addedTask;
    } catch (error) {
      setError(error.message);
      return null;
    }
  }, []);
  
  const updateTask = useCallback(async (taskId, updates) => {
    try {
      setError(null);
      
      const response = await fetch(`/api/tasks/${taskId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update task: ${response.statusText}`);
      }
      
      const updatedTask = await response.json();
      setTasks(prevTasks => 
        prevTasks.map(task => task.id === taskId ? updatedTask : task)
      );
      return updatedTask;
    } catch (error) {
      setError(error.message);
      return null;
    }
  }, []);
  
  const deleteTask = useCallback(async (taskId) => {
    try {
      setError(null);
      
      const response = await fetch(`/api/tasks/${taskId}/`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete task: ${response.statusText}`);
      }
      
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      return true;
    } catch (error) {
      setError(error.message);
      return false;
    }
  }, []);
  
  const toggleTaskCompletion = useCallback(async (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return null;
    
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    return updateTask(taskId, { status: newStatus });
  }, [tasks, updateTask]);
  
  return {
    tasks,
    loading,
    error,
    fetchTasks,
    addTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion
  };
};
```

Now let's test this hook:

```jsx
// src/hooks/useTaskManager.test.js
import { renderHook, act } from '@testing-library/react-hooks';
import { useTaskManager } from './useTaskManager';

// Mock fetch API
global.fetch = jest.fn();

describe('useTaskManager Hook', () => {
  const mockTasks = [
    { id: 1, title: 'Task 1', status: 'pending' },
    { id: 2, title: 'Task 2', status: 'completed' }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('initializes with loading state when no initialTasks provided', () => {
    // Mock fetch that never resolves for this test
    global.fetch.mockImplementation(() => new Promise(() => {}));
    
    const { result } = renderHook(() => useTaskManager());
    
    expect(result.current.loading).toBe(true);
    expect(result.current.tasks).toEqual([]);
    expect(result.current.error).toBeNull();
  });
  
  test('initializes with provided initialTasks', () => {
    const { result } = renderHook(() => useTaskManager(mockTasks));
    
    expect(result.current.loading).toBe(false);
    expect(result.current.tasks).toEqual(mockTasks);
    expect(result.current.error).toBeNull();
    
    // Should not try to fetch tasks
    expect(global.fetch).not.toHaveBeenCalled();
  });
  
  test('fetches tasks from API when no initialTasks provided', async () => {
    // Mock successful fetch
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks
    });
    
    const { result, waitForNextUpdate } = renderHook(() => useTaskManager());
    
    // Initially in loading state
    expect(result.current.loading).toBe(true);
    
    // Wait for the fetch to complete
    await waitForNextUpdate();
    
    // Should have loaded tasks
    expect(result.current.loading).toBe(false);
    expect(result.current.tasks).toEqual(mockTasks);
    expect(result.current.error).toBeNull();
    
    // Should have made the fetch call
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/');
  });
  
  test('handles fetch error', async () => {
    // Mock failed fetch
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    
    const { result, waitForNextUpdate } = renderHook(() => useTaskManager());
    
    // Wait for the fetch to fail
    await waitForNextUpdate();
    
    // Should have error state
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Network error');
    expect(result.current.tasks).toEqual([]);
  });
  
  test('adds a new task', async () => {
    // Start with initialTasks to skip initial fetch
    const { result } = renderHook(() => useTaskManager(mockTasks));
    
    const newTask = { title: 'New Task', status: 'pending' };
    const addedTask = { id: 3, ...newTask };
    
    // Mock successful POST
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => addedTask
    });
    
    // Add the task
    let taskResult;
    await act(async () => {
      taskResult = await result.current.addTask(newTask);
    });
    
    // Check that fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newTask)
    });
    
    // Check the result
    expect(taskResult).toEqual(addedTask);
    
    // Check that tasks were updated
    expect(result.current.tasks).toHaveLength(3);
    expect(result.current.tasks[2]).toEqual(addedTask);
  });
  
  test('updates an existing task', async () => {
    // Start with initialTasks
    const { result } = renderHook(() => useTaskManager(mockTasks));
    
    const updates = { title: 'Updated Task 1' };
    const updatedTask = { ...mockTasks[0], ...updates };
    
    // Mock successful PATCH
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => updatedTask
    });
    
    // Update the task
    let taskResult;
    await act(async () => {
      taskResult = await result.current.updateTask(1, updates);
    });
    
    // Check that fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updates)
    });
    
    // Check the result
    expect(taskResult).toEqual(updatedTask);
    
    // Check that tasks were updated
    expect(result.current.tasks[0].title).toBe('Updated Task 1');
  });
  
  test('deletes a task', async () => {
    // Start with initialTasks
    const { result } = renderHook(() => useTaskManager(mockTasks));
    
    // Mock successful DELETE
    global.fetch.mockResolvedValueOnce({
      ok: true
    });
    
    // Delete the task
    let deleteResult;
    await act(async () => {
      deleteResult = await result.current.deleteTask(1);
    });
    
    // Check that fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
      method: 'DELETE'
    });
    
    // Check the result
    expect(deleteResult).toBe(true);
    
    // Check that tasks were updated
    expect(result.current.tasks).toHaveLength(1);
    expect(result.current.tasks[0].id).toBe(2);
  });
  
  test('toggles task completion status', async () => {
    // Start with initialTasks
    const { result } = renderHook(() => useTaskManager(mockTasks));
    
    // First task is pending, should be toggled to completed
    const updatedTask = { ...mockTasks[0], status: 'completed' };
    
    // Mock successful PATCH
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => updatedTask
    });
    
    // Toggle the task
    await act(async () => {
      await result.current.toggleTaskCompletion(1);
    });
    
    // Check that fetch was called correctly
    expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'completed' })
    });
    
    // Check that tasks were updated
    expect(result.current.tasks[0].status).toBe('completed');
  });
  
  test('handles error when adding task', async () => {
    // Start with initialTasks
    const { result } = renderHook(() => useTaskManager(mockTasks));
    
    // Mock failed POST
    global.fetch.mockRejectedValueOnce(new Error('Failed to add task'));
    
    // Try to add a task
    let taskResult;
    await act(async () => {
      taskResult = await result.current.addTask({ title: 'New Task' });
    });
    
    // Check the result
    expect(taskResult).toBeNull();
    
    // Check error state
    expect(result.current.error).toBe('Failed to add task');
    
    // Tasks should not have changed
    expect(result.current.tasks).toEqual(mockTasks);
  });
});
```

## State Management Testing

Testing state management includes Redux reducers, actions, selectors, and store integration.

### Redux Store Testing

Let's create Redux state management for our tasks and test it:

```jsx
// src/redux/slices/tasksSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/tasks/');
      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const addTask = createAsyncThunk(
  'tasks/addTask',
  async (task, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(task)
      });
      
      if (!response.ok) {
        throw new Error('Failed to add task');
      }
      
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateTask = createAsyncThunk(
  'tasks/updateTask',
  async ({ taskId, updates }, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update task');
      }
      
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const deleteTask = createAsyncThunk(
  'tasks/deleteTask',
  async (taskId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete task');
      }
      
      return taskId;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: {
    items: [],
    status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null
  },
  reducers: {
    clearTasksError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks cases
      .addCase(fetchTasks.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;
        state.error = null;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      
      // Add task cases
      .addCase(addTask.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(addTask.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items.push(action.payload);
        state.error = null;
      })
      .addCase(addTask.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      
      // Update task cases
      .addCase(updateTask.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(updateTask.fulfilled, (state, action) => {
        state.status = 'succeeded';
        const index = state.items.findIndex(task => task.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        state.error = null;
      })
      .addCase(updateTask.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      
      // Delete task cases
      .addCase(deleteTask.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(deleteTask.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = state.items.filter(task => task.id !== action.payload);
        state.error = null;
      })
      .addCase(deleteTask.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { clearTasksError } = tasksSlice.actions;

export default tasksSlice.reducer;

// Selectors
export const selectAllTasks = (state) => state.tasks.items;
export const selectTaskById = (state, taskId) => 
  state.tasks.items.find(task => task.id === taskId);
export const selectTasksStatus = (state) => state.tasks.status;
export const selectTasksError = (state) => state.tasks.error;
export const selectCompletedTasks = (state) => 
  state.tasks.items.filter(task => task.status === 'completed');
export const selectPendingTasks = (state) => 
  state.tasks.items.filter(task => task.status === 'pending');
```

Now let's test this Redux slice:

```jsx
// src/redux/slices/tasksSlice.test.js
import tasksReducer, {
  fetchTasks,
  addTask,
  updateTask,
  deleteTask,
  clearTasksError,
  selectAllTasks,
  selectTaskById,
  selectTasksStatus,
  selectTasksError,
  selectCompletedTasks,
  selectPendingTasks
} from './tasksSlice';
import { configureStore } from '@reduxjs/toolkit';

// Mock fetch API
global.fetch = jest.fn();

describe('Tasks Slice', () => {
  const initialState = {
    items: [],
    status: 'idle',
    error: null
  };
  
  const mockTasks = [
    { id: 1, title: 'Task 1', status: 'pending' },
    { id: 2, title: 'Task 2', status: 'completed' }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  // Reducer Tests
  describe('Reducer', () => {
    test('returns initial state', () => {
      expect(tasksReducer(undefined, { type: undefined })).toEqual(initialState);
    });
    
    test('clears error state', () => {
      const stateWithError = {
        ...initialState,
        error: 'Some error'
      };
      
      expect(tasksReducer(stateWithError, clearTasksError())).toEqual({
        ...stateWithError,
        error: null
      });
    });
  });
  
  // Thunk Tests
  describe('Thunks', () => {
    let store;
    
    beforeEach(() => {
      store = configureStore({
        reducer: {
          tasks: tasksReducer
        }
      });
    });
    
    test('fetchTasks - successful', async () => {
      // Mock successful fetch
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTasks
      });
      
      // Dispatch the thunk
      await store.dispatch(fetchTasks());
      
      // Check state after dispatch
      const state = store.getState().tasks;
      expect(state.status).toBe('succeeded');
      expect(state.items).toEqual(mockTasks);
      expect(state.error).toBeNull();
      
      // Check that fetch was called correctly
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith('/api/tasks/');
    });
    
    test('fetchTasks - failed', async () => {
      // Mock failed fetch
      global.fetch.mockRejectedValueOnce(new Error('Network error'));
      
      // Dispatch the thunk
      await store.dispatch(fetchTasks());
      
      // Check state after dispatch
      const state = store.getState().tasks;
      expect(state.status).toBe('failed');
      expect(state.error).toContain('Network error');
      expect(state.items).toEqual([]);
    });
    
    test('addTask - successful', async () => {
      // Start with some tasks
      store = configureStore({
        reducer: {
          tasks: tasksReducer
        },
        preloadedState: {
          tasks: {
            ...initialState,
            items: [...mockTasks]
          }
        }
      });
      
      const newTask = { title: 'New Task', status: 'pending' };
      const addedTask = { id: 3, ...newTask };
      
      // Mock successful fetch
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => addedTask
      });
      
      // Dispatch the thunk
      await store.dispatch(addTask(newTask));
      
      // Check state after dispatch
      const state = store.getState().tasks;
      expect(state.status).toBe('succeeded');
      expect(state.items).toHaveLength(3);
      expect(state.items[2]).toEqual(addedTask);
      
      // Check that fetch was called correctly
      expect(global.fetch).toHaveBeenCalledWith('/api/tasks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newTask)
      });
    });
    
    test('updateTask - successful', async () => {
      // Start with some tasks
      store = configureStore({
        reducer: {
          tasks: tasksReducer
        },
        preloadedState: {
          tasks: {
            ...initialState,
            items: [...mockTasks]
          }
        }
      });
      
      const taskId = 1;
      const updates = { title: 'Updated Task 1' };
      const updatedTask = { ...mockTasks[0], ...updates };
      
      // Mock successful fetch
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => updatedTask
      });
      
      // Dispatch the thunk
      await store.dispatch(updateTask({ taskId, updates }));
      
      // Check state after dispatch
      const state = store.getState().tasks;
      expect(state.status).toBe('succeeded');
      expect(state.items[0].title).toBe('Updated Task 1');
      
      // Check that fetch was called correctly
      expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
    });
    
    test('deleteTask - successful', async () => {
      // Start with some tasks
      store = configureStore({
        reducer: {
          tasks: tasksReducer
        },
        preloadedState: {
          tasks: {
            ...initialState,
            items: [...mockTasks]
          }
        }
      });
      
      const taskId = 1;
      
      // Mock successful fetch
      global.fetch.mockResolvedValueOnce({
        ok: true
      });
      
      // Dispatch the thunk
      await store.dispatch(deleteTask(taskId));
      
      // Check state after dispatch
      const state = store.getState().tasks;
      expect(state.status).toBe('succeeded');
      expect(state.items).toHaveLength(1);
      expect(state.items[0].id).toBe(2);
      
      // Check that fetch was called correctly
      expect(global.fetch).toHaveBeenCalledWith('/api/tasks/1/', {
        method: 'DELETE'
      });
    });
  });
  
  // Selector Tests
  describe('Selectors', () => {
    const state = {
      tasks: {
        items: mockTasks,
        status: 'succeeded',
        error: null
      }
    };
    
    test('selectAllTasks returns all tasks', () => {
      expect(selectAllTasks(state)).toEqual(mockTasks);
    });
    
    test('selectTaskById returns task with matching id', () => {
      expect(selectTaskById(state, 1)).toEqual(mockTasks[0]);
      expect(selectTaskById(state, 999)).toBeUndefined();
    });
    
    test('selectTasksStatus returns status', () => {
      expect(selectTasksStatus(state)).toBe('succeeded');
    });
    
    test('selectTasksError returns error', () => {
      expect(selectTasksError(state)).toBeNull();
      
      const stateWithError = {
        tasks: {
          ...state.tasks,
          error: 'Some error'
        }
      };
      
      expect(selectTasksError(stateWithError)).toBe('Some error');
    });
    
    test('selectCompletedTasks returns only completed tasks', () => {
      const completedTasks = selectCompletedTasks(state);
      expect(completedTasks).toHaveLength(1);
      expect(completedTasks[0].id).toBe(2);
    });
    
    test('selectPendingTasks returns only pending tasks', () => {
      const pendingTasks = selectPendingTasks(state);
      expect(pendingTasks).toHaveLength(1);
      expect(pendingTasks[0].id).toBe(1);
    });
  });
});
```

### Testing a Component with Redux

Now let's test a component that uses our Redux store:

```jsx
// src/components/TaskManager/TaskManager.jsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchTasks,
  addTask,
  updateTask,
  deleteTask,
  selectAllTasks,
  selectTasksStatus,
  selectTasksError
} from '../../redux/slices/tasksSlice';
import Task from '../Task/Task';
import TaskForm from '../TaskForm/TaskForm';
import './TaskManager.css';

const TaskManager = () => {
  const dispatch = useDispatch();
  const tasks = useSelector(selectAllTasks);
  const status = useSelector(selectTasksStatus);
  const error = useSelector(selectTasksError);
  
  useEffect(() => {
    if (status === 'idle') {
      dispatch(fetchTasks());
    }
  }, [status, dispatch]);
  
  const handleAddTask = (newTask) => {
    dispatch(addTask(newTask));
  };
  
  const handleToggleComplete = (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    dispatch(updateTask({ taskId, updates: { status: newStatus } }));
  };
  
  const handleDeleteTask = (taskId) => {
    dispatch(deleteTask(taskId));
  };
  
  if (status === 'loading') {
    return <div data-testid="loading">Loading tasks...</div>;
  }
  
  return (
    <div className="task-manager" data-testid="task-manager">
      <h1>Task Manager</h1>
      
      {error && (
        <div className="error-message" data-testid="error-message">
          Error: {error}
        </div>
      )}
      
      <TaskForm onAddTask={handleAddTask} />
      
      <div className="tasks-container">
        <h2>Your Tasks</h2>
        
        {tasks.length === 0 ? (
          <p data-testid="no-tasks-message">No tasks found</p>
        ) : (
          tasks.map(task => (
            <Task
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDeleteTask}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default TaskManager;
```

Let's test this component with Redux:

```jsx
// src/components/TaskManager/TaskManager.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import tasksReducer, {
  fetchTasks,
  addTask,
  updateTask,
  deleteTask
} from '../../redux/slices/tasksSlice';
import TaskManager from './TaskManager';

// Mock Task component
jest.mock('../Task/Task', () => {
  return function MockTask({ task, onToggleComplete, onDelete }) {
    return (
      <div data-testid={`task-${task.id}`}>
        <span>{task.title}</span>
        <button
          onClick={() => onToggleComplete(task.id)}
          data-testid={`toggle-${task.id}`}
        >
          Toggle
        </button>
        <button
          onClick={() => onDelete(task.id)}
          data-testid={`delete-${task.id}`}
        >
          Delete
        </button>
      </div>
    );
  };
});

// Mock TaskForm component
jest.mock('../TaskForm/TaskForm', () => {
  return function MockTaskForm({ onAddTask }) {
    return (
      <div data-testid="task-form">
        <button
          onClick={() => onAddTask({ title: 'New Task', status: 'pending' })}
          data-testid="add-task-button"
        >
          Add Task
        </button>
      </div>
    );
  };
});

// Mock Redux thunks
jest.mock('../../redux/slices/tasksSlice', () => {
  const actual = jest.requireActual('../../redux/slices/tasksSlice');
  return {
    ...actual,
    fetchTasks: jest.fn(),
    addTask: jest.fn(),
    updateTask: jest.fn(),
    deleteTask: jest.fn()
  };
});

describe('TaskManager Component', () => {
  const mockTasks = [
    { id: 1, title: 'Task 1', status: 'pending' },
    { id: 2, title: 'Task 2', status: 'completed' }
  ];
  
  let store;
  
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock thunk action creators
    fetchTasks.mockReturnValue({ type: 'tasks/fetchTasks/fulfilled', payload: mockTasks });
    addTask.mockReturnValue({ type: 'tasks/addTask/fulfilled', payload: { id: 3, title: 'New Task', status: 'pending' } });
    updateTask.mockReturnValue({ type: 'tasks/updateTask/fulfilled', payload: { ...mockTasks[0], status: 'completed' } });
    deleteTask.mockReturnValue({ type: 'tasks/deleteTask/fulfilled', payload: 1 });
    
    // Create fresh store for each test
    store = configureStore({
      reducer: {
        tasks: tasksReducer
      },
      preloadedState: {
        tasks: {
          items: [...mockTasks],
          status: 'succeeded',
          error: null
        }
      }
    });
  });
  
  test('renders task list correctly', () => {
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Check heading
    expect(screen.getByText('Task Manager')).toBeInTheDocument();
    
    // Check task form
    expect(screen.getByTestId('task-form')).toBeInTheDocument();
    
    // Check tasks are rendered
    expect(screen.getByTestId('task-1')).toBeInTheDocument();
    expect(screen.getByTestId('task-2')).toBeInTheDocument();
  });
  
  test('fetches tasks on mount when status is idle', () => {
    // Create store with idle status
    store = configureStore({
      reducer: {
        tasks: tasksReducer
      },
      preloadedState: {
        tasks: {
          items: [],
          status: 'idle',
          error: null
        }
      }
    });
    
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Should dispatch fetchTasks
    expect(fetchTasks).toHaveBeenCalledTimes(1);
  });
  
  test('displays loading state', () => {
    // Create store with loading status
    store = configureStore({
      reducer: {
        tasks: tasksReducer
      },
      preloadedState: {
        tasks: {
          items: [],
          status: 'loading',
          error: null
        }
      }
    });
    
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Should show loading
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.queryByText('Task Manager')).not.toBeInTheDocument();
  });
  
  test('displays error message', () => {
    // Create store with error
    store = configureStore({
      reducer: {
        tasks: tasksReducer
      },
      preloadedState: {
        tasks: {
          items: [],
          status: 'failed',
          error: 'Failed to fetch tasks'
        }
      }
    });
    
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Should show error message
    expect(screen.getByTestId('error-message')).toBeInTheDocument();
    expect(screen.getByText(/Failed to fetch tasks/)).toBeInTheDocument();
  });
  
  test('displays no tasks message when there are no tasks', () => {
    // Create store with no tasks
    store = configureStore({
      reducer: {
        tasks: tasksReducer
      },
      preloadedState: {
        tasks: {
          items: [],
          status: 'succeeded',
          error: null
        }
      }
    });
    
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Should show no tasks message
    expect(screen.getByTestId('no-tasks-message')).toBeInTheDocument();
    expect(screen.getByText('No tasks found')).toBeInTheDocument();
  });
  
  test('adds a new task', () => {
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Click add task button
    fireEvent.click(screen.getByTestId('add-task-button'));
    
    // Should dispatch addTask
    expect(addTask).toHaveBeenCalledTimes(1);
    expect(addTask).toHaveBeenCalledWith({ title: 'New Task', status: 'pending' });
  });
  
  test('toggles task completion', () => {
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Click toggle button for task 1
    fireEvent.click(screen.getByTestId('toggle-1'));
    
    // Should dispatch updateTask with correct parameters
    expect(updateTask).toHaveBeenCalledTimes(1);
    expect(updateTask).toHaveBeenCalledWith({
      taskId: 1,
      updates: { status: 'completed' }
    });
  });
  
  test('deletes a task', () => {
    render(
      <Provider store={store}>
        <TaskManager />
      </Provider>
    );
    
    // Click delete button for task 1
    fireEvent.click(screen.getByTestId('delete-1'));
    
    // Should dispatch deleteTask
    expect(deleteTask).toHaveBeenCalledTimes(1);
    expect(deleteTask).toHaveBeenCalledWith(1);
  });
});
```

## API Interaction Testing

Testing API interactions with Mock Service Worker (MSW) ensures your components handle API responses correctly.

Let's create a component that fetches data from an API:

```jsx
// src/components/TaskDashboard/TaskDashboard.jsx
import React, { useState, useEffect } from 'react';
import './TaskDashboard.css';

const TaskDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('/api/tasks/stats/');
        if (!response.ok) {
          throw new Error(`Failed to fetch stats: ${response.statusText}`);
        }
        
        const data = await response.json();
        setStats(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);
  
  if (loading) return <div data-testid="loading">Loading dashboard...</div>;
  if (error) return <div data-testid="error">Error: {error}</div>;
  if (!stats) return <div data-testid="no-data">No data available</div>;
  
  return (
    <div className="task-dashboard" data-testid="task-dashboard">
      <h1>Task Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card total" data-testid="total-tasks">
          <h3>Total Tasks</h3>
          <p className="stat-value">{stats.total_tasks}</p>
        </div>
        
        <div className="stat-card completed" data-testid="completed-tasks">
          <h3>Completed</h3>
          <p className="stat-value">{stats.completed_tasks}</p>
          <p className="stat-percentage">
            ({Math.round((stats.completed_tasks / stats.total_tasks) * 100) || 0}%)
          </p>
        </div>
        
        <div className="stat-card pending" data-testid="pending-tasks">
          <h3>Pending</h3>
          <p className="stat-value">{stats.pending_tasks}</p>
        </div>
        
        <div className="stat-card overdue" data-testid="overdue-tasks">
          <h3>Overdue</h3>
          <p className="stat-value">{stats.overdue_tasks}</p>
        </div>
      </div>
      
      {stats.recent_activity && stats.recent_activity.length > 0 && (
        <div className="recent-activity" data-testid="recent-activity">
          <h2>Recent Activity</h2>
          <ul>
            {stats.recent_activity.map((activity, index) => (
              <li key={index}>{activity.description}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default TaskDashboard;
```

Now let's set up MSW to test this component:

```jsx
// src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  // Other handlers...
  
  // Task Stats API endpoint
  rest.get('/api/tasks/stats/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        total_tasks: 15,
        completed_tasks: 8,
        pending_tasks: 7,
        overdue_tasks: 3,
        recent_activity: [
          { 
            id: 1,
            description: 'Task "Complete project" was marked as completed',
            timestamp: '2023-04-15T10:30:00Z'
          },
          {
            id: 2,
            description: 'New task "Review code" was added',
            timestamp: '2023-04-14T16:45:00Z'
          }
        ]
      })
    );
  })
];

// src/mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

Now let's test the component with MSW:

```jsx
// src/components/TaskDashboard/TaskDashboard.test.jsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { rest } from 'msw';
import { server } from '../../mocks/server';
import TaskDashboard from './TaskDashboard';

describe('TaskDashboard Component', () => {
  // Set up MSW server before tests
  beforeAll(() => server.listen());
  
  // Reset any request handlers added during tests
  afterEach(() => server.resetHandlers());
  
  // Clean up after all tests
  afterAll(() => server.close());
  
  test('fetches and displays dashboard stats', async () => {
    render(<TaskDashboard />);
    
    // Initially should show loading
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('task-dashboard')).toBeInTheDocument();
    });
    
    // Check dashboard content
    expect(screen.getByText('Task Dashboard')).toBeInTheDocument();
    
    // Check stats
    expect(screen.getByTestId('total-tasks')).toHaveTextContent('15');
    expect(screen.getByTestId('completed-tasks')).toHaveTextContent('8');
    expect(screen.getByTestId('completed-tasks')).toHaveTextContent('53%'); // 8/15 = 0.533...
    expect(screen.getByTestId('pending-tasks')).toHaveTextContent('7');
    expect(screen.getByTestId('overdue-tasks')).toHaveTextContent('3');
    
    // Check recent activity
    expect(screen.getByTestId('recent-activity')).toBeInTheDocument();
    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    expect(screen.getByText('Task "Complete project" was marked as completed')).toBeInTheDocument();
    expect(screen.getByText('New task "Review code" was added')).toBeInTheDocument();
  });
  
  test('handles API error', async () => {
    // Override the handler to simulate an error
    server.use(
      rest.get('/api/tasks/stats/', (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({ message: 'Server error' })
        );
      })
    );
    
    render(<TaskDashboard />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Error:/)).toBeInTheDocument();
  });
  
  test('handles empty response', async () => {
    // Override the handler to simulate empty data
    server.use(
      rest.get('/api/tasks/stats/', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json({
            total_tasks: 0,
            completed_tasks: 0,
            pending_tasks: 0,
            overdue_tasks: 0,
            recent_activity: []
          })
        );
      })
    );
    
    render(<TaskDashboard />);
    
    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByTestId('task-dashboard')).toBeInTheDocument();
    });
    
    // Check stats are zero
    expect(screen.getByTestId('total-tasks')).toHaveTextContent('0');
    expect(screen.getByTestId('completed-tasks')).toHaveTextContent('0');
    expect(screen.getByTestId('completed-tasks')).toHaveTextContent('0%');
    
    // Recent activity section should not be present
    expect(screen.queryByTestId('recent-activity')).not.toBeInTheDocument();
  });
  
  test('handles network failure', async () => {
    // Override the handler to simulate network failure
    server.use(
      rest.get('/api/tasks/stats/', (req, res) => {
        return res.networkError('Failed to connect');
      })
    );
    
    render(<TaskDashboard />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Error:/)).toBeInTheDocument();
  });
});
```

## Form Testing

Form tests verify that your forms collect and validate user input correctly.

Let's create a task form and test it:

```jsx
// src/components/TaskForm/TaskForm.jsx
import React, { useState } from 'react';
import './TaskForm.css';

const TaskForm = ({ onAddTask, initialValues = {} }) => {
  const [formData, setFormData] = useState({
    title: initialValues.title || '',
    description: initialValues.description || '',
    due_date: initialValues.due_date || '',
    status: initialValues.status || 'pending'
  });
  
  const [errors, setErrors] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when field is changed
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.trim().length < 3) {
      newErrors.title = 'Title must be at least 3 characters';
    }
    
    if (formData.due_date) {
      const dueDate = new Date(formData.due_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (dueDate < today) {
        newErrors.due_date = 'Due date cannot be in the past';
      }
    }
    
    setErrors