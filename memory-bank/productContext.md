# LedgerLink - Product Context

## Project Overview

LedgerLink is a web application built with Django REST Framework (backend) and React with Material UI (frontend). It provides a comprehensive system for managing customers, orders, products, and billing for a fulfillment or logistics business.

## System Architecture

### Backend Architecture

- **Framework**: Django REST Framework
- **Database**: PostgreSQL hosted on Supabase
- **Authentication**: JWT-based authentication with token refresh
- **API Structure**: RESTful endpoints for CRUD operations
- **Logging**: Comprehensive server-side logging system

### Frontend Architecture

- **Framework**: React with hooks (functional components)
- **UI Framework**: Material UI v5 with custom theme
- **State Management**: Local React state with hooks
- **Routing**: React Router v6 with protected routes
- **Data Tables**: Material React Table
- **Build Tool**: Vite for development and production builds
- **Logging**: Client-side logging system with storage and export functionality

## Key Components

### Backend Apps

| App | Purpose |
|-----|---------|
| customers | Customer management |
| orders | Order management |
| products | Product catalog |
| services | Service offerings |
| billing | Billing and invoicing |
| rules | Business rules for pricing and conditions |
| inserts | Insertable material management |
| shipping | Shipping and logistics |
| materials | Raw materials tracking |
| bulk_operations | Bulk import/export functionality |
| customer_services | Customer-specific service configurations |

### Frontend Structure

- Components organized by feature
- Utility functions for auth, API client, and logging
- Custom hooks for reusable functionality
- Material UI components with consistent theming

## Core Functionality

- Customer management
- Order processing and tracking
- Product catalog management
- Dynamic pricing through complex rule system
- Shipping and logistics tracking
- Billing and invoicing
- Reporting and analytics
- Materialized views for performance optimization
- Comprehensive logging system

## Design Patterns and Principles

- **Backend**:
  - Django's model-serializer-view pattern
  - RESTful API design
  - Custom exception handling
  - Comprehensive logging with decorators
  - Business logic encapsulation in rule system

- **Frontend**:
  - Component-based architecture
  - Container/presentational component pattern
  - Custom hooks for reusable logic
  - Centralized API client and error handling
  - Client-side logging system

## Memory Bank Organization

This Memory Bank serves as a centralized location for project documentation, architecture decisions, and progress tracking. The core files are:

- **productContext.md**: This document - provides a comprehensive overview of the project.
- **activeContext.md**: Tracks the current session's context and recent activities.
- **progress.md**: Tracks progress and manages tasks in a structured format.
- **decisionLog.md**: Logs architectural decisions, their rationale, and implications.

Additional documentation will be added as needed to support specific architectural concerns or modules.