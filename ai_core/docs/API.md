# LedgerLink AI System API Reference

## Table of Contents
1. [Overview](#overview)
2. [Core APIs](#core-apis)
3. [REST APIs](#rest-apis)
4. [WebSocket API](#websocket-api)
5. [Error Handling](#error-handling)

## Overview

The LedgerLink AI System provides several APIs for interacting with its various components:
- Core Python APIs for direct integration
- REST APIs for HTTP-based integration
- WebSocket APIs for real-time updates

## Core APIs

### 1. Project Analysis API

Analyze your Django project structure and components.

```python
from ai_core.components import ProjectAnalyzer

# Initialize analyzer
analyzer = ProjectAnalyzer()

# Basic analysis
result = analyzer.analyze_project()

# Full analysis with specific components
result = analyzer.analyze_project(
    full_analysis=True,
    components=['models', 'views', 'templates']
)

# Available components for analysis:
# - 'apps': Django applications
# - 'models': Database models
# - 'views': View classes and functions
# - 'urls': URL patterns
# - 'templates': Template files
```

### 2. Code Generation API

Generate Django code based on specifications.

```python
from ai_core.code_generation import CodeGenerator

generator = CodeGenerator()

# Generate a model
model_spec = {
    'name': 'Product',
    'fields': [
        {
            'name': 'name',
            'type': 'CharField',
            'params': {'max_length': 100}
        },
        {
            'name': 'price',
            'type': 'DecimalField',
            'params': {
                'max_digits': 8,
                'decimal_places': 2
            }
        }
    ],
    'meta': {
        'ordering': ['-created_at'],
        'verbose_name': 'Product'
    }
}

code = generator.generate_model(model_spec)

# Generate a view
view_spec = {
    'name': 'ProductListView',
    'type': 'ListView',
    'model': 'Product',
    'methods': [
        {
            'name': 'get_queryset',
            'body': 'return Product.objects.filter(active=True)'
        }
    ]
}

code = generator.generate_view(view_spec)
```

### 3. Feature Implementation API

Implement new features automatically.

```python
from ai_core.feature_implementation import FeatureImplementer, FeatureManager

# Using the Feature Manager
manager = FeatureManager()

# Create a feature request
feature = manager.create_feature_request(
    title="Add search functionality",
    description="Implement product search with filters",
    user=request.user
)

# Implement a feature
implementer = FeatureImplementer()
result = implementer.implement_feature(feature.id)

# Check implementation status
status = manager.get_implementation_status(feature.id)
```

## REST APIs

### Authentication
All API endpoints require authentication. Use either:
- Session authentication (for web applications)
- Token authentication (for API clients)

```bash
# Token Authentication Header
Authorization: Token your-api-token
```

### Feature Requests

#### Create a Feature Request
```bash
POST /api/ai/features/
Content-Type: application/json

{
    "title": "Add search functionality",
    "description": "Implement product search with filters",
    "priority": "high"
}

Response (201 Created):
{
    "id": 1,
    "title": "Add search functionality",
    "status": "pending",
    "created_at": "2024-01-07T20:00:00Z"
}
```

#### Get Feature Status
```bash
GET /api/ai/features/{id}/status/

Response (200 OK):
{
    "status": "implementing",
    "progress": {
        "current_step": "generating_code",
        "total_steps": 5,
        "completed_steps": 2
    },
    "details": {
        "files_modified": ["models.py", "views.py"],
        "tests_added": ["tests/test_search.py"]
    }
}
```

#### Start Implementation
```bash
POST /api/ai/features/{id}/implement/
Content-Type: application/json

{
    "priority": "high",
    "schedule_for": "2024-01-08T10:00:00Z"  # Optional
}

Response (202 Accepted):
{
    "message": "Feature implementation started",
    "estimated_completion": "2024-01-08T10:30:00Z"
}
```

### Code Analysis

#### Analyze Code
```bash
POST /api/ai/system/analyze-code/
Content-Type: application/json

{
    "code": "class MyModel(models.Model):\n    name = models.CharField(max_length=100)",
    "analysis_type": "model"
}

Response (200 OK):
{
    "type": "model",
    "fields": [
        {
            "name": "name",
            "type": "CharField",
            "required": true,
            "constraints": ["max_length: 100"]
        }
    ],
    "patterns": [
        {
            "type": "naming_convention",
            "confidence": 0.95
        }
    ]
}
```

### Code Generation

#### Generate Code
```bash
POST /api/ai/system/generate-code/
Content-Type: application/json

{
    "type": "model",
    "specification": {
        "name": "Product",
        "fields": [
            {
                "name": "name",
                "type": "CharField",
                "params": {"max_length": 100}
            }
        ]
    }
}

Response (200 OK):
{
    "code": "class Product(models.Model):\n    name = models.CharField(max_length=100)\n",
    "file_path": "products/models.py"
}
```

## WebSocket API

### Connection
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/ai/features/');

socket.onopen = () => {
    console.log('Connected to AI system');
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Feature update:', data);
};
```

### Message Types

#### Request Feature Status
```javascript
socket.send(JSON.stringify({
    type: 'feature_status',
    feature_id: 123
}));
```

#### Feature Update Event
```javascript
{
    "type": "feature_update",
    "feature_id": 123,
    "status": "implementing",
    "details": {
        "current_step": "generating_code",
        "progress": 60
    }
}
```

## Error Handling

### HTTP Status Codes
- 200: Success
- 201: Created
- 202: Accepted
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Error Response Format
```json
{
    "error": "Error message",
    "details": {
        "field": ["Error details"]
    },
    "code": "ERROR_CODE"
}
```

### Common Error Codes
- `INVALID_REQUEST`: Request validation failed
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Permission denied
- `NOT_FOUND`: Resource not found
- `IMPLEMENTATION_ERROR`: Feature implementation failed
- `GENERATION_ERROR`: Code generation failed
- `ANALYSIS_ERROR`: Code analysis failed

### Example Error Response
```json
{
    "error": "Feature implementation failed",
    "details": {
        "reason": "Invalid model specification",
        "field": "fields",
        "message": "Field type 'InvalidType' is not supported"
    },
    "code": "IMPLEMENTATION_ERROR"
}
```

## Rate Limits

- API rate limits are enforced per user/token
- Default limits:
  - 100 requests per minute for analysis endpoints
  - 50 requests per minute for generation endpoints
  - 10 feature implementations per hour

## Support

For API support and bug reports:
- Email: support@ledgerlink.com
- GitHub Issues: https://github.com/your-org/ledgerlink/issues
- Documentation: https://docs.ledgerlink.com/api


