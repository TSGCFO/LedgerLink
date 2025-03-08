#!/usr/bin/env python
# Test runner script for customer_services without materialized views

import os
import sys
import django
from django.conf import settings
from django.test.runner import DiscoverRunner

if __name__ == "__main__":
    # Set environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'LedgerLink.settings'
    os.environ['SKIP_MATERIALIZED_VIEWS'] = 'True'
    
    # Initialize Django
    django.setup()
    
    # Create a test runner that automatically finds tests
    test_runner = DiscoverRunner(verbosity=2)
    
    # Find and run the tests in the customer_services app
    test_apps = ['customer_services.tests']
    failures = test_runner.run_tests(test_apps)
    
    # Exit with appropriate code
    sys.exit(bool(failures))