# Django CSRF Configuration Guide

## Overview
This document provides instructions for configuring CSRF (Cross-Site Request Forgery) protection in the Django backend to work with the LedgerLink frontend.

## Problem
The frontend is receiving CSRF verification errors when making POST requests to the backend API. The error occurs because the domain used by the frontend is not included in Django's `CSRF_TRUSTED_ORIGINS` setting.

From the application logs:
```
Error generating billing report: {"message":"Invalid response from server","status":404,"originalError":{"message":"Failed to execute 'json' on 'Response': Unexpected end of JSON input"}}
```

## Solution

### 1. Update Django Settings

Add the frontend domain(s) to the `CSRF_TRUSTED_ORIGINS` setting in your Django settings file:

```python
# In settings.py

# Existing CSRF settings
CSRF_COOKIE_SECURE = True  # Only send cookie over HTTPS
CSRF_USE_SESSIONS = False  # Store CSRF token in cookie instead of session
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to access the CSRF cookie

# Add this setting or update it if it already exists
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5175',  # Development server default
    'http://localhost:5176',  # Current development server
    'http://localhost:5177',  # Alternative development server
    'http://127.0.0.1:5175',
    'http://127.0.0.1:5176',
    'http://127.0.0.1:5177',
    'https://your-production-domain.com',
    # Add any ngrok domains if using ngrok for development
    'https://5101bf014543.ngrok.app',  # Example ngrok domain
]
```

### 2. Verify CORS Settings (if applicable)

If you're using Django CORS headers or a similar package for cross-origin resource sharing, make sure those settings are also configured correctly:

```python
# If using django-cors-headers
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5175',
    'http://localhost:5176',
    'http://localhost:5177',
    'http://127.0.0.1:5175',
    'http://127.0.0.1:5176',
    'http://127.0.0.1:5177',
    'https://your-production-domain.com',
    'https://5101bf014543.ngrok.app',  # Example ngrok domain
]

# Allow credentials (cookies, including CSRF cookie)
CORS_ALLOW_CREDENTIALS = True
```

### 3. Restart Django Server

After making these changes, restart the Django development server to apply the new settings:

```bash
# Stop the current server (Ctrl+C) and then run:
python manage.py runserver
```

## Testing the Configuration

1. Start the Django backend server
2. Start the frontend development server (`npm run dev`)
3. Navigate to the Billing V2 page
4. Try to generate a report by selecting a customer and date range
5. Check browser developer console and server logs for any CSRF-related errors

## Troubleshooting

If CSRF errors persist:

1. Verify the frontend is including the CSRF token in requests:
   - Check that requests include either the `X-CSRFToken` header or the `csrfmiddlewaretoken` form field
   - Verify the CSRF token is being properly extracted from cookies in the frontend

2. Check that the domain in request headers matches exactly with what's in `CSRF_TRUSTED_ORIGINS`
   - Look in the Django logs for the domain that's making the request
   - Ensure that domain (including protocol - http/https) is in the trusted origins list

3. For API requests, ensure Content-Type is 'application/json'
   - The browser automatically sends 'application/x-www-form-urlencoded' for form submissions, which Django's CSRF middleware handles automatically
   - For AJAX/fetch requests with 'application/json', ensure you're explicitly sending the CSRF token as a header