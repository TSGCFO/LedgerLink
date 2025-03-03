"""
Test settings for LedgerLink project.
"""

from LedgerLink.settings import *
import os

# Database settings for testing with PostgreSQL
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

# Use in-memory storage for testing
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

# Disable debug mode
DEBUG = False

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use a test template directory
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'tests', 'templates')]

# Disable all caching for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use custom test runner to bypass migrations
TEST_RUNNER = 'tests.test_runner.NoMigrationTestRunner'

# Disable CSRF check in tests 
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django.middleware.csrf.CsrfViewMiddleware']

# Skip migrations completely
MIGRATION_MODULES = {app: None for app in INSTALLED_APPS}