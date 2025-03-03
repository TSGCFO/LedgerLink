import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Create a theme for consistent UI in tests
const theme = createTheme();

/**
 * Custom render function that wraps components with necessary providers
 * for testing (Router, ThemeProvider, etc.)
 * 
 * @param {React.ReactElement} ui - The component to render
 * @param {Object} options - Additional render options
 * @returns {Object} The render result object
 */
const customRender = (ui, options = {}) => {
  const AllProviders = ({ children }) => {
    return (
      <Router>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </Router>
    );
  };
  
  return render(ui, { wrapper: AllProviders, ...options });
};

// Re-export everything from React Testing Library
export * from '@testing-library/react';

// Override the render method
export { customRender as render };