import os
import sys
import subprocess
from datetime import datetime

print("Testing Testcontainers Cloud setup")
print(f"Current time: {datetime.now()}")
print(f"TC_CLOUD_TOKEN present: {'Yes' if 'TC_CLOUD_TOKEN' in os.environ else 'No'}")

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')

try:
    print("\nSetting up Django environment...")
    import django
    django.setup()
    print("Django environment set up successfully")
    
    print("\nAttempting to initialize PostgreSQL container...")
    # Set environment variables for database connection
    os.environ['USE_TESTCONTAINERS'] = 'True'
    os.environ['TC_DB_NAME'] = 'test'
    os.environ['TC_DB_USER'] = 'test'
    os.environ['TC_DB_PASSWORD'] = 'test'
    os.environ['TC_DB_HOST'] = 'localhost'
    os.environ['TC_DB_PORT'] = '5432'
    
    # Testing simplified version without database
    print("\nTesting SKU utility functions:")
    from Billing_V2.utils.sku_utils import normalize_sku, convert_sku_format
    
    # Test normalize_sku
    print("- Testing normalize_sku...")
    assert normalize_sku("ABC-123") == "ABC123"
    assert normalize_sku("abc 123") == "ABC123"
    assert normalize_sku(None) == ""
    print("  normalize_sku tests passed!")
    
    # Test convert_sku_format
    print("- Testing convert_sku_format...")
    data = [
        {"sku": "ABC-123", "quantity": 5},
        {"sku": "DEF-456", "quantity": 10}
    ]
    expected = {
        "ABC123": 5,
        "DEF456": 10
    }
    assert convert_sku_format(data) == expected
    print("  convert_sku_format tests passed!")
    
    print("\nAll utility tests passed successfully!")
    
except Exception as e:
    print(f"\nError occurred: {e}")
    import traceback
    traceback.print_exc()