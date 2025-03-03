import pytest
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.db import connections, connection


def is_sqlite_in_memory_db():
    """Check if we are using an in-memory database."""
    database_name = settings.DATABASES['default']['NAME']
    return (database_name == ':memory:' or 
            'mode=memory' in database_name or 
            database_name.startswith('file:memorydb'))


def is_postgresql_db():
    """Check if we are using a PostgreSQL database."""
    return settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'


@pytest.fixture(scope='session')
def django_db_setup():
    """
    This fixture completely replaces the default django_db_setup fixture 
    provided by pytest-django.
    
    It sets up the database using create_model() to directly create tables 
    without running migrations. For PostgreSQL, it also creates materialized views
    and other PostgreSQL-specific objects.
    """
    from django.db import connection
    from django.apps import apps

    # Create all tables directly using Django's ORM 
    with connection.schema_editor() as schema_editor:
        for app_config in apps.get_app_configs():
            if app_config.models_module:
                for model in app_config.get_models():
                    try:
                        schema_editor.create_model(model)
                    except Exception as e:
                        print(f"Failed to create table for {model.__name__}: {e}")
    
    # If using PostgreSQL, create materialized views and other PostgreSQL-specific objects
    if is_postgresql_db():
        print("PostgreSQL detected - creating materialized views and other PostgreSQL-specific objects")
        try:
            # Execute SQL from test_postgresql_objects.sql
            sql_file_path = os.path.join(settings.BASE_DIR, 'tests', 'test_postgresql_objects.sql')
            if os.path.exists(sql_file_path):
                with open(sql_file_path, 'r') as f:
                    sql = f.read()
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                print("Successfully created PostgreSQL-specific objects")
            else:
                print(f"WARNING: Could not find {sql_file_path}")
        except Exception as e:
            print(f"Failed to create PostgreSQL-specific objects: {e}")


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def admin_user():
    User = get_user_model()
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword'
    )
    return user


@pytest.fixture
def authenticated_client(client, admin_user):
    client.force_login(admin_user)
    return client