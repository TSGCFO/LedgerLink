import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';

// Add jest-axe custom matchers
expect.extend(toHaveNoViolations);

// Mock the auth utilities
jest.mock('../../../utils/auth', () => ({
  login: jest.fn(),
}));

// Mock navigation
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('Login Component - Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should have accessible form labels', async () => {
    const { container } = render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    // Check specifically for form labeling issues
    const results = await axe(container, {
      rules: {
        'label': { enabled: true },
        'label-content-name-mismatch': { enabled: true },
      }
    });
    
    expect(results).toHaveNoViolations();
  });
  
  it('should have sufficient color contrast', async () => {
    const { container } = render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    // Check specifically for color contrast issues
    const results = await axe(container, {
      rules: {
        'color-contrast': { enabled: true },
      }
    });
    
    expect(results).toHaveNoViolations();
  });
  
  it('should have correct ARIA attributes', async () => {
    const { container } = render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    // Check specifically for ARIA issues
    const results = await axe(container, {
      rules: {
        'aria-allowed-attr': { enabled: true },
        'aria-required-attr': { enabled: true },
        'aria-valid-attr': { enabled: true },
      }
    });
    
    expect(results).toHaveNoViolations();
  });
});