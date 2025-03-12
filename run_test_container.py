import os
import sys
import subprocess
from datetime import datetime

# First, set up environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'LedgerLink.settings'
os.environ['USE_TESTCONTAINERS'] = 'True'
os.environ['TC_DB_NAME'] = 'test'
os.environ['TC_DB_USER'] = 'test'
os.environ['TC_DB_PASSWORD'] = 'test'
os.environ['TC_DB_HOST'] = 'localhost'
os.environ['TC_DB_PORT'] = '5432'

# Ensure TC_CLOUD_TOKEN is set
if 'TC_CLOUD_TOKEN' not in os.environ:
    token = "tcc_syc_E_w00Z15uBApPw7ZYhPYrNv6TKbMdK1MRTvksR4ow46x"  # Default token from the screenshot
    os.environ['TC_CLOUD_TOKEN'] = token
    print(f"Set TC_CLOUD_TOKEN to default value")
else:
    print(f"Using existing TC_CLOUD_TOKEN")

print("Running Django/pytest with TestContainers")
print(f"Current time: {datetime.now()}")

# Try running the test for SKU utils which don't need database access
try:
    command = [
        "python", "-m", "pytest", 
        "Billing_V2/tests/test_utils.py::SkuUtilsTest::test_normalize_sku_with_valid_input", 
        "-v"
    ]
    print(f"\nRunning command: {' '.join(command)}")
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=os.environ
    )
    
    print(f"\n--- STDOUT ---\n{result.stdout}")
    print(f"\n--- STDERR ---\n{result.stderr}")
    print(f"\nExit code: {result.returncode}")
    
except Exception as e:
    print(f"\nError running command: {e}")
    import traceback
    traceback.print_exc()