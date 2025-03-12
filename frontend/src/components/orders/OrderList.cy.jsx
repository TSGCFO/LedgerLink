import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import OrderList from './OrderList';

const theme = createTheme();

// Mock data
const mockOrders = {
  count: 3,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      order_number: 'ORD-001',
      customer: {
        id: 1,
        company_name: 'Test Company',
      },
      order_date: '2025-03-01T10:00:00Z',
      status: 'pending',
      priority: 'normal',
      shipping_method: 'Standard',
    },
    {
      id: 2,
      order_number: 'ORD-002',
      customer: {
        id: 2,
        company_name: 'Another Company',
      },
      order_date: '2025-03-02T10:00:00Z',
      status: 'in_progress',
      priority: 'high',
      shipping_method: 'Express',
    },
    {
      id: 3,
      order_number: 'ORD-003',
      customer: {
        id: 1,
        company_name: 'Test Company',
      },
      order_date: '2025-03-03T10:00:00Z',
      status: 'completed',
      priority: 'normal',
      shipping_method: 'Standard',
    }
  ]
};

const mockStatusCounts = {
  pending: 10,
  in_progress: 5,
  completed: 20,
  cancelled: 2,
};

describe('OrderList.cy.jsx', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/v1/orders**', {
      statusCode: 200,
      body: mockOrders
    }).as('getOrders');
    
    cy.intercept('GET', '/api/v1/orders/status_counts/', {
      statusCode: 200,
      body: mockStatusCounts
    }).as('getStatusCounts');
    
    // Mock filtered results
    cy.intercept('GET', '/api/v1/orders/?status=pending**', {
      statusCode: 200,
      body: {
        ...mockOrders,
        results: mockOrders.results.filter(o => o.status === 'pending')
      }
    }).as('getPendingOrders');
    
    // Mock localStorage for auth token
    cy.window().then(win => {
      win.localStorage.setItem('auth_token', 'fake-token');
    });
  });
  
  it('renders properly and displays orders', () => {
    cy.mount(
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <OrderList />
        </BrowserRouter>
      </ThemeProvider>
    );
    
    // Wait for API calls to complete
    cy.wait('@getOrders');
    cy.wait('@getStatusCounts');
    
    // Check title
    cy.get('h1').should('contain', 'Orders');
    
    // Check filter chips
    cy.contains('pending (10)').should('be.visible');
    cy.contains('in progress (5)').should('be.visible');
    cy.contains('completed (20)').should('be.visible');
    
    // Check table headers
    cy.contains('Order Number').should('be.visible');
    cy.contains('Customer').should('be.visible');
    cy.contains('Status').should('be.visible');
    
    // Check order data
    cy.contains('ORD-001').should('be.visible');
    cy.contains('ORD-002').should('be.visible');
    cy.contains('ORD-003').should('be.visible');
    cy.contains('Test Company').should('be.visible');
    cy.contains('Another Company').should('be.visible');
  });
  
  it('filters orders when status chip is clicked', () => {
    cy.mount(
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <OrderList />
        </BrowserRouter>
      </ThemeProvider>
    );
    
    // Wait for initial API calls
    cy.wait('@getOrders');
    cy.wait('@getStatusCounts');
    
    // Click on the pending filter
    cy.contains('pending (10)').click();
    
    // Wait for filtered API call
    cy.wait('@getPendingOrders');
    
    // Should only show pending orders
    cy.contains('ORD-001').should('be.visible');
    cy.contains('ORD-002').should('not.exist');
    cy.contains('ORD-003').should('not.exist');
  });
  
  it('has accessible table with correct ARIA attributes', () => {
    cy.mount(
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <OrderList />
        </BrowserRouter>
      </ThemeProvider>
    );
    
    // Wait for API calls to complete
    cy.wait('@getOrders');
    cy.wait('@getStatusCounts');
    
    // Table should have correct role
    cy.get('table').should('have.attr', 'role', 'grid');
    
    // Headers should have correct role
    cy.get('th').each(header => {
      cy.wrap(header).should('have.attr', 'role', 'columnheader');
    });
    
    // Rows should have correct role
    cy.get('tbody tr').each(row => {
      cy.wrap(row).should('have.attr', 'role', 'row');
    });
    
    // Cells should have correct role
    cy.get('tbody td').each(cell => {
      cy.wrap(cell).should('have.attr', 'role', 'cell');
    });
  });
});