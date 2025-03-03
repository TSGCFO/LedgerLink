# LedgerLink Project: Product Context

## Project Overview

LedgerLink is a web application built with Django REST Framework (backend) and React with Material UI (frontend). It provides a comprehensive system for managing customers, orders, products, and billing for a fulfillment or logistics business.

## System Architecture

### Backend Architecture
- **Framework**: Django REST Framework
- **Database**: PostgreSQL hosted on Supabase
- **Authentication**: JWT-based authentication with token refresh mechanism
- **API Structure**: RESTful API endpoints for CRUD operations
- **Error Handling**: Custom exception classes in api/exceptions.py
- **Logging**: Comprehensive request/response logging system

### Frontend Architecture
- **Framework**: React with Material UI v5
- **State Management**: Local React state with hooks (useState, useEffect)
- **Routing**: React Router v6 with protected routes
- **API Integration**: Custom API client with token-based authentication
- **Tables**: Material React Table for data tables
- **Forms**: Material UI form components
- **Build Tool**: Vite for development and production builds

## Core Modules

### Backend (Django Apps)
- **customers/** - Customer management
- **orders/** - Order management
- **products/** - Product catalog
- **services/** - Service offerings
- **billing/** - Billing and invoicing
- **rules/** - Business rules for pricing and conditions
- **inserts/** - Insertable material management
- **shipping/** - Shipping and logistics
- **materials/** - Raw materials tracking
- **bulk_operations/** - Bulk import/export functionality
- **customer_services/** - Customer-specific service configurations

### Frontend Structure
- **src/**
  - **components/** - React components organized by feature
  - **utils/** - Utility functions (auth, API client, logger)
  - **App.jsx** - Main application component with routing
  - **main.jsx** - Application entry point

## Key Models and Relationships

- **Customer**: Basic customer information (company_name, contact details, etc.)
- **Order**: Transaction details with shipping information and SKU quantities
- **Rule/RuleGroup**: Business logic for determining service pricing
  - **BasicRule**: Simple condition-based rules (field, operator, value)
  - **AdvancedRule**: Complex rules with JSON-based conditions and calculations
    - Supports case-based tiers with min/max ranges and values in tier_config
- **BillingReport**: Generated billing reports for customers

## Special Features

### Rules System
- Complex business logic implementation
- Support for case-based tiers with min/max ranges
- Frontend builders for rule creation and editing

### Logging System
- Client-side logging with localStorage storage
- Server-side logging with file-based storage
- API endpoints for log management
- Log viewer in frontend

### Bulk Operations
- Data import/export functionality
- CSV file processing
- Validation and error handling

### Materialized Views
- Performance optimization for complex queries
- Regular refresh mechanism
- Concurrent refresh support

## Memory Bank Purpose

This Memory Bank serves as a central repository for project documentation, tracking architectural decisions, managing tasks, and maintaining context across development sessions. It consists of four core files:

1. **productContext.md** (this file) - High-level project overview and architecture
2. **activeContext.md** - Current session context and focus areas
3. **progress.md** - Task tracking and project progress
4. **decisionLog.md** - Log of architectural decisions and their rationale

This structure helps maintain project knowledge, guide development efforts, and ensure consistent architectural vision throughout the project lifecycle.