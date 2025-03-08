# Authentication Testing Documentation

This document outlines the testing approach and implementation for authentication functionality in the LedgerLink application.

*Created as part of the comprehensive testing implementation project. This document is referenced in TESTING_SUMMARY.md.*

## Overview

Authentication is a critical component of the LedgerLink application, providing security and access control. The testing approach covers unit testing, component testing, accessibility testing, and end-to-end testing.

## Test Structure

### Unit Tests

Unit tests for authentication focus on:

- The authentication utility functions
- Token management
- Login/logout functionality

File: `/frontend/src/utils/__tests__/auth.test.js`

### Component Tests

Component tests verify the behavior of authentication-related React components:

**Login Component**
- File: `/frontend/src/components/auth/__tests__/Login.test.jsx`
- Tests form rendering, input handling, submissions, and error display

**ProtectedRoute Component**
- File: `/frontend/src/components/auth/__tests__/ProtectedRoute.test.jsx`
- Tests route protection and authentication state handling

### Accessibility Tests

Accessibility tests ensure that authentication components are accessible to all users:

**Login Component Accessibility**
- File: `/frontend/src/components/auth/__tests__/Login.a11y.test.jsx`
- Verifies WCAG compliance using jest-axe
- Tests specific accessibility concerns: labels, color contrast, ARIA attributes

### End-to-End Tests

E2E tests verify complete authentication flows from the user's perspective:

**Authentication Flows**
- File: `/frontend/cypress/e2e/auth.cy.js`
- Tests login, logout, protected routes, error handling
- Includes accessibility checks using cypress-axe

## Test Coverage

| Component/Function  | Unit Tests | Component Tests | A11y Tests | E2E Tests |
|---------------------|------------|-----------------|------------|-----------|
| Login Component     | ✅         | ✅              | ✅         | ✅        |
| ProtectedRoute      | ✅         | ✅              | N/A        | ✅        |
| Auth Utilities      | ✅         | N/A             | N/A        | ✅        |
| Token Management    | ✅         | N/A             | N/A        | ✅        |
| Error Handling      | ✅         | ✅              | ✅         | ✅        |

## Implementation Details

### Login Component Tests

The Login component tests cover:

1. **Rendering tests**:
   - Verify that all form elements render correctly
   - Check for presence of username field, password field, and submit button

2. **Interaction tests**:
   - Verify that input values are updated on change
   - Test form submission with valid credentials
   - Test form submission with invalid credentials
   - Verify error message display
   - Test error clearing on re-submission

3. **Accessibility tests**:
   - Test overall component accessibility using axe
   - Verify form labeling
   - Check color contrast
   - Validate ARIA attributes

Example test:
```jsx
test('shows error message on login failure', async () => {
  // Mock login to reject
  auth.login.mockRejectedValueOnce(new Error('Invalid credentials'));
  
  renderLogin();
  
  // Fill in the form
  fireEvent.change(screen.getByLabelText(/username/i), { 
    target: { value: 'wronguser' } 
  });
  fireEvent.change(screen.getByLabelText(/password/i), { 
    target: { value: 'wrongpass' } 
  });
  
  // Submit the form
  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
  
  // Check for error message
  await waitFor(() => {
    expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
  });
});
```

### ProtectedRoute Component Tests

The ProtectedRoute component tests focus on:

1. **Child rendering**:
   - Verify that child components are rendered
   - Test with multiple children

2. **Authentication state handling**:
   - Test behavior with existing token
   - Test behavior without token
   - Verify development token setting

### Auth Utilities Tests

The auth utility tests cover:

1. **Token management**:
   - Setting and retrieving tokens
   - Clearing tokens
   - Authentication state checking

2. **API Integration**:
   - Login API interactions
   - Token refresh functionality 
   - Error handling

3. **Event handling**:
   - Authentication state change events

### End-to-End Tests

The E2E tests verify complete user flows:

1. **Login flow**:
   - Display of login form
   - Form submission
   - Error handling
   - Successful authentication
   - Redirect after login

2. **Protected route access**:
   - Redirect to login when unauthenticated
   - Access to routes when authenticated

3. **Logout flow**:
   - Token clearing
   - Redirect to login

4. **Accessibility**:
   - WCAG compliance of login form
   - Accessibility in various states (empty, filled, error)

## Running the Tests

### Unit and Component Tests

```bash
# Run all authentication tests
npm test -- auth

# Run specific test file
npm test -- Login.test.jsx

# Run with coverage
npm test -- auth --coverage
```

### End-to-End Tests

```bash
# Run E2E tests with UI
npm run cypress:open

# Run auth E2E tests headlessly
npm run cypress:run -- --spec "cypress/e2e/auth.cy.js"
```

## Best Practices

1. **Mock dependencies**: Authentication tests mock API calls and storage
2. **Test error cases**: Cover both success and failure paths
3. **Verify state changes**: Check that tokens are properly stored/removed
4. **Accessibility testing**: Include both component-level and E2E accessibility tests
5. **Isolated tests**: Reset state between tests for independence