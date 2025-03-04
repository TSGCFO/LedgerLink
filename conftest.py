import pytest
import os
import sys
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.db import connections, connection

# Only import testcontainers if not in Docker environment
try:
    from testcontainers.postgres import PostgresContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False


def is_sqlite_in_memory_db():
    """Check if we are using an in-memory database."""
    database_name = settings.DATABASES['default']['NAME']
    return (database_name == ':memory:' or 
            'mode=memory' in database_name or 
            database_name.startswith('file:memorydb'))


def is_postgresql_db():
    """Check if we are using a PostgreSQL database."""
    return settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'


def should_use_testcontainers():
    """Check if we should use TestContainers for database setup."""
    # Don't use TestContainers if we're in Docker or if it's not available
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true'
    use_testcontainers = (
        is_postgresql_db() and 
        os.environ.get('USE_TESTCONTAINERS', 'True').lower() == 'true' and
        not in_docker and
        TESTCONTAINERS_AVAILABLE
    )
    return use_testcontainers


@pytest.fixture(scope='session')
def postgres_container():
    """
    Fixture that provides a PostgreSQL container.
    The container is started when this fixture is first requested
    and stopped at the end of the test session.
    """
    if not should_use_testcontainers():
        # Skip TestContainers if not needed
        print("TestContainers not used - using existing database connection.")
        yield None
        return
    
    # TestContainers implementation
    try:
        # Define container configuration - match version in docker-compose.test.yml
        postgres_container = PostgresContainer(
            image="postgres:15",
            username="postgres",
            password="postgres",
            dbname="ledgerlink_test",
            port=5432
        )
        
        # Start the container
        print("Starting PostgreSQL container with TestContainers...")
        postgres_container.start()
        
        # Save the connection information for the Django fixture
        os.environ['TC_DB_NAME'] = postgres_container.dbname
        os.environ['TC_DB_USER'] = postgres_container.username
        os.environ['TC_DB_PASSWORD'] = postgres_container.password
        os.environ['TC_DB_HOST'] = postgres_container.get_container_host_ip()
        os.environ['TC_DB_PORT'] = str(postgres_container.get_exposed_port(5432))
        
        print(f"TestContainers PostgreSQL running at: {os.environ['TC_DB_HOST']}:{os.environ['TC_DB_PORT']}")
        
        # Make container available to tests
        yield postgres_container
        
        # Stop container when tests are done
        print("Stopping PostgreSQL container...")
        postgres_container.stop()
        print("PostgreSQL container stopped.")
    except Exception as e:
        print(f"Error setting up TestContainers: {e}")
        yield None


@pytest.fixture(scope='session')
def django_db_setup(request, postgres_container):
    """
    This fixture completely replaces the default django_db_setup fixture 
    provided by pytest-django.
    
    It sets up the database using create_model() to directly create tables 
    without running migrations. For PostgreSQL, it also creates materialized views
    and other PostgreSQL-specific objects.
    """
    from django.db import connection, connections
    from django.apps import apps
    
    # Check if we're in Docker
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true'
    
    # If in Docker, use the existing database configuration
    if in_docker:
        print("Using Docker database configuration")
        # Nothing to do - settings are already configured by docker-compose
        pass
    # If using TestContainers, configure Django to use the container's connection details
    elif should_use_testcontainers() and postgres_container:
        print("Using TestContainers database configuration")
        # Update Django's database configuration
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['TC_DB_NAME'],
            'USER': os.environ['TC_DB_USER'],
            'PASSWORD': os.environ['TC_DB_PASSWORD'],
            'HOST': os.environ['TC_DB_HOST'],
            'PORT': os.environ['TC_DB_PORT'],
            'ATOMIC_REQUESTS': True,
        }
        
        # Close any existing connections and reconnect with new settings
        for conn in connections.all():
            conn.close()
    
    # When not in Docker, we need to set up the database schema
    if not in_docker:
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


@pytest.fixture(scope='function')
def _django_db_helper(request, django_db_setup, django_db_blocker):
    """
    This fixture is used by pytest-django to provide database access for tests.
    Specifically for TestContainers, this ensures database is properly set up.
    """
    django_db_blocker.unblock()
    try:
        yield
    finally:
        django_db_blocker.restore()