# Technical Context

## Technology Stack

### Backend
- Django REST Framework
- PostgreSQL Database
- JWT Authentication
- Celery for async tasks
- WebSocket support
- OpenAPI/Swagger documentation
- Pandas for data processing

### Frontend
- React
- Material UI
- Material React Table
- React Router
- Vite build tool

## Development Setup
1. Django backend with modular app structure
2. React frontend with Material UI components
3. RESTful API architecture
4. WebSocket for real-time features

## Technical Constraints
1. Django Settings
   - No direct modifications to settings.py
   - Additional settings must be added separately

2. Models
   - No modifications to existing Django models
   - No field additions or removals
   - No alterations to model relationships

3. Frontend Requirements
   - Material UI components mandatory
   - Material React Table for list views:
     * Must implement resizable columns
     * Must use onChange resize mode
     * Must use auto table layout
     * Must match orders list behavior
   - Rules app can use alternative UI libraries
   - All components must be responsive
   - All list views must display all model fields
   - Thorough component testing required

4. Security
   - No security/authentication implementation during development

5. Development Guidelines
    - Frontend components in frontend folder only
    - Backend logic must remain unaltered
    - Comprehensive testing required

6. API Response Structure
    - Customer Services API returns nested data structure:
      ```json
      {
        "success": true,
        "data": [
          {
            "id": number,
            "customer_details": {
              "id": number,
              "company_name": string
            },
            "service_details": {
              "id": number,
              "service_name": string
            }
          }
        ]
      }
      ```
    - Frontend components must handle nested data appropriately
    - API responses include success flag and data wrapper
    - Error responses include error message and status code
    - Rules API responses may include 302 redirects for successful operations
    - Operator choices for advanced rules use specialized format:
      ```json
      {
        "operators": [
          {
            "value": string,
            "label": string
          }
        ]
      }
      ```

7. Bulk Operations Requirements
    - File Format Support:
      * CSV, XLSX, XLS formats only
      * Maximum file size: 10MB
      * Maximum 1000 rows per file
    
    - Template Structure:
      * Headers must match model field names
      * Required fields must be present
      * Choice fields must use valid values
      * JSON fields must be properly formatted
    
    - Data Validation:
      * Empty values handled appropriately:
        - NaN values converted to None/defaults
        - Empty strings allowed for optional fields
        - Default values for status/priority fields
      * Foreign key validation required
      * Data type validation enforced
      * Business logic validation applied
    
    - API Response Format:
      ```json
      {
        "success": boolean,
        "errors": [
          {
            "row": number,
            "errors": {
              "field": ["error messages"]
            }
          }
        ],
        "import_summary": {
          "total_rows": number,
          "successful": number,
          "failed": number
        }
      }
      ```

8. Error Handling Requirements
    - Client-side validation must prevent invalid file uploads
    - Server-side validation must provide detailed error messages
    - Row-level errors must include field-specific messages
    - Progress tracking must handle validation failures
    - User feedback must be clear and actionable