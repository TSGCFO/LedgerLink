# Billing V2 Backend API Requirements

## Overview
This document outlines the required backend API endpoints for the Billing V2 feature in LedgerLink. The frontend has been updated to use these endpoints, but the backend implementation needs to be completed.

## API Endpoints

### 1. List Billing Reports
**Endpoint:** `/api/v2/reports/`  
**Method:** GET  
**Query Parameters:**
- `customer_id` (optional): Filter reports by customer ID
- `start_date` (optional): Filter reports with date >= start_date
- `end_date` (optional): Filter reports with date <= end_date
- `created_after` (optional): Filter reports created after this date
- `created_before` (optional): Filter reports created before this date
- `order_by` (optional): Field to order results by

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string-here",
      "customer": 1,
      "customer_name": "Customer Name",
      "start_date": "2025-01-01",
      "end_date": "2025-01-31",
      "total_amount": 1500.00,
      "generated_at": "2025-01-15T10:30:00Z",
      "output_format": "json",
      "created_at": "2025-01-15T10:30:00Z",
      "created_by": "admin_user"
    },
    // Additional reports...
  ]
}
```

### 2. Get Billing Report Details
**Endpoint:** `/api/v2/reports/{id}/`  
**Method:** GET  

**Response Format:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string-here",
    "customer": 1,
    "customer_name": "Customer Name",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "total_amount": 1500.00,
    "generated_at": "2025-01-15T10:30:00Z",
    "output_format": "json",
    "created_at": "2025-01-15T10:30:00Z",
    "created_by": "admin_user",
    "orders": [
      {
        "order_id": "ORD-001",
        "transaction_date": "2025-01-15",
        "status": "Completed",
        "ship_to_name": "John Smith",
        "ship_to_address": "123 Test St",
        "total_items": 5,
        "line_items": 2,
        "services": [
          {
            "service_id": 1,
            "service_name": "Standard Shipping",
            "amount": 25.00,
            "quantity": 1,
            "cost_type": "per_order"
          }
        ],
        "total_amount": 150.00
      }
    ],
    "service_totals": {
      "1": {
        "name": "Standard Shipping",
        "amount": 25.00,
        "order_count": 1
      }
    }
  }
}
```

### 3. Generate Billing Report
**Endpoint:** `/api/v2/reports/generate/`  
**Method:** POST  
**Request Format:**
```json
{
  "customer_id": 1,
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "output_format": "json"
}
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string-here",
    "customer": 1,
    "customer_name": "Customer Name",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "total_amount": 1500.00,
    "generated_at": "2025-01-15T10:30:00Z",
    "output_format": "json",
    "created_at": "2025-01-15T10:30:00Z",
    "created_by": "admin_user"
  }
}
```

### 4. Download Billing Report
**Endpoint:** `/api/v2/reports/{id}/download/`  
**Method:** GET  
**Query Parameters:**
- `format` (optional): Format to download (csv, json, pdf). Defaults to csv.

**Response:**
- Content-Type: Based on format (e.g., text/csv, application/json, application/pdf)
- Content-Disposition: attachment; filename="billing-report-{id}.{format}"

### 5. Get Customer Summary
**Endpoint:** `/api/v2/reports/customer-summary/`  
**Method:** GET  
**Query Parameters:**
- `customer_id` (optional): Get summary for specific customer

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "customer_id": 1,
      "customer_name": "Customer Name",
      "reports_count": 5,
      "total_billed": 7500.00,
      "first_billing_date": "2025-01-01",
      "last_billing_date": "2025-03-01",
      "average_bill_amount": 1500.00
    }
  ]
}
```

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages:

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {} // Optional additional error information
  }
}
```

Common error scenarios:
- 400 Bad Request: Invalid input parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 500 Internal Server Error: Unexpected server error

## CSRF Configuration

The Django backend needs to be configured to accept CSRF tokens from the frontend domain:

```python
# In Django settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5176',  # Local development
    'https://your-production-domain.com',
    # Add any other domains that might access the API
]
```

## Implementation Priority

1. `/api/v2/reports/generate/` - Currently returning 404, needs immediate implementation
2. `/api/v2/reports/` - Currently returning minimal data, needs complete implementation
3. Other endpoints can follow after these critical ones are working