#!/usr/bin/env python
"""
Comprehensive test script specifically for verifying the 'ne' operator fix.
This script provides a thorough test of the 'ne' operator functionality
without requiring Django's test infrastructure or database.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add project root to path so we can import Django modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Initialize Django settings (minimal)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')

# Import the function we need to test
try:
    from rules.views import evaluate_condition
    logger.info("Successfully imported evaluate_condition function")
except ImportError as e:
    logger.error(f"Failed to import evaluate_condition: {e}")
    sys.exit(1)

class MockOrder:
    """Mock order for testing condition evaluation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class OperatorTester:
    """Test the 'ne' operator functionality."""
    
    def __init__(self):
        # Create different types of mock orders for testing
        self.basic_order = MockOrder(
            transaction_id="ORD-123",
            weight_lb="10",
            total_item_qty="5",
            packages="1",
            line_items="2",
            volume_cuft="2.5",
            reference_number="ORD-12345",
            ship_to_name="John Doe",
            ship_to_company="ACME Corp",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_country="US",
            carrier="UPS",
            sku_quantity='{"SKU-123": 2, "SKU-456": 3}',
            notes="Test order notes"
        )
        
        self.empty_order = MockOrder(
            transaction_id="ORD-EMPTY",
            weight_lb="0",
            total_item_qty="0",
            packages="0",
            line_items="0",
            volume_cuft="0",
            ship_to_country="",
            notes=""
        )
        
        self.edge_case_order = MockOrder(
            transaction_id="ORD-EDGE",
            weight_lb="not a number",
            ship_to_country=None,
            notes=None
        )
        
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0
        }
    
    def run_test(self, description, order, field, operator, value, expected):
        """Run a single test case and record results."""
        self.test_results["total"] += 1
        logger.info(f"Test: {description}")
        
        try:
            result = evaluate_condition(order, field, operator, value)
            
            if result == expected:
                logger.info(f"✅ PASSED: {field} {operator} {value} = {result}")
                self.test_results["passed"] += 1
            else:
                logger.error(f"❌ FAILED: {field} {operator} {value} = {result}, expected {expected}")
                self.test_results["failed"] += 1
                
        except Exception as e:
            logger.error(f"⚠️ ERROR: {field} {operator} {value} - {str(e)}")
            self.test_results["errors"] += 1
    
    def test_ne_operator(self):
        """Test the 'ne' operator specifically."""
        # Test with string fields
        self.run_test("Basic 'ne' with non-matching string", 
                     self.basic_order, 'ship_to_country', 'ne', 'CA', True)
        
        self.run_test("Basic 'ne' with matching string", 
                     self.basic_order, 'ship_to_country', 'ne', 'US', False)
        
        # Test with numeric fields
        self.run_test("'ne' with non-matching number", 
                     self.basic_order, 'weight_lb', 'ne', '15', True)
        
        self.run_test("'ne' with matching number", 
                     self.basic_order, 'weight_lb', 'ne', '10', False)
        
        # Test with empty values
        self.run_test("'ne' with empty field and non-empty value", 
                     self.empty_order, 'notes', 'ne', 'test', True)
        
        self.run_test("'ne' with empty field and empty value", 
                     self.empty_order, 'notes', 'ne', '', False)
        
        # Test with NULL values
        self.run_test("'ne' with None field and value", 
                     self.edge_case_order, 'ship_to_country', 'ne', 'test', False)
        
        # Test from bug reproduction
        self.run_test("'ne' with original bug case",
                    self.basic_order, 'ship_to_country', 'ne', 'tom', True)
    
    def test_neq_operator(self):
        """Test the 'neq' operator alias."""
        # Test with string fields
        self.run_test("'neq' with non-matching string", 
                     self.basic_order, 'ship_to_country', 'neq', 'CA', True)
        
        self.run_test("'neq' with matching string", 
                     self.basic_order, 'ship_to_country', 'neq', 'US', False)
        
        # Test with numeric fields
        self.run_test("'neq' with non-matching number", 
                     self.basic_order, 'weight_lb', 'neq', '15', True)
        
        self.run_test("'neq' with matching number", 
                     self.basic_order, 'weight_lb', 'neq', '10', False)
    
    def run_all_tests(self):
        """Run all test methods."""
        logger.info("\n========== STARTING 'ne' OPERATOR TESTS ==========\n")
        
        # Run tests for 'ne' operator
        logger.info("\n----- Testing 'ne' Operator -----")
        self.test_ne_operator()
        
        # Run tests for 'neq' operator alias
        logger.info("\n----- Testing 'neq' Operator (Alias) -----")
        self.test_neq_operator()
        
        # Report results
        logger.info("\n========== TEST RESULTS ==========")
        logger.info(f"Total Tests: {self.test_results['total']}")
        logger.info(f"Passed: {self.test_results['passed']}")
        logger.info(f"Failed: {self.test_results['failed']}")
        logger.info(f"Errors: {self.test_results['errors']}")
        
        if self.test_results["failed"] == 0 and self.test_results["errors"] == 0:
            logger.info("\n✅ ALL TESTS PASSED - The 'ne' operator fix is working correctly!")
            return True
        else:
            logger.error("\n❌ SOME TESTS FAILED - The 'ne' operator fix may not be working correctly!")
            return False

if __name__ == "__main__":
    tester = OperatorTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)