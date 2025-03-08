#!/usr/bin/env python
"""
Fix the billing calculator implementation to resolve test failures.
"""
import os
import re

def fix_billing_calculator():
    """
    Reads the current billing calculator file and fixes the implementation issues
    with normalize_sku, convert_sku_format, and ncontains operator in RuleEvaluator.
    """
    # Path to the billing calculator file
    file_path = "billing/billing_calculator.py"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Read the current content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the normalize_sku function
    normalize_sku_pattern = r'def normalize_sku\(sku\):.*?\n    return[^}]*?\n'
    normalize_sku_replacement = '''def normalize_sku(sku):
    """Normalize SKU by removing hyphens and spaces, and converting to uppercase."""
    if sku is None:
        return ""
    # Remove hyphens and spaces, convert to uppercase
    return re.sub(r'[-\\s]', '', sku.upper())

'''
    
    content = re.sub(normalize_sku_pattern, normalize_sku_replacement, content, flags=re.DOTALL)
    
    # Fix the convert_sku_format function
    convert_sku_pattern = r'def convert_sku_format\(sku_data\):.*?\n    return result\n'
    convert_sku_replacement = '''def convert_sku_format(sku_data):
    """
    Convert SKU data from various formats to a normalized dictionary.
    
    Args:
        sku_data: String JSON or list of dictionaries with SKU info
        
    Returns:
        Dictionary with normalized SKUs as keys and quantities as values
    """
    result = {}
    
    if sku_data is None:
        return result
        
    try:
        if isinstance(sku_data, str):
            data = json.loads(sku_data)
        else:
            data = sku_data
            
        for item in data:
            sku = normalize_sku(item.get('sku'))
            quantity = item.get('quantity')
            if sku and quantity is not None:
                result[sku] = int(quantity)  # Convert to integer
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
        
    return result

'''
    
    content = re.sub(convert_sku_pattern, convert_sku_replacement, content, flags=re.DOTALL)
    
    # Fix the ncontains operator in RuleEvaluator.evaluate_rule
    ncontains_pattern = r'elif operator in \[\'ncontains\', \'not_contains\'\]:.*?return not any\(value in str\(order_value\) for value in values\)'
    ncontains_replacement = '''elif operator in ['ncontains', 'not_contains']:
            if field == 'sku_quantity':
                try:
                    # Handle SKU quantity field specially
                    if isinstance(order_value, str):
                        skus = json.loads(order_value)
                        for value in values:
                            normalized_value = normalize_sku(value)
                            contains_flag = False
                            for sku in skus.keys():
                                normalized_sku = normalize_sku(sku)
                                if normalized_value in normalized_sku:
                                    contains_flag = True
                                    break
                            if contains_flag:
                                return False
                        return True
                    return True
                except (json.JSONDecodeError, AttributeError):
                    return True
            else:
                # Standard not contains operation
                return not any(value in str(order_value) for value in values)'''
    
    content = re.sub(ncontains_pattern, ncontains_replacement, content, flags=re.DOTALL)
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully fixed {file_path}!")
    return True

if __name__ == "__main__":
    fix_billing_calculator()