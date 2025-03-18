"""
Utility functions for billing app tests
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
    skip_fields = ['id', 'customer', 'created_by', 'updated_by']  # Fields to skip in verification
    
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
        for relation_field in skip_fields:
            if f"{relation_field}_id" in columns:
                print(f"Found {relation_field}_id in database for {relation_field} field")
        
        for field in model_fields:
            if field not in columns:
                # Check if this might be a relation field (field_id exists)
                relation_field = f"{field}_id"
                if relation_field not in columns:
                    missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing fields in {table_name}: {', '.join(missing_fields)}"
    
    return True, f"All fields exist in {table_name}"


def verify_billing_schema():
    """
    Verify that the billing tables and views exist and have the correct structure.
    
    Returns:
        tuple: (success, message)
    """
    required_tables = [
        'billing_billingreport',
        'billing_billingreportdetail'
    ]
    
    with connection.cursor() as cursor:
        # Check for required tables
        for table in required_tables:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)",
                (table,)
            )
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return False, f"Required table {table} does not exist"
            
        # Check for specific fields in billing_billingreport
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='billing_billingreport' AND column_name='generated_at')"
        )
        generated_at_exists = cursor.fetchone()[0]
        
        if not generated_at_exists:
            return False, "Field generated_at does not exist in billing_billingreport"
    
    return True, "Billing schema verification passed"