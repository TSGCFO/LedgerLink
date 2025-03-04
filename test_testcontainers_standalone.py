#!/usr/bin/env python
"""
Standalone test script for TestContainers with PostgreSQL.
This script doesn't depend on pytest or Django's test framework.
"""

import os
import sys
import time
from decimal import Decimal
from testcontainers.postgres import PostgresContainer

def run_test():
    """Run a standalone test of TestContainers with PostgreSQL."""
    print("\nStarting TestContainers PostgreSQL...")
    
    # Start a PostgreSQL container
    try:
        # Configure Docker not to use any credential helpers
        os.environ["DOCKER_CONFIG"] = "/tmp/docker-config"
        os.makedirs("/tmp/docker-config", exist_ok=True)
        with open("/tmp/docker-config/config.json", "w") as f:
            f.write('{"credsStore":""}')
        
        # Start the container
        postgres = PostgresContainer(
            "postgres:14.5",
            username="postgres",
            password="postgres",
            dbname="testdb"
        )
        postgres.start()
        print(f"Container started at {postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}")
        
        # Get connection details
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        print(f"Container connection: postgresql://{postgres.username}:***@{host}:{port}/{postgres.dbname}")
        
        # Create test tables
        import psycopg2
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=postgres.username,
            password=postgres.password,
            dbname=postgres.dbname
        )
        cursor = connection.cursor()
        
        # Test 1: Basic query works
        print("\nTest 1: Basic query execution")
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        assert result[0] == 1, "Expected query to return 1"
        print("✓ Basic query execution successful")
        
        # Test 2: Create and query a table
        print("\nTest 2: Creating and querying tables")
        cursor.execute("""
            CREATE TABLE test_material (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                description TEXT,
                price DECIMAL(10, 2)
            )
        """)
        cursor.execute("""
            INSERT INTO test_material (name, description, price)
            VALUES (%s, %s, %s)
        """, ["Test Material", "Material for testing", 10.99])
        cursor.execute("SELECT name, price FROM test_material")
        name, price = cursor.fetchone()
        assert name == "Test Material", f"Expected 'Test Material', got '{name}'"
        assert float(price) == 10.99, f"Expected 10.99, got {price}"
        print("✓ Table creation and querying successful")
        
        # Test 3: Materialized view
        print("\nTest 3: Creating and querying materialized views")
        cursor.execute("""
            CREATE MATERIALIZED VIEW test_view AS
            SELECT * FROM test_material
        """)
        cursor.execute("""
            SELECT count(*) 
            FROM pg_class 
            WHERE relname = 'test_view'
            AND relkind = 'm'
        """)
        count = cursor.fetchone()[0]
        assert count == 1, f"Expected 1 materialized view, found {count}"
        print("✓ Materialized view creation successful")
        
        # Clean up and close the connection
        connection.close()
        print("\nAll tests passed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Stop the container
        try:
            postgres.stop()
            print("Container stopped")
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)