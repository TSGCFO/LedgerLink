"""
Django settings for LedgerLink project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vql06k^elcrm_&^vo^4mb61h=kqu0xs1@y3)9k=h01jv*vd+@('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "customers.apps.CustomersConfig",
    "products.apps.ProductsConfig",
    "services.apps.ServicesConfig",
    "customer_services.apps.CustomerServicesConfig",
    "orders.apps.OrdersConfig",
    "inserts.apps.InsertsConfig",
    "materials.apps.MaterialsConfig",
    "shipping.apps.ShippingConfig",
    "rules.apps.BillingConfig",
    "crispy_forms",
    "crispy_bootstrap5",
    "rest_framework",
    'Main.apps.MainConfig',
    'billing.apps.BillingConfig',
    'ai_core.apps.AICoreConfig',
    'channels',
]

# Add LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'main:dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Update crispy forms to use Bootstrap 5
CRISPY_TEMPLATE_PACK = 'bootstrap5'  # Change from bootstrap4
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
     'ai_core.middleware.AIMonitoringMiddleware',
]

ROOT_URLCONF = 'LedgerLink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'Main' / 'templates',  # Add this line
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'LedgerLink.wsgi.application'

# Channels configuration
ASGI_APPLICATION = 'LedgerLink.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pycharm_django',
        'USER': 'postgres',
        'PASSWORD': 'hassan',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# URL prefix for static files
STATIC_URL = '/static/'

# Directory where Django will collect all static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    ]

# The finders Django uses to locate static files
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Simplified static file serving
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Maximum file upload size (10MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Message framework settings
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Update the LOGGING configuration in settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'billing': {  # Logger for billing app
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'ai_core': {  # Logger for AI system
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# AI system configuration
# ----------------------------------------------------------------------
# This dictionary contains the configuration for the AI system components.
# It includes the enabled status of each component, their settings, and the
# security settings for the AI system.
#
# Parameters:
# ----------------------------------------------------------------------
# enabled (bool): A boolean value indicating whether the AI system is enabled.
#
# components (dict): A dictionary containing the configuration for each AI system component.
#
# security (dict): A dictionary containing the security settings for the AI system.
#
# Returns:
# ----------------------------------------------------------------------
# AI_SYSTEM_CONFIG (dict): A dictionary containing the AI system configuration.
# ```
# AI system configuration settings for the Django project
# LedgerLink/settings.py
# Add this configuration
AI_SYSTEM_CONFIG = {
    'enabled': True,
    'components': {
        'project_analyzer': {
            'enabled': True,
            'settings': {
                'analysis_interval': 600,
                'ignore_patterns': [
                    '*.pyc',
                    '__pycache__',
                    'migrations',
                ]
            }
        },
        'context_manager': {
            'enabled': True,
            'settings': {
                'cache_timeout': 600,
                'max_context_size': 10000
            }
        },
        'code_generator': {
            'enabled': True,
            'settings': {
                'template_dir': 'ai_core/code_templates'
            }
        }
    },
    'security': {
        'restricted_paths': [
            'settings.py',
            'manage.py',
            'wsgi.py',
            'asgi.py'
        ],
        'backup_enabled': True,
        'backup_path': 'ai_backups'
    }
}

# ----------------------------------------------------------------------
# End of AI system configuration

# ----------------------------------------------------------------------
"""
Configure Django Rest Framework (DRF) settings for the project.

This dictionary defines the default authentication and permission classes
for DRF views in the project. It ensures that API endpoints are secure
and only accessible to authenticated users.

Parameters:
----------
DEFAULT_PERMISSION_CLASSES : list
    A list of permission classes that determine the default permissions
    for all DRF views. In this case, it requires users to be authenticated
    to access any API endpoint.

DEFAULT_AUTHENTICATION_CLASSES : list
    A list of authentication classes that determine how users are
    authenticated for DRF views. It includes both session-based and
    basic authentication methods.

Returns:
-------
dict
    A dictionary containing the DRF configuration settings.
"""
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

# ----------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'ai_system_cache',
    }
}