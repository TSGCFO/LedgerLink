# Billing V2 Testing Plan

## Overview
This document outlines the testing plan for the Billing V2 feature in LedgerLink. It covers different testing types and specific test cases to ensure the feature works as expected.

## Prerequisites
- Backend API endpoints implemented according to the specification
- CSRF configuration updated in Django settings
- Frontend modifications completed

## 1. Manual Testing

### 1.1 Loading the Billing V2 Page
- **Action**: Navigate to /billing-v2
- **Expected Result**: Page loads with billing report form and empty or populated report list
- **Verification Points**:
  - "Billing System V2" title appears
  - Customer dropdown populated with customers
  - Form contains date fields and format selection
  - No console errors in browser developer tools

### 1.2 Generating a Report
- **Action**: 
  1. Select "Abokichi" customer
  2. Set start date to 02/16/2024
  3. Set end date to 03/10/2024
  4. Select JSON output format
  5. Click "Generate Report" button
- **Expected Result**: Report is generated and added to report list
- **Verification Points**:
  - Loading indicator during generation
  - Success message after generation
  - New report appears in list
  - No CSRF or API errors in console

### 1.3 Viewing Report Details
- **Action**: Click on a report in the list
- **Expected Result**: Report details panel shows order and service information
- **Verification Points**:
  - Order details are displayed correctly
  - Service totals are calculated correctly
  - UI layout is consistent

### 1.4 Downloading a Report
- **Action**: Click download button on a report
- **Expected Result**: Report is downloaded in the selected format
- **Verification Points**:
  - File downloads with correct format
  - File contains expected data
  
### 1.5 Error Handling Test
- **Action**: Try to generate a report with invalid dates (e.g., future dates)
- **Expected Result**: Error message displayed to user
- **Verification Points**:
  - Form validation prevents submission or API returns error
  - Error message is clear and actionable

## 2. API Testing

### 2.1 List Reports API
- **Endpoint**: GET /api/v2/reports/
- **Test Cases**:
  - Get all reports
  - Filter by customer_id
  - Filter by date range
  - Verify response format matches specification

### 2.2 Generate Report API
- **Endpoint**: POST /api/v2/reports/generate/
- **Test Cases**:
  - Generate with valid customer and dates
  - Generate with invalid customer (should error)
  - Generate with invalid date range (should error)
  - Verify CSRF token handling

### 2.3 Get Report Details API
- **Endpoint**: GET /api/v2/reports/{id}/
- **Test Cases**:
  - Get existing report
  - Get non-existent report (should 404)

### 2.4 Download Report API
- **Endpoint**: GET /api/v2/reports/{id}/download/
- **Test Cases**:
  - Download in CSV format
  - Download in JSON format
  - Download non-existent report (should 404)

## 3. Integration Testing

### 3.1 End-to-End Flow Testing
- **Flow**:
  1. Navigate to Billing V2 page
  2. Generate a new report
  3. View the generated report
  4. Download the report
- **Verification**: Entire flow completes without errors

### 3.2 Customer API Integration
- **Test**: Verify customer dropdown is populated from customer API
- **Verification**: All active customers appear in the dropdown

### 3.3 Authentication Integration
- **Test**: Attempt to access billing page without authentication
- **Verification**: User is redirected to login page

## 4. Performance Testing

### 4.1 Report Generation Performance
- **Test**: Generate reports for customers with large numbers of orders
- **Verification**: Report generation completes in a reasonable time (< 30 seconds)

### 4.2 Report List Loading Performance
- **Test**: Page load performance with many reports
- **Verification**: Page loads in < 3 seconds with 100+ reports

## 5. Edge Cases & Security Testing

### 5.1 CSRF Protection
- **Test**: Attempt to submit report generation from another origin
- **Verification**: Request is rejected due to CSRF protection

### 5.2 Input Validation
- **Test**: Submit form with:
  - Missing required fields
  - Invalid date ranges (end date before start date)
  - Special characters in input fields
- **Verification**: Appropriate validation errors are shown

### 5.3 API Error Handling
- **Test**: Trigger various API errors (server errors, timeouts)
- **Verification**: Frontend handles errors gracefully with appropriate messages

## Testing Environment Setup

### Development Environment
1. Start Django backend:
   ```
   cd /LedgerLink
   python manage.py runserver
   ```

2. Start React frontend:
   ```
   cd /LedgerLink/frontend
   npm run dev
   ```

3. Access the application at http://localhost:5176/billing-v2

### Test Data
- Ensure "Abokichi" customer (ID: 1) has orders in the test database
- Create test data for the date range 02/16/2024 - 03/10/2024 if needed

## Bug Reporting Template

When filing bugs, include:
1. **Steps to reproduce**: Detailed steps to recreate the issue
2. **Expected behavior**: What should happen
3. **Actual behavior**: What actually happened
4. **Environment**: Browser, OS, screen size
5. **Screenshots/Videos**: Visual evidence if applicable
6. **Console logs**: Any JavaScript or server errors
7. **Network logs**: API requests and responses related to the issue