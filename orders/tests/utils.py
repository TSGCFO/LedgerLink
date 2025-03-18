"""
Utility functions for orders app tests
"""
from django.db import connection


def verify_field_exists(model_class, field_name):
    """
    Verify that a specific field exists on a model's database table.
    
    Args:
        model_class: The Django model class
        field_name: The name of the field to check
        
    Returns:
        tuple: (success, message)
    """
    table_name = model_class._meta.db_table
    
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)",
            (table_name,)
        )
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return False, f"Table {table_name} does not exist"
        
        # Check for the specific column
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s",
            (table_name,)
        )
        columns = [row[0] for row in cursor.fetchall()]
        
        if field_name not in columns:
            return False, f"Field {field_name} does not exist in {table_name}. Available columns: {columns}"
    
    return True, f"Field {field_name} exists in {table_name}"


def verify_model_schema(model_class):
    """
    Verify that all fields in a model exist in the database table.
    
    Args:
        model_class: The Django model class
        
    Returns:
        tuple: (success, message)
    """
    table_name = model_class._meta.db_table
    
    # Get model fields, excluding relations and special fields
    model_fields = []
    skip_fields = ['id', 'customer']  # Fields to skip in verification
    
    for f in model_class._meta.fields:
        # Skip relation fields and fields in skip_fields
        if f.name not in skip_fields:
            model_fields.append(f.name)
    
    missing_fields = []
    
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)",
            (table_name,)
        )
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return False, f"Table {table_name} does not exist"
        
        # Check for each field
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s",
            (table_name,)
        )
        columns = [row[0] for row in cursor.fetchall()]
        
        # Special handling for relations
        if 'customer_id' in columns and 'customer' in skip_fields:
            # This is okay - Django creates customer_id for ForeignKey fields
            print(f"Found customer_id in database for customer field")
        
        for field in model_fields:
            if field not in columns:
                # Check if this might be a relation field (field_id exists)
                relation_field = f"{field}_id"
                if relation_field not in columns:
                    missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing fields in {table_name}: {', '.join(missing_fields)}"
    
    return True, f"All fields exist in {table_name}"