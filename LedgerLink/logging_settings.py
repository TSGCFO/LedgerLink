"""
Logging configuration for LedgerLink
"""

import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Generate log filenames with timestamps
timestamp = datetime.now().strftime('%Y%m%d')
DEBUG_LOG = os.path.join(LOGS_DIR, f'debug_{timestamp}.log')
ERROR_LOG = os.path.join(LOGS_DIR, f'error_{timestamp}.log')
API_LOG = os.path.join(LOGS_DIR, f'api_{timestamp}.log')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] [{name}] [{module}.{funcName}] {message}',
            'style': '{',
        },
        'api': {
            'format': '[{asctime}] [{levelname}] [{name}] Method: {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG,
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG,
            'formatter': 'verbose',
        },
        'file_api': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': API_LOG,
            'formatter': 'api',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file_api', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rules': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'customers': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'products': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'billing': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'shipping': {
            'handlers': ['console', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}