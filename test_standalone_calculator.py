#!/usr/bin/env python
"""
Standalone test for Billing_V2 calculator.
This uses mocks to avoid database connections.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
import datetime
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

# Now import the calculator utility
from Billing_V2.utils.calculator import BillingCalculator, generate_billing_report

class TestBillingCalculator(unittest.TestCase):
    """Test BillingCalculator class"""
    
    def test_calculate_service_cost_single(self):
        """Test calculating cost for a single service"""
        # Create test data
        service = MagicMock()
        service.charge_type = 'single'
        service.name = 'Test Service'
        
        customer_service = MagicMock()
        customer_service.service = service
        customer_service.unit_price = Decimal('100.00')
        
        order = MagicMock()
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        
        # Calculate cost
        cost = calculator.calculate_service_cost(customer_service, order)
        
        # Verify result
        self.assertEqual(cost, Decimal('100.00'))
        
    def test_calculate_service_cost_quantity(self):
        """Test calculating cost for a quantity-based service"""
        # Create test data
        service = MagicMock()
        service.charge_type = 'quantity'
        service.name = 'Test Service'
        
        customer_service = MagicMock()
        customer_service.service = service
        customer_service.unit_price = Decimal('10.00')
        customer_service.assigned_skus = None
        
        order = MagicMock()
        order.total_item_qty = 5
        
        # Create calculator
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        
        # Calculate cost
        cost = calculator.calculate_service_cost(customer_service, order)
        
        # Verify result (10.00 * 5 = 50.00)
        self.assertEqual(cost, Decimal('50.00'))
        
    @patch('Billing_V2.utils.calculator.BillingCalculator')
    def test_generate_billing_report(self, mock_calculator_class):
        """Test the generate_billing_report function"""
        # Set up mock calculator instance
        mock_instance = MagicMock()
        mock_calculator_class.return_value = mock_instance
        
        # Set up returns for the mock instance
        mock_instance.generate_report.return_value = MagicMock()
        mock_instance.to_json.return_value = '{"test": "data"}'
        mock_instance.to_csv.return_value = 'test,data'
        mock_instance.to_dict.return_value = {'test': 'data'}
        
        # Test with JSON format
        result_json = generate_billing_report(1, '2023-01-01', '2023-01-31', 'json')
        self.assertEqual(result_json, '{"test": "data"}')
        
        # Test with CSV format
        result_csv = generate_billing_report(1, '2023-01-01', '2023-01-31', 'csv')
        self.assertEqual(result_csv, 'test,data')
        
        # Test with dict format
        result_dict = generate_billing_report(1, '2023-01-01', '2023-01-31', 'dict')
        self.assertEqual(result_dict, {'test': 'data'})
        
        # Verify the mock was instantiated correctly (don't check the exact date object)
        self.assertEqual(mock_calculator_class.call_count, 3)
        # Check that customer_id was passed correctly
        for call in mock_calculator_class.call_args_list:
            args, kwargs = call
            self.assertEqual(kwargs['customer_id'], 1)
        
        # Verify each format method was called once
        mock_instance.to_json.assert_called_once()
        mock_instance.to_csv.assert_called_once()
        mock_instance.to_dict.assert_called_once()

if __name__ == "__main__":
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBillingCalculator)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    sys.exit(not result.wasSuccessful())