"""
Schema verification utilities for testing.

These utilities help ensure that the database schema matches the
expected model definitions before tests run.
"""
from django.db import connection
import inspect
from django.apps import apps


def verify_field_exists(model_class, field_name):
    """
    Verify that a field exists on a model in the database schema.
    
    Args:
        model_class: The Django model class to check
        field_name: The name of the field to verify
        
    Returns:
        (bool, str): A tuple of (success, message)
    """
    model_meta = model_class._meta
    table_name = model_meta.db_table
    
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s", 
            [table_name]
        )
        columns = [row[0] for row in cursor.fetchall()]
        
        if field_name not in columns:
            message = (
                f"Field '{field_name}' not found in table '{table_name}'. "
                f"Available columns: {', '.join(columns)}"
            )
            return False, message
        
        return True, f"Field '{field_name}' exists in table '{table_name}'"


def verify_model_schema(model_class, required_fields=None):
    """
    Verify that a model's schema in the database matches its definition.
    
    Args:
        model_class: The Django model class to check
        required_fields: Optional list of field names that must exist
        
    Returns:
        (bool, list): A tuple of (success, messages)
    """
    messages = []
    success = True
    
    # Get model fields
    model_meta = model_class._meta
    table_name = model_meta.db_table
    model_fields = {f.name: f for f in model_meta.fields}
    
    # If no specific required fields are provided, check all fields
    if required_fields is None:
        required_fields = list(model_fields.keys())
    
    # Get database columns
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s", 
            [table_name]
        )
        db_columns = [row[0] for row in cursor.fetchall()]
    
    # Check each required field
    for field_name in required_fields:
        if field_name in model_fields:
            if field_name not in db_columns:
                success = False
                messages.append(
                    f"Field '{field_name}' defined in model but missing in database table '{table_name}'"
                )
        else:
            messages.append(f"Field '{field_name}' not defined in model {model_class.__name__}")
    
    if success:
        messages.append(f"All required fields exist in table '{table_name}'")
    
    return success, messages


def verify_app_schema(app_label, required_models=None):
    """
    Verify schema for all models in an app.
    
    Args:
        app_label: The Django app label to check
        required_models: Optional list of model names to check
        
    Returns:
        (bool, dict): A tuple of (success, results_by_model)
    """
    app_config = apps.get_app_config(app_label)
    results = {}
    overall_success = True
    
    models_to_check = []
    for model in app_config.get_models():
        if required_models is None or model.__name__ in required_models:
            models_to_check.append(model)
    
    for model in models_to_check:
        model_success, messages = verify_model_schema(model)
        results[model.__name__] = {
            'success': model_success,
            'messages': messages
        }
        if not model_success:
            overall_success = False
    
    return overall_success, results


def verify_critical_models():
    """
    Verify schema for critical models that commonly cause test failures.
    
    Returns:
        (bool, dict): A tuple of (success, results_by_model)
    """
    critical_models = {
        'customers': ['Customer'],
        'orders': ['Order', 'OrderSKUView'],
        'products': ['Product'],
        'services': ['Service']
    }
    
    all_results = {}
    overall_success = True
    
    for app_label, models in critical_models.items():
        try:
            success, results = verify_app_schema(app_label, models)
            all_results[app_label] = results
            if not success:
                overall_success = False
        except Exception as e:
            all_results[app_label] = {
                'error': str(e)
            }
            overall_success = False
    
    return overall_success, all_results