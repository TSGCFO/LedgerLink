"""
Test settings for the LedgerLink project.
"""

from LedgerLink.settings import *
import os
# Try to import dj_database_url, but don't fail if not available
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# Database settings for testing with PostgreSQL
# First check for DATABASE_URL environment variable
if os.environ.get('DATABASE_URL') and HAS_DJ_DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config()
    }
else:
    # Fall back to individual settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'ledgerlink_test'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# Settings for handling migrations in tests
SKIP_MATERIALIZED_VIEWS = os.environ.get('SKIP_MATERIALIZED_VIEWS', 'False').upper() == 'TRUE'
DISABLE_CUSTOM_MIGRATIONS = os.environ.get('DISABLE_CUSTOM_MIGRATIONS', 'False').upper() == 'TRUE'

# Constants for billing validation
MAX_REPORT_DATE_RANGE = 365

# Use in-memory storage for testing
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

# Disable debug mode for tests
DEBUG = False

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable all caching for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable CSRF check in tests 
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django.middleware.csrf.CsrfViewMiddleware']