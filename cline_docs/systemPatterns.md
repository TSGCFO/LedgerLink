# System Patterns

## Architecture Overview

### Backend Architecture
1. Modular Django Apps
   - ai_core: AI and ML functionality
   - api: Core API functionality and utilities
   - billing: Billing and payment processing
   - bulk_operations: Bulk data import functionality
   - customer_services: Customer service management
   - customers: Customer data management
   - inserts: Data insertion handling
   - materials: Materials management
   - orders: Order processing
   - products: Product management
   - rules: Business rules engine
   - shipping: Shipping logistics

2. API Design
   - RESTful architecture
   - Serializer-based data transformation
   - JWT authentication
   - Custom middleware support
   - WebSocket integration

3. Bulk Operations Design
   - Template-based import system
   - CSV/Excel file processing
   - Multi-step validation:
     * Client-side file validation
     * Server-side data validation
     * Business logic validation
   - Progress tracking
   - Detailed error reporting
   - Default value handling
   - NaN value processing

### Frontend Architecture
1. Component Structure
   - Material UI based components
   - Material React Table for list views:
     * Resizable columns with onChange mode
     * Auto table layout for dynamic widths
     * Consistent implementation across all list views
   - Responsive design patterns
   - Component-based architecture
   - Multi-step workflow components:
     * Template selection
     * File upload
     * Validation progress
     * Results summary

2. State Management
   - React hooks for local state
   - API client utility for data fetching
   - Form validation patterns
   - Progress tracking state
   - Error state management

## Key Technical Decisions
1. Database
   - SQLite for development (db.sqlite3)
   - PostgreSQL ready for production

2. Authentication
   - JWT-based authentication system
   - Deferred security implementation

3. API Documentation
   - OpenAPI/Swagger integration
   - Comprehensive endpoint documentation

4. Testing
   - Unit tests for Django apps
   - Component testing for frontend
   - Integration testing requirements

## Development Patterns
1. Code Organization
   - Modular app structure
   - Separation of concerns
   - DRY principle adherence

2. Frontend Patterns
   - Component reusability
   - Material UI design system
   - Responsive design implementation
   - API Response Handling:
     * Service layer for API interactions
     * Response unwrapping (data extraction)
     * Nested data transformation
     * Error handling standardization
   - File Processing:
     * Client-side validation
     * Progress tracking
     * Error display
     * Success feedback

3. Backend Patterns
   - Model-driven development
   - API-first approach
   - Service layer abstraction
   - Response Structure:
     * Success flag in responses
     * Data wrapper for payload
     * Nested serialization for related data
     * Consistent error format
   - Bulk Import Patterns:
     * Template generation service
     * Field validation service
     * Data transformation service
     * Error collection and reporting
     * Default value handling
     * NaN value processing

4. Data Validation Patterns
   - Client-side validation:
     * File format validation
     * Size limits
     * Required fields
   - Server-side validation:
     * Data type validation
     * Business rules validation
     * Foreign key validation
   - Error Reporting:
     * Row-level errors
     * Field-level errors
     * Validation summaries