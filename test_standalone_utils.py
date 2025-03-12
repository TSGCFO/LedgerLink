#!/usr/bin/env python
"""
Standalone test for Billing_V2 utility functions.
This doesn't require database connections or Django's test framework.
"""

import os
import sys
import unittest
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

# Now import the utility functions
from Billing_V2.utils.sku_utils import normalize_sku, convert_sku_format, validate_sku_quantity
import json

class TestSkuUtils(unittest.TestCase):
    """Test SKU utility functions"""
    
    def test_normalize_sku(self):
        """Test normalize_sku function"""
        self.assertEqual(normalize_sku("ABC-123"), "ABC123")
        self.assertEqual(normalize_sku("abc 123"), "ABC123")
        self.assertEqual(normalize_sku("abc-1 2 3"), "ABC123")
        self.assertEqual(normalize_sku("  ABC  - 123  "), "ABC123")
        self.assertEqual(normalize_sku(None), "")
        self.assertEqual(normalize_sku(""), "")
        self.assertEqual(normalize_sku(123), "123")
    
    def test_convert_sku_format(self):
        """Test convert_sku_format function"""
        # Test with list of dictionaries
        data = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "quantity": 10}
        ]
        expected = {
            "ABC123": 5,
            "DEF456": 10
        }
        self.assertEqual(convert_sku_format(data), expected)
        
        # Test with JSON string
        json_data = json.dumps(data)
        self.assertEqual(convert_sku_format(json_data), expected)
        
        # Test with duplicates (should aggregate)
        data_with_duplicates = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "ABC123", "quantity": 10}
        ]
        expected_aggregated = {
            "ABC123": 15
        }
        self.assertEqual(convert_sku_format(data_with_duplicates), expected_aggregated)
        
        # Test invalid inputs
        self.assertEqual(convert_sku_format(None), {})
        self.assertEqual(convert_sku_format("{invalid json}"), {})
        self.assertEqual(convert_sku_format({"not": "a list"}), {})
    
    def test_validate_sku_quantity(self):
        """Test validate_sku_quantity function"""
        # Test with valid data
        data = [
            {"sku": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "quantity": 10}
        ]
        self.assertTrue(validate_sku_quantity(data))
        
        # Test with valid JSON string
        json_data = json.dumps(data)
        self.assertTrue(validate_sku_quantity(json_data))
        
        # Test invalid inputs
        self.assertFalse(validate_sku_quantity(None))
        self.assertFalse(validate_sku_quantity("{invalid json}"))
        self.assertFalse(validate_sku_quantity({"not": "a list"}))
        
        # Test with invalid items
        invalid_data = [
            {"missing_sku_key": "ABC-123", "quantity": 5},
            {"sku": "DEF-456", "missing_quantity_key": 10},
            "not a dictionary",
            {"sku": "", "quantity": 5},
            {"sku": "GHI-789", "quantity": 0},
            {"sku": "JKL-012", "quantity": "not a number"}
        ]
        self.assertFalse(validate_sku_quantity(invalid_data))

if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSkuUtils))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    sys.exit(not result.wasSuccessful())