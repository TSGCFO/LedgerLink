# Billing V2 System Documentation

## Overview

The Billing V2 system is a complete rewrite of the original billing system with improved performance, reliability, and features. It provides a robust solution for generating billing reports based on orders and services, applying business rules to determine which services apply to which orders, and calculating the appropriate costs.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Models](#database-models)
3. [Core Components](#core-components)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Management Commands](#management-commands)
7. [Usage Guide](#usage-guide)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## System Architecture

The Billing V2 system follows a standard Django architecture with a focus on separation of concerns and maintainability:

- **Models**: Define the database structure for billing reports, order costs, and service costs.
- **Views**: Handle HTTP requests and responses using Django REST Framework.
- **Serializers**: Convert between Python objects and JSON/HTML representations.
- **Utils**: Contain core business logic for SKU normalization, rule evaluation, and billing calculation.
- **Management Commands**: Provide command-line tools for administrative tasks.
- **Tests**: Ensure the system works as expected through comprehensive unit and integration tests.
- **Frontend**: React components for the user interface.

## Database Models

### BillingReport

The main model that represents a billing report for a customer over a specific date range.

**Fields**:
- `customer`: ForeignKey to Customer model
- `start_date`: DateTime for the beginning of the billing period
- `end_date`: DateTime for the end of the billing period
- `created_at`: DateTime when the report was created
- `updated_at`: DateTime when the report was last updated
- `total_amount`: DecimalField for the total amount of the report
- `service_totals`: JSONField with service totals by service ID

**Methods**:
- `add_order_cost(order_cost)`: Add an order cost to the report and update totals
- `to_dict()`: Convert the report to a dictionary format
- `to_json()`: Convert the report to a JSON string

### OrderCost

Represents the cost details for a specific order within a billing report.

**Fields**:
- `order`: ForeignKey to Order model
- `billing_report`: ForeignKey to BillingReport model
- `total_amount`: DecimalField for the total amount of the order cost

**Methods**:
- `add_service_cost(service_cost)`: Add a service cost to the order cost and update total
- `to_dict()`: Convert the order cost to a dictionary format

### ServiceCost

Represents the cost of a specific service applied to an order.

**Fields**:
- `order_cost`: ForeignKey to OrderCost model
- `service_id`: IntegerField for the service ID
- `service_name`: CharField for the service name
- `amount`: DecimalField for the amount of the service cost

**Methods**:
- `to_dict()`: Convert the service cost to a dictionary format

## Core Components

### SKU Utilities

Located in `utils/sku_utils.py`, these functions handle SKU normalization and validation:

- `normalize_sku(sku)`: Normalize a SKU by removing hyphens and spaces, and converting to uppercase
- `convert_sku_format(sku_data)`: Convert SKU data from various formats to a normalized dictionary
- `validate_sku_quantity(sku_data)`: Validate SKU quantity data

### Rule Evaluator

Located in `utils/rule_evaluator.py`, this class handles rule evaluation:

- `evaluate_rule(rule, order)`: Evaluate a single rule against an order
- `evaluate_rule_group(rule_group, order)`: Evaluate a rule group against an order
- `evaluate_case_based_rule(rule, order)`: Evaluate a case-based tier rule against an order

### Billing Calculator

Located in `utils/calculator.py`, this class handles billing calculation:

- `generate_report()`: Generate a billing report for the specified customer and date range
- `calculate_service_cost(customer_service, order)`: Calculate the cost for a service applied to an order
- `to_dict()`, `to_json()`, `to_csv()`: Convert the report to various formats

## API Endpoints

The Billing V2 API provides the following endpoints:

### List Billing Reports

- **URL**: `/api/v2/reports/`
- **Method**: GET
- **Description**: Get a list of billing reports
- **Query Parameters**:
  - `customer_id`: Filter by customer ID
  - `start_date`: Filter by start date (YYYY-MM-DD)
  - `end_date`: Filter by end date (YYYY-MM-DD)
  - `created_after`: Filter by creation date (YYYY-MM-DD)
  - `created_before`: Filter by creation date (YYYY-MM-DD)
  - `order_by`: Field to order by (e.g., `-created_at`, `total_amount`)
- **Response**: List of billing reports in summary format

### Get Billing Report Details

- **URL**: `/api/v2/reports/{id}/`
- **Method**: GET
- **Description**: Get details for a specific billing report
- **Response**: Detailed billing report with nested order costs and service costs

### Generate Billing Report

- **URL**: `/api/v2/reports/generate/`
- **Method**: POST
- **Description**: Generate a new billing report
- **Request Body**:
  ```json
  {
    "customer_id": 123,
    "start_date": "2023-01-01",
    "end_date": "2023-01-31",
    "output_format": "json"
  }
  ```
- **Response**: Newly generated billing report

### Download Billing Report

- **URL**: `/api/v2/reports/{id}/download/`
- **Method**: GET
- **Description**: Download a billing report in a specific format
- **Query Parameters**:
  - `format`: Output format (`csv`, `json`, `pdf`)
- **Response**: File download in the specified format

### Customer Summary

- **URL**: `/api/v2/reports/customer-summary/`
- **Method**: GET
- **Description**: Get a summary of billing reports by customer
- **Query Parameters**:
  - `customer_id`: Optional customer ID filter
- **Response**: Summary data grouped by customer

## Frontend Components

### BillingPage

The main container component that manages state and data fetching. It includes:
- Customer selection
- Date range selection
- Report generation form
- Report list
- Report details view

### BillingReportGenerator

Form for generating new billing reports with:
- Customer selection (autocomplete)
- Date range selection (date pickers)
- Output format selection
- Form validation

### BillingReportList

List of existing reports with:
- Selection functionality
- Sorting and filtering
- Download options
- Preview information

### BillingReportViewer

Detailed view of a selected report with:
- Report summary
- Service totals
- Order details in collapsible sections
- Download options

## Management Commands

### generate_billing_report

Generates billing reports for customers from the command line.

**Usage**:
```bash
python manage.py generate_billing_report --customer-id=123 --start-date=2023-01-01 --end-date=2023-01-31 --output-format=json --output-dir=/path/to/output
```

**Options**:
- `--customer-id`: Customer ID to generate report for
- `--all-customers`: Generate reports for all active customers
- `--start-date`: Start date (YYYY-MM-DD) for report period
- `--end-date`: End date (YYYY-MM-DD) for report period
- `--days`: Number of days for report period (default: 30)
- `--output-format`: Output format for reports (`json`, `csv`, `dict`)
- `--output-dir`: Directory to save report files

### cleanup_billing_reports

Cleans up old billing reports to maintain database size.

**Usage**:
```bash
python manage.py cleanup_billing_reports --days=90 --customer-id=123 --dry-run
```

**Options**:
- `--days`: Delete reports older than this many days (default: 90)
- `--customer-id`: Limit cleanup to a specific customer
- `--dry-run`: Show what would be deleted without actually deleting

### export_billing_reports

Exports billing reports in bulk to various formats.

**Usage**:
```bash
python manage.py export_billing_reports /path/to/output --format=json --customer-id=123 --combine
```

**Options**:
- `output_dir`: Directory to save exported files
- `--format`: Output format (`json`, `csv`)
- `--customer-id`: Filter by customer ID
- `--report-id`: Export a specific report by ID
- `--start-date`: Filter by start date (YYYY-MM-DD)
- `--end-date`: Filter by end date (YYYY-MM-DD)
- `--combine`: Combine all reports into a single file
- `--min-amount`: Filter by minimum total amount
- `--max-amount`: Filter by maximum total amount

## Usage Guide

### Generating Billing Reports

1. Navigate to the Billing V2 page from the sidebar menu
2. Select a customer from the dropdown
3. Select a date range for the billing period
4. Choose an output format (JSON, CSV, PDF)
5. Click "Generate Report"
6. View the generated report in the report viewer

### Viewing Existing Reports

1. Navigate to the Billing V2 page from the sidebar menu
2. Select a report from the list on the left
3. View the report details in the viewer on the right
4. Expand order sections to see detailed service costs

### Downloading Reports

1. Navigate to the Billing V2 page from the sidebar menu
2. Select a report from the list
3. Click the download button for the desired format (CSV, JSON)
4. Save the file to your computer

### Generating Reports via API

To generate a report programmatically:

```python
import requests

response = requests.post(
    'http://localhost:8000/api/v2/reports/generate/',
    json={
        'customer_id': 123,
        'start_date': '2023-01-01',
        'end_date': '2023-01-31',
        'output_format': 'json'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

report = response.json()
print(f"Generated report with total amount: ${report['total_amount']}")
```

### Generating Reports via Command Line

To generate reports for all customers for the last 30 days:

```bash
python manage.py generate_billing_report --all-customers --output-dir=/tmp/reports
```

To generate a report for a specific customer and date range:

```bash
python manage.py generate_billing_report --customer-id=123 --start-date=2023-01-01 --end-date=2023-01-31 --output-format=csv --output-dir=/tmp/reports
```

## Testing

The Billing V2 system has comprehensive tests for models, utilities, and views. To run the tests:

```bash
# Run all tests
python manage.py test Billing_V2

# Run specific test modules
python manage.py test Billing_V2.tests.test_models
python manage.py test Billing_V2.tests.test_utils
python manage.py test Billing_V2.tests.test_views

# Run with coverage
coverage run --source='Billing_V2' manage.py test Billing_V2
coverage report
coverage html
```

## Deployment

The Billing V2 system is included in the main deployment process for the LedgerLink application. When deploying:

1. Ensure database migrations are applied:
   ```bash
   python manage.py migrate Billing_V2
   ```

2. Collect static files if using the frontend:
   ```bash
   python manage.py collectstatic
   ```

3. Update the frontend build if making React component changes:
   ```bash
   cd frontend
   npm run build
   ```

## Troubleshooting

### Common Issues

1. **Reports not showing all orders**:
   - Check the date range - orders must be within the specified range
   - Verify customer ID is correct
   - Ensure orders have valid SKU data

2. **Service costs not calculating correctly**:
   - Check rule configuration in the database
   - Verify SKU format in orders
   - Look for excluded SKUs in case-based tier rules

3. **API errors**:
   - Check authentication token
   - Verify request format and parameters
   - Look for validation errors in the response

### Debugging

The Billing V2 system has comprehensive logging. Check the following log files:

- `logs/debug_YYYYMMDD.log`: General debug information
- `logs/error_YYYYMMDD.log`: Error messages
- `logs/api_YYYYMMDD.log`: API request/response details

You can increase logging verbosity by changing the log level in `settings.py`:

```python
LOGGING['loggers']['Billing_V2'] = {
    'handlers': ['console', 'file_debug', 'file_error'],
    'level': 'DEBUG',
    'propagate': False,
}
```

### Getting Help

For additional help, please contact the development team or refer to the internal documentation.