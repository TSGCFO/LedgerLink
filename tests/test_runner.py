from django.test.runner import DiscoverRunner
from django.db import connection
import os


class NoMigrationTestRunner(DiscoverRunner):
    """Test runner that disables migrations and creates tables directly."""
    
    def setup_databases(self, **kwargs):
        """
        Set up test databases by creating tables directly rather than running migrations.
        """
        # Get databases from parent method
        databases = super().setup_databases(**kwargs)
        
        # Drop all tables before creating them
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        # Create tables for all apps directly
        from django.apps import apps
        from django.db import connections

        # Force use of syncdb to create tables
        for app_config in apps.get_app_configs():
            if app_config.models_module:
                for model in app_config.get_models():
                    with connection.schema_editor() as schema_editor:
                        try:
                            schema_editor.create_model(model)
                        except Exception as e:
                            print(f"Failed to create model {model}: {e}")
                            
        return databases