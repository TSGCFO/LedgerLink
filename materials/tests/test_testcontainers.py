import os
import sys
import pytest
import django
from django.db import connection
from decimal import Decimal
from testcontainers.postgres import PostgresContainer
import time

# Configure Django settings before importing models
from django.conf import settings
from django import setup as django_setup

# Set up a standalone test container
@pytest.fixture(scope="session", autouse=True)
def setup_django_with_testcontainers():
    """
    Create and start a PostgreSQL container for testing,
    then set up Django to use it.
    """
    print("\nStarting TestContainers PostgreSQL for testing...")
    
    # Start a PostgreSQL container
    container = PostgresContainer(
        "postgres:14.5", 
        username="postgres",
        password="postgres",
        dbname="testdb"
    )
    container.start()
    
    # Configure Django settings to use the TestContainers PostgreSQL
    os.environ["DJANGO_SETTINGS_MODULE"] = "LedgerLink.settings"
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": container.dbname,
        "USER": container.username,
        "PASSWORD": container.password,
        "HOST": container.get_container_host_ip(),
        "PORT": str(container.get_exposed_port(5432)),
    }
    print(f"TestContainers PostgreSQL running at: {container.get_container_host_ip()}:{container.get_exposed_port(5432)}")
    
    # Make sure Django is set up
    django_setup()
    
    # Create the test tables
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS materials_material (id SERIAL PRIMARY KEY, name VARCHAR(100), description TEXT, unit_price DECIMAL(10, 2))")
        cursor.execute("CREATE TABLE IF NOT EXISTS materials_boxprice (id SERIAL PRIMARY KEY, box_type VARCHAR(100), price DECIMAL(10, 2), length DECIMAL(10, 2), width DECIMAL(10, 2), height DECIMAL(10, 2))")
    
    yield container
    
    # Stop the container
    print("\nStopping TestContainers PostgreSQL...")
    container.stop()
    print("TestContainers PostgreSQL stopped.")

# Import models after Django is set up with our container
from materials.models import Material, BoxPrice


class TestTestContainersSetup:
    """Tests to verify that TestContainers is working correctly with Django tests."""
    
    def test_postgresql_connection(self):
        """Test that we can connect to the PostgreSQL database via TestContainers."""
        # Check connection is active
        assert connection.is_usable()
        
        # Get connection details
        db_settings = connection.settings_dict
        
        # Check if host is not the default localhost
        db_host = db_settings.get('HOST')
        # TestContainers typically sets a Docker container IP, not localhost
        assert db_host != 'localhost'
        
        # Verify we can execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_model_creation(self):
        """Test that we can create and retrieve model instances in the TestContainers database."""
        # Create a test material
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO materials_material (name, description, unit_price)
                VALUES (%s, %s, %s) RETURNING id
            """, ["TestContainers Test Material", "Testing with TestContainers", Decimal("25.99")])
            material_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO materials_boxprice (box_type, price, length, width, height)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, ["TestContainers Box", Decimal("12.50"), Decimal("10.0"), Decimal("8.0"), Decimal("6.0")])
            box_id = cursor.fetchone()[0]
        
        # Retrieve and verify
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM materials_material WHERE id = %s", [material_id])
            material_name = cursor.fetchone()[0]
            assert material_name == "TestContainers Test Material"
            
            cursor.execute("SELECT box_type FROM materials_boxprice WHERE id = %s", [box_id])
            box_type = cursor.fetchone()[0]
            assert box_type == "TestContainers Box"
    
    def test_materialized_view(self):
        """Test that PostgreSQL-specific objects like materialized views are created correctly."""
        # Since this is a fresh container, we need to create the materialized views first
        with connection.cursor() as cursor:
            # Create a simple materialized view for testing
            cursor.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS test_materialized_view AS
                SELECT 1 as id, 'test' as name
            """)
            
            # Check if the materialized view exists
            cursor.execute("""
                SELECT count(*) 
                FROM pg_class 
                WHERE relname = 'test_materialized_view'
                AND relkind = 'm'
            """)
            result = cursor.fetchone()
            assert result[0] > 0, "Materialized view was not created correctly"