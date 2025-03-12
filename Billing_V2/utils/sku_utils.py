import json
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Global cache for normalized SKUs
_normalized_sku_cache = {}

def normalize_sku(sku):
    """
    Normalize a SKU by removing hyphens and spaces, and converting to uppercase.
    With built-in caching to improve performance for repeated SKUs.
    
    Args:
        sku: The SKU to normalize
        
    Returns:
        Normalized SKU string
    """
    # Check cache first
    if sku in _normalized_sku_cache:
        return _normalized_sku_cache[sku]
        
    try:
        if sku is None:
            return ""
        
        # Remove hyphens and spaces, convert to uppercase
        normalized = str(sku).replace("-", "").replace(" ", "").upper()
        
        # Cache result
        _normalized_sku_cache[sku] = normalized
        return normalized
    except Exception as e:
        # Only log errors at debug level for performance
        logger.debug(f"Error normalizing SKU {sku}: {str(e)}")
        return ""

# Set up LRU cache for JSON parsing
@lru_cache(maxsize=128)
def _parse_sku_json(sku_json):
    """Parse JSON string of SKU data with caching"""
    try:
        return json.loads(sku_json)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in SKU data")
        return []

def convert_sku_format(sku_data):
    """
    Convert SKU data from various formats to a normalized dictionary.
    Optimized for performance with caching for common patterns.
    
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
        
        # Parse JSON if string - use cached version for repeated strings
        if isinstance(sku_data, str):
            # Use a cache for parsing JSON strings
            sku_data = _parse_sku_json(sku_data)
        
        # Ensure we have a list
        if not isinstance(sku_data, list):
            logger.debug(f"SKU data is not a list")
            return result
        
        # Pre-allocate dictionary capacity for performance
        result = {}
        
        # Process each item - use fast path for well-formed data
        for item in sku_data:
            if not isinstance(item, dict):
                continue
                
            sku = item.get('sku')
            quantity = item.get('quantity')
            
            if not sku or not quantity:
                continue
                
            # Normalize SKU - use cached version
            normalized_sku = normalize_sku(sku)
            if not normalized_sku:
                continue
                
            # Convert quantity to integer
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    continue
            except (ValueError, TypeError):
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