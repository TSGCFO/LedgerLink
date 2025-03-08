
import unittest
import json
import re

def normalize_sku(sku):
    """Normalize SKU by removing hyphens and spaces, and converting to uppercase."""
    if sku is None:
        return ""
    # Remove hyphens and spaces, convert to uppercase
    return re.sub(r'[-\s]', '', sku.upper())

def convert_sku_format(sku_data):
    """
    Convert SKU data from various formats to a normalized dictionary.
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
    
class SkuUtilsTests(unittest.TestCase):
    def test_normalize_sku(self):
        """Test the fixed normalize_sku function."""
        self.assertEqual(normalize_sku('SKU-123'), 'SKU123')
        self.assertEqual(normalize_sku('sku 123'), 'SKU123')
        self.assertEqual(normalize_sku('sku-123'), 'SKU123')
        self.assertEqual(normalize_sku(None), '')
        self.assertEqual(normalize_sku(''), '')
    
    def test_convert_sku_format(self):
        """Test the fixed convert_sku_format function."""
        # Test with string input
        sku_data = '[{"sku": "SKU-123", "quantity": 2}, {"sku": "SKU-456", "quantity": 3}]'
        expected = {'SKU123': 2, 'SKU456': 3}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with list input
        sku_data = [{'sku': 'SKU-123', 'quantity': 2}, {'sku': 'SKU-456', 'quantity': 3}]
        expected = {'SKU123': 2, 'SKU456': 3}
        self.assertEqual(convert_sku_format(sku_data), expected)
        
        # Test with invalid input
        self.assertEqual(convert_sku_format('invalid'), {})
        self.assertEqual(convert_sku_format(None), {})

if __name__ == '__main__':
    unittest.main()
