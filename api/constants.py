from django.utils.translation import gettext_lazy as _

# API Versions
API_VERSIONS = {
    'v1': {
        'active': True,
        'end_of_life': None,
        'deprecated': False,
    }
}

# HTTP Status Messages
HTTP_STATUS_MESSAGES = {
    200: _('Request processed successfully.'),
    201: _('Resource created successfully.'),
    204: _('Resource deleted successfully.'),
    400: _('Invalid request data.'),
    401: _('Authentication required.'),
    403: _('Permission denied.'),
    404: _('Resource not found.'),
    405: _('Method not allowed.'),
    409: _('Resource conflict.'),
    429: _('Too many requests.'),
    500: _('Internal server error.'),
}

# Error Codes
ERROR_CODES = {
    'VALIDATION_ERROR': 'Validation failed',
    'AUTHENTICATION_ERROR': 'Authentication failed',
    'PERMISSION_ERROR': 'Permission denied',
    'NOT_FOUND': 'Resource not found',
    'CONFLICT_ERROR': 'Resource conflict',
    'THROTTLED': 'Too many requests',
    'INTERNAL_ERROR': 'Internal server error',
}

# Pagination Settings
PAGINATION = {
    'DEFAULT_PAGE_SIZE': 10,
    'MAX_PAGE_SIZE': 100,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'PAGE_QUERY_PARAM': 'page',
}

# Cache Keys and Timeouts
CACHE = {
    'DEFAULT_TIMEOUT': 300,  # 5 minutes
    'LONG_TIMEOUT': 3600,    # 1 hour
    'SHORT_TIMEOUT': 60,     # 1 minute
    'KEY_PREFIX': 'api_cache',
}

# Order Status
ORDER_STATUS = {
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'CANCELLED': 'cancelled',
    'REFUNDED': 'refunded',
}

ORDER_STATUS_CHOICES = [
    (ORDER_STATUS['PENDING'], _('Pending')),
    (ORDER_STATUS['PROCESSING'], _('Processing')),
    (ORDER_STATUS['COMPLETED'], _('Completed')),
    (ORDER_STATUS['CANCELLED'], _('Cancelled')),
    (ORDER_STATUS['REFUNDED'], _('Refunded')),
]

# Payment Status
PAYMENT_STATUS = {
    'PENDING': 'pending',
    'AUTHORIZED': 'authorized',
    'PAID': 'paid',
    'FAILED': 'failed',
    'REFUNDED': 'refunded',
}

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS['PENDING'], _('Pending')),
    (PAYMENT_STATUS['AUTHORIZED'], _('Authorized')),
    (PAYMENT_STATUS['PAID'], _('Paid')),
    (PAYMENT_STATUS['FAILED'], _('Failed')),
    (PAYMENT_STATUS['REFUNDED'], _('Refunded')),
]

# Shipping Status
SHIPPING_STATUS = {
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'SHIPPED': 'shipped',
    'DELIVERED': 'delivered',
    'RETURNED': 'returned',
}

SHIPPING_STATUS_CHOICES = [
    (SHIPPING_STATUS['PENDING'], _('Pending')),
    (SHIPPING_STATUS['PROCESSING'], _('Processing')),
    (SHIPPING_STATUS['SHIPPED'], _('Shipped')),
    (SHIPPING_STATUS['DELIVERED'], _('Delivered')),
    (SHIPPING_STATUS['RETURNED'], _('Returned')),
]

# User Roles
USER_ROLES = {
    'ADMIN': 'admin',
    'STAFF': 'staff',
    'CUSTOMER': 'customer',
    'GUEST': 'guest',
}

USER_ROLE_CHOICES = [
    (USER_ROLES['ADMIN'], _('Admin')),
    (USER_ROLES['STAFF'], _('Staff')),
    (USER_ROLES['CUSTOMER'], _('Customer')),
    (USER_ROLES['GUEST'], _('Guest')),
]

# API Rate Limiting
RATE_LIMITING = {
    'DEFAULT': '100/hour',
    'BURST': '20/minute',
    'SUSTAINED': '1000/day',
    'STRICT': '50/hour',
}

# File Upload Settings
FILE_UPLOAD = {
    'MAX_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_TYPES': [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
    'MAX_FILES': 10,
}

# Search Settings
SEARCH = {
    'MIN_CHARS': 3,
    'MAX_RESULTS': 50,
    'FUZZY_MATCH_THRESHOLD': 0.8,
}

# Audit Log Actions
AUDIT_ACTIONS = {
    'CREATE': 'create',
    'UPDATE': 'update',
    'DELETE': 'delete',
    'VIEW': 'view',
    'LOGIN': 'login',
    'LOGOUT': 'logout',
}

AUDIT_ACTION_CHOICES = [
    (AUDIT_ACTIONS['CREATE'], _('Create')),
    (AUDIT_ACTIONS['UPDATE'], _('Update')),
    (AUDIT_ACTIONS['DELETE'], _('Delete')),
    (AUDIT_ACTIONS['VIEW'], _('View')),
    (AUDIT_ACTIONS['LOGIN'], _('Login')),
    (AUDIT_ACTIONS['LOGOUT'], _('Logout')),
]

# API Feature Flags
FEATURE_FLAGS = {
    'USE_CACHING': True,
    'ENABLE_AUDIT_LOG': True,
    'STRICT_VALIDATION': True,
    'ENABLE_RATE_LIMITING': True,
    'ENABLE_VERSIONING': True,
}

# Response Fields
RESPONSE_FIELDS = {
    'SUCCESS': 'success',
    'MESSAGE': 'message',
    'DATA': 'data',
    'ERROR': 'error',
    'META': 'meta',
}

# Common Regex Patterns
REGEX_PATTERNS = {
    'EMAIL': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'PHONE': r'^\+?1?\d{9,15}$',
    'USERNAME': r'^[\w.@+-]+$',
    'PASSWORD': r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$',
    'UUID': r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
}

# Date Formats
DATE_FORMATS = {
    'API_DATE': '%Y-%m-%d',
    'API_DATETIME': '%Y-%m-%dT%H:%M:%SZ',
    'DISPLAY_DATE': '%b %d, %Y',
    'DISPLAY_DATETIME': '%b %d, %Y %H:%M',
}

# api/constants.py
# Add these constants

BULK_OPERATION_STATUSES = {
    'PENDING': 'pending',
    'VALIDATING': 'validating',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'COMPLETED_WITH_ERRORS': 'completed_with_errors'
}

BULK_OPERATION_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

SUPPORTED_FILE_FORMATS = ['csv', 'xlsx']

BULK_OPERATION_CACHE_TIMEOUT = 3600  # 1 hour