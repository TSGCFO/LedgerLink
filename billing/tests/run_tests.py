#!/usr/bin/env python
"""
Test runner for the billing application.
This script allows running different test suites with customized settings.
"""

import os
import sys
import argparse
import subprocess
from django.conf import settings


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run billing application tests')
    parser.add_argument(
        '--unit', action='store_true',
        help='Run unit tests only (models, calculators, utils)'
    )
    parser.add_argument(
        '--integration', action='store_true',
        help='Run integration tests only'
    )
    parser.add_argument(
        '--performance', action='store_true',
        help='Run performance tests only'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Run all tests, including performance tests'
    )
    parser.add_argument(
        '--exclude-performance', action='store_true',
        help='Run all tests except performance tests'
    )
    parser.add_argument(
        '--coverage', action='store_true',
        help='Generate code coverage report'
    )
    parser.add_argument(
        '--verbose', '-v', action='count', default=1,
        help='Verbosity level (use -v, -vv, or -vvv for more detailed output)'
    )
    
    return parser.parse_args()


def run_tests(args):
    test_modules = []
    
    if args.unit:
        test_modules.extend([
            'billing.tests.test_models',
            'billing.tests.test_calculator',
            'billing.tests.test_utils',
            'billing.tests.test_exporters'
        ])
    elif args.integration:
        test_modules.append('billing.tests.test_integration')
    elif args.performance:
        test_modules.append('billing.tests.test_performance')
    elif args.all:
        test_modules.append('billing.tests')
    elif args.exclude_performance:
        test_modules.extend([
            'billing.tests.test_models',
            'billing.tests.test_calculator',
            'billing.tests.test_utils',
            'billing.tests.test_exporters',
            'billing.tests.test_integration'
        ])
    else:  # Default - run all except performance tests
        test_modules.extend([
            'billing.tests.test_models',
            'billing.tests.test_calculator',
            'billing.tests.test_utils',
            'billing.tests.test_exporters',
            'billing.tests.test_integration'
        ])
    
    verbosity = min(args.verbose, 3)  # Cap verbosity at 3
    cmd = ['python', 'manage.py', 'test'] + test_modules + ['--verbosity', str(verbosity)]
    
    if args.coverage:
        cmd = ['coverage', 'run'] + cmd
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if args.coverage:
        coverage_cmd = ['coverage', 'report', '-m']
        subprocess.run(coverage_cmd)
        
        # Generate HTML report
        html_cmd = ['coverage', 'html']
        subprocess.run(html_cmd)
        print("\nHTML coverage report generated in htmlcov/index.html")
    
    return result.returncode


if __name__ == '__main__':
    args = parse_arguments()
    sys.exit(run_tests(args))