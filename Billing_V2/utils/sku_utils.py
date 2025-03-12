import json
import logging

logger = logging.getLogger(__name__)


def normalize_sku(sku):
    """
    Normalize a SKU by removing hyphens and spaces, and converting to uppercase.
    
    Args:
        sku: The SKU to normalize
        
    Returns:
        Normalized SKU string
    """
    try:
        if sku is None:
            return ""
        
        # Remove hyphens and spaces, convert to uppercase
        normalized = str(sku).replace("-", "").replace(" ", "").upper()
        return normalized
    except Exception as e:
        logger.error(f"Error normalizing SKU {sku}: {str(e)}")
        return ""


def convert_sku_format(sku_data):
    """
    Convert SKU data from various formats to a normalized dictionary.
    
    Args:
        sku_data: SKU data as string or list
        
    Returns:
        Dictionary mapping normalized SKUs to quantities
    """
    result = {}
    
    try:
        # Return empty result if None
        if sku_data is None:
            return result
        
        # Parse JSON if string
        if isinstance(sku_data, str):
            try:
                sku_data = json.loads(sku_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in SKU data: {sku_data}")
                return result
        
        # Ensure we have a list
        if not isinstance(sku_data, list):
            logger.error(f"SKU data is not a list: {sku_data}")
            return result
        
        # Process each item
        for item in sku_data:
            if not isinstance(item, dict):
                logger.error(f"SKU item is not a dictionary: {item}")
                continue
                
            if 'sku' not in item or 'quantity' not in item:
                logger.error(f"SKU item missing required keys: {item}")
                continue
                
            # Normalize SKU
            normalized_sku = normalize_sku(item['sku'])
            if not normalized_sku:
                logger.error(f"Empty normalized SKU: {item}")
                continue
                
            # Convert quantity to integer
            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    logger.error(f"Invalid quantity {quantity} for SKU {normalized_sku}")
                    continue
            except (ValueError, TypeError):
                logger.error(f"Invalid quantity {item['quantity']} for SKU {normalized_sku}")
                continue
                
            # Add to result, aggregating if duplicate
            if normalized_sku in result:
                result[normalized_sku] += quantity
            else:
                result[normalized_sku] = quantity
                
        return result
    except Exception as e:
        logger.error(f"Error converting SKU format: {str(e)}")
        return {}


def validate_sku_quantity(sku_data):
    """
    Validate SKU quantity data.
    
    Args:
        sku_data: SKU data to validate
        
    Returns:
        Boolean indicating if data is valid
    """
    try:
        # Parse JSON if string
        if isinstance(sku_data, str):
            try:
                sku_data = json.loads(sku_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in SKU data: {sku_data}")
                return False
        
        # Convert to dictionary format
        sku_dict = convert_sku_format(sku_data)
        if not sku_dict:
            return False
            
        # Validate each SKU and quantity
        for sku, quantity in sku_dict.items():
            if not isinstance(sku, str) or not sku:
                return False
                
            try:
                quantity_num = float(quantity)
                if quantity_num <= 0:
                    return False
            except (ValueError, TypeError):
                return False
                
        return True
    except Exception as e:
        logger.error(f"Error validating SKU quantity: {str(e)}")
        return False