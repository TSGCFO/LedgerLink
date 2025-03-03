"""
Validation utilities for rule components.
Centralizes validation logic to avoid duplication between models and views.
"""
from django.core.exceptions import ValidationError
import json
import logging

logger = logging.getLogger(__name__)

def validate_sku_quantity(value):
    """Validate the SKU quantity format"""
    if not isinstance(value, (list, dict)):
        return False

    # If it's a list, each item should be a dict with 'sku' and 'quantity'
    if isinstance(value, list):
        return all(
            isinstance(item, dict) and
            'sku' in item and
            'quantity' in item and
            isinstance(item['quantity'], (int, float))
            for item in value
        )

    # If it's a dict, each value should be a quantity
    return all(isinstance(v, (int, float)) for v in value.values())

def validate_field_operator_value(field, operator, value):
    """
    Validate that a field, operator, and value combination is valid.
    Returns (is_valid, error_message) tuple.
    """
    # Define field categories
    string_fields = [
        'reference_number', 'ship_to_name', 'ship_to_company',
        'ship_to_city', 'ship_to_state', 'ship_to_country',
        'carrier', 'sku_name', 'notes'
    ]
    numeric_fields = [
        'weight_lb', 'line_items', 'total_item_qty',
        'volume_cuft', 'sku_count', 'packages'
    ]
    sku_fields = ['sku_quantity']
    
    # Define operator categories
    string_operators = ['eq', 'ne', 'contains', 'ncontains', 'startswith', 'endswith']
    numeric_operators = ['gt', 'lt', 'eq', 'ne', 'ge', 'le']
    sku_operators = ['contains', 'ncontains', 'only_contains', 'in', 'ni']
    
    # Get values list
    values = [v.strip() for v in value.split(';') if v.strip()] if value else []
    
    # String field validation
    if field in string_fields:
        if operator not in string_operators:
            return False, f"Operator '{operator}' is not valid for string fields."
    
    # Numeric field validation
    elif field in numeric_fields:
        if operator not in numeric_operators:
            return False, f"Operator '{operator}' is not valid for numeric fields."
        
        if operator in ['gt', 'lt', 'ge', 'le', 'eq', 'ne']:
            try:
                [float(v) for v in values]
            except ValueError:
                return False, f"Operator '{operator}' requires numeric values."
    
    # SKU quantity validation
    elif field == 'sku_quantity':
        if operator not in sku_operators:
            return False, f"Operator '{operator}' is not valid for SKU quantity."
        
        if not values:
            return False, "At least one SKU must be specified"
    
    return True, None

def validate_calculation(calculation_type, calculation_data, tier_config=None):
    """
    Validate a calculation configuration.
    Returns (is_valid, error_message) tuple.
    
    Parameters:
        calculation_type (str): The type of calculation to validate
        calculation_data (dict): The calculation data including value
        tier_config (dict, optional): The tier configuration at the model level
            for case_based_tier calculations
    """
    valid_types = [
        'flat_fee', 'percentage', 'per_unit', 'weight_based',
        'volume_based', 'tiered_percentage', 'product_specific', 
        'case_based_tier'
    ]
    
    if calculation_type not in valid_types:
        return False, f"Invalid calculation type: {calculation_type}"
    
    if 'value' not in calculation_data:
        return False, "Value is required for calculation"
    
    try:
        float(calculation_data['value'])
    except (ValueError, TypeError):
        return False, "Value must be a number"
    
    # Special handling for case_based_tier
    if calculation_type == 'case_based_tier':
        # First check if tier_config is in the calculation data (legacy format)
        if 'tier_config' in calculation_data:
            tier_config_to_validate = calculation_data['tier_config']
        # Otherwise use the model-level tier_config
        elif tier_config:
            tier_config_to_validate = tier_config
        else:
            return False, "tier_config is required for case_based_tier"
            
        # Validate tier_config
        if not isinstance(tier_config_to_validate, dict):
            return False, "tier_config must be a dictionary"
            
        if 'ranges' not in tier_config_to_validate:
            return False, "ranges are required in tier_config"
            
        ranges = tier_config_to_validate['ranges']
        if not isinstance(ranges, list):
            return False, "ranges must be a list"
            
        for tier in ranges:
            if not all(k in tier for k in ('min', 'max', 'multiplier')):
                return False, "Each tier must have min, max, and multiplier"
                
            try:
                min_val = float(tier['min'])
                max_val = float(tier['max'])
                multiplier = float(tier['multiplier'])
                
                if min_val < 0 or max_val < 0 or multiplier < 0:
                    return False, "Min, max, and multiplier values must be non-negative"
                
                if min_val > max_val:
                    return False, f"Min value ({min_val}) cannot be greater than max value ({max_val})"
            except (TypeError, ValueError):
                return False, "Min, max, and multiplier values must be valid numbers"
        
        # Validate excluded_skus if present
        excluded_skus = tier_config_to_validate.get('excluded_skus', [])
        if excluded_skus and not isinstance(excluded_skus, list):
            return False, "excluded_skus must be a list of SKU strings"
    
    return True, None