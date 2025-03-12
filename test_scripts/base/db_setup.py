"""
Database setup helper for tests
This module contains functions to ensure database is properly configured for tests
"""
import os
import sys
import django
from django.db import connection

def setup_test_database():
    """
    Perform additional database setup for tests
    - Skip materialized views if the environment variable is set
    """
    skip_views = os.environ.get('SKIP_MATERIALIZED_VIEWS') == 'True'
    
    print(f"Database setup - Skip materialized views: {skip_views}")
    
    if not skip_views:
        # If not skipping views, ensure they're created and accessible
        try:
            with connection.cursor() as cursor:
                # Check if the CustomerServiceView exists
                cursor.execute("""
                    SELECT to_regclass('customer_services_customerserviceview');
                """)
                if cursor.fetchone()[0] is None:
                    print("CustomerServiceView does not exist - creating it")
                    # Run the SQL to create it directly if necessary
                    cursor.execute("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS customer_services_customerserviceview AS
                    SELECT
                        cs.id,
                        cs.customer_id,
                        c.company_name,
                        s.id AS service_id,
                        s.name AS service_name,
                        s.description AS service_description,
                        s.price,
                        s.charge_type
                    FROM
                        customer_services_customerservice cs
                    JOIN
                        customers_customer c ON cs.customer_id = c.id
                    JOIN
                        services_service s ON cs.service_id = s.id
                    WITH NO DATA;
                    """)
        except Exception as e:
            print(f"Warning: Failed to verify materialized views: {e}")
            # Continue anyway - tests will fail explicitly if views are needed
    
    return True

if __name__ == "__main__":
    # Can be run as a standalone script
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LedgerLink.settings.test")
    django.setup()
    setup_test_database()
    print("Database setup complete")