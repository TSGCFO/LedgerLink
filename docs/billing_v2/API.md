# Billing V2 API Documentation

## Overview

The Billing V2 API provides programmatic access to the billing report generation and management functionality. It allows you to generate reports, retrieve existing reports, and download reports in various formats.

## Base URL

All API endpoints are relative to the base URL:

```
https://[your-domain]/api/v2/
```

## Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_TOKEN
```

## Endpoints

### List Billing Reports

Retrieves a list of billing reports with optional filtering.

- **URL**: `/reports/`
- **Method**: GET
- **Auth Required**: Yes

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `customer_id` | Integer | Filter by customer ID |
| `start_date` | String | Filter by start date (YYYY-MM-DD) |
| `end_date` | String | Filter by end date (YYYY-MM-DD) |
| `created_after` | String | Filter by creation date (YYYY-MM-DD) |
| `created_before` | String | Filter by creation date (YYYY-MM-DD) |
| `order_by` | String | Field to order by (e.g., `-created_at`, `total_amount`) |

**Success Response**:

- **Code**: 200 OK
- **Content Example**:

```json
[
  {
    "id": 1,
    "customer_id": 123,
    "customer_name": "ACME Corp",
    "start_date": "2023-01-01",
    "end_date": "2023-01-31",
    "created_at": "2023-02-01T12:00:00Z",
    "total_amount": 1500.0,
    "order_count": 5
  },
  {
    "id": 2,
    "customer_id": 456,
    "customer_name": "Widgets Inc",
    "start_date": "2023-01-01",
    "end_date": "2023-01-31",
    "created_at": "2023-02-01T14:30:00Z",
    "total_amount": 2750.0,
    "order_count": 8
  }
]
```

**Error Response**:

- **Code**: 401 Unauthorized
- **Content**: `{ "detail": "Authentication credentials were not provided." }`

OR

- **Code**: 500 Internal Server Error
- **Content**: `{ "error": "An error occurred while fetching reports." }`

### Get Billing Report Details

Retrieves the full details of a specific billing report.

- **URL**: `/reports/{id}/`
- **Method**: GET
- **Auth Required**: Yes

**URL Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | Integer | The ID of the billing report to retrieve |

**Success Response**:

- **Code**: 200 OK
- **Content Example**:

```json
{
  "id": 1,
  "customer_id": 123,
  "customer_name": "ACME Corp",
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "created_at": "2023-02-01T12:00:00Z",
  "total_amount": 1500.0,
  "service_totals": {
    "1": {
      "service_name": "Picking",
      "amount": 500.0
    },
    "2": {
      "service_name": "Shipping",
      "amount": 1000.0
    }
  },
  "orders": [
    {
      "order_id": 10001,
      "reference_number": "REF-10001",
      "order_date": "2023-01-15",
      "total_amount": 1500.0,
      "service_costs": [
        {
          "service_id": 1,
          "service_name": "Picking",
          "amount": 500.0
        },
        {
          "service_id": 2,
          "service_name": "Shipping",
          "amount": 1000.0
        }
      ]
    }
  ]
}
```

**Error Response**:

- **Code**: 404 Not Found
- **Content**: `{ "detail": "Not found." }`

### Generate Billing Report

Generates a new billing report for a customer within a specified date range.

- **URL**: `/reports/generate/`
- **Method**: POST
- **Auth Required**: Yes

**Request Body**:

```json
{
  "customer_id": 123,
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "output_format": "json"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | Integer | Yes | The ID of the customer to generate the report for |
| `start_date` | String | Yes | Start date of the report period (YYYY-MM-DD) |
| `end_date` | String | Yes | End date of the report period (YYYY-MM-DD) |
| `output_format` | String | No | Output format (json, csv, pdf, dict). Default: json |

**Success Response**:

- **Code**: 201 Created
- **Content**: The generated billing report (format varies based on output_format)

**JSON format example**:

```json
{
  "id": 3,
  "customer_id": 123,
  "customer_name": "ACME Corp",
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "created_at": "2023-02-15T09:45:00Z",
  "total_amount": 2500.0,
  "service_totals": {
    "1": {
      "service_name": "Picking",
      "amount": 800.0
    },
    "2": {
      "service_name": "Shipping",
      "amount": 1700.0
    }
  },
  "orders": [
    {
      "order_id": 10005,
      "reference_number": "REF-10005",
      "order_date": "2023-01-20",
      "total_amount": 2500.0,
      "service_costs": [
        {
          "service_id": 1,
          "service_name": "Picking",
          "amount": 800.0
        },
        {
          "service_id": 2,
          "service_name": "Shipping",
          "amount": 1700.0
        }
      ]
    }
  ]
}
```

**Error Response**:

- **Code**: 400 Bad Request
- **Content**: `{ "error": "Start date must be before end date" }`

OR

- **Code**: 400 Bad Request
- **Content**: `{ "error": "Customer with ID 999 not found" }`

OR

- **Code**: 500 Internal Server Error
- **Content**: `{ "error": "An error occurred generating the report" }`

### Download Billing Report

Downloads a billing report in a specific format.

- **URL**: `/reports/{id}/download/`
- **Method**: GET
- **Auth Required**: Yes

**URL Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | Integer | The ID of the billing report to download |

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | String | The output format (csv, json, pdf). Default: csv |

**Success Response**:

- **Code**: 200 OK
- **Content**: The report in the specified format

**Headers**:

```
Content-Type: text/csv
Content-Disposition: attachment; filename="billing_report_1.csv"
```

**CSV format example**:

```
order_id,service_id,service_name,amount
10001,1,"Picking",500.00
10001,2,"Shipping",1000.00
```

**Error Response**:

- **Code**: 404 Not Found
- **Content**: `{ "detail": "Not found." }`

OR

- **Code**: 400 Bad Request
- **Content**: `{ "error": "Invalid format: xyz" }`

### Customer Summary

Returns a summary of billing reports by customer.

- **URL**: `/reports/customer-summary/`
- **Method**: GET
- **Auth Required**: Yes

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `customer_id` | Integer | Optional customer ID filter |

**Success Response**:

- **Code**: 200 OK
- **Content Example**:

```json
[
  {
    "customer_id": 123,
    "customer_name": "ACME Corp",
    "report_count": 5,
    "total_amount": 7500.0,
    "first_report": "2023-01-01T00:00:00Z",
    "latest_report": "2023-05-01T00:00:00Z"
  },
  {
    "customer_id": 456,
    "customer_name": "Widgets Inc",
    "report_count": 3,
    "total_amount": 4200.0,
    "first_report": "2023-02-01T00:00:00Z",
    "latest_report": "2023-04-01T00:00:00Z"
  }
]
```

**Error Response**:

- **Code**: 500 Internal Server Error
- **Content**: `{ "error": "An error occurred getting customer summary" }`

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - The request was invalid or cannot be otherwise served |
| 401 | Unauthorized - Authentication credentials were missing or invalid |
| 403 | Forbidden - The request is understood but has been refused |
| 404 | Not Found - The requested resource could not be found |
| 500 | Internal Server Error - Something went wrong on the server |

## Rate Limiting

API requests are limited to 100 requests per minute per user. If you exceed this limit, you will receive a 429 Too Many Requests response.

## Examples

### Generating a Report with cURL

```bash
curl -X POST https://example.com/api/v2/reports/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "start_date": "2023-01-01",
    "end_date": "2023-01-31",
    "output_format": "json"
  }'
```

### Downloading a Report with cURL

```bash
curl -X GET https://example.com/api/v2/reports/1/download/?format=csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output billing_report_1.csv
```

### Filtering Reports with Python

```python
import requests

response = requests.get(
    'https://example.com/api/v2/reports/',
    params={
        'customer_id': 123,
        'start_date': '2023-01-01',
        'end_date': '2023-01-31',
        'order_by': '-created_at'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

reports = response.json()
for report in reports:
    print(f"Report #{report['id']} - {report['customer_name']} - ${report['total_amount']}")
```
