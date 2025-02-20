"""
Logging configuration for LedgerLink
"""

import os
from datetime import datetime
from logging.handlers import WatchedFileHandler
import threading

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Generate log filenames with timestamps
timestamp = datetime.now().strftime('%Y%m%d')
DEBUG_LOG = os.path.join(LOGS_DIR, f'debug_{timestamp}.log')
ERROR_LOG = os.path.join(LOGS_DIR, f'error_{timestamp}.log')
API_LOG = os.path.join(LOGS_DIR, f'api_{timestamp}.log')

# Custom RotatingFileHandler with file locking
class SafeRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def emit(self, record):
        if self.lock:  # Check if lock exists
            try:
                with self.lock:
                    super().emit(record)
            except Exception:
                self.handleError(record)
        else:
            try:
                super().emit(record)
            except Exception:
                self.handleError(record)

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
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': DEBUG_LOG,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': ERROR_LOG,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_api': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': API_LOG,
            'formatter': 'api',
            'encoding': 'utf-8',
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