"""
Django test settings for LedgerLink project.
These settings extend the main settings but are optimized for testing.
"""

from .settings import *  # Import the main settings

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use PostgreSQL test database (clone of main DB structure but separate data)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_ledgerlink',
        'USER': DATABASES['default']['USER'],
        'PASSWORD': DATABASES['default']['PASSWORD'],
        'HOST': DATABASES['default']['HOST'],
        'PORT': DATABASES['default']['PORT'],
        'TEST': {
            'NAME': 'test_ledgerlink',
        },
    }
}

# Set media directory for test uploads
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# Disable logging during tests to reduce noise
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Set testing flag
TESTING = True

# Make sure we don't accidentally send emails during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Turn off CSRF protection during testing
MIDDLEWARE = [m for m in MIDDLEWARE if 'CsrfViewMiddleware' not in m]

# Speed up password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]