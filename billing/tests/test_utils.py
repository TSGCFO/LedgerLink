from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings
import json
from decimal import Decimal
from datetime import datetime
import unittest
from unittest.mock import patch, Mock

from billing.utils import (
    ReportDataValidator, ReportCache, ReportFileHandler,
    ReportFormatter, log_report_generation
)


class ReportDataValidatorTests(TestCase):
    """Tests for the ReportDataValidator class."""
    
    def setUp(self):
        # Valid report data for testing
        self.valid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Service 1',
                            'amount': '10.00'
                        }
                    ],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '10.00'
        }
    
    def test_valid_data(self):
        """Test validation of valid report data."""
        # Validation should pass without error
        ReportDataValidator.validate_report_data(self.valid_data)
    
    def test_invalid_data_type(self):
        """Test validation fails for non-dict data."""
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(['not', 'a', 'dict'])
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        # Missing 'orders' field
        invalid_data = {'total_amount': '10.00'}
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
        
        # Missing 'total_amount' field
        invalid_data = {'orders': []}
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_orders_not_list(self):
        """Test validation fails if orders is not a list."""
        invalid_data = {
            'orders': 'not a list',
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_invalid_order(self):
        """Test validation fails for invalid order structure."""
        # Order is not a dict
        invalid_data = {
            'orders': ['not a dict'],
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
        
        # Order missing required field 'order_id'
        invalid_data = {
            'orders': [
                {
                    'services': [],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
        
        # Order services is not a list
        invalid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': 'not a list',
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_invalid_service(self):
        """Test validation fails for invalid service structure."""
        # Service is not a dict
        invalid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': ['not a dict'],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
        
        # Service missing required field
        invalid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'amount': '10.00'
                            # Missing 'service_name'
                        }
                    ],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_negative_amount(self):
        """Test validation fails for negative amount."""
        invalid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Service 1',
                            'amount': '10.00'
                        }
                    ],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '-10.00'  # Negative total
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_invalid_amount_format(self):
        """Test validation fails for invalid amount format."""
        invalid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Service 1',
                            'amount': 'not a number'
                        }
                    ],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '10.00'
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_sum_mismatch(self):
        """Test validation fails if order amounts don't sum to total."""
        invalid_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Service 1',
                            'amount': '10.00'
                        }
                    ],
                    'total_amount': '10.00'
                }
            ],
            'total_amount': '20.00'  # Doesn't match sum of order totals
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)


class ReportFileHandlerTests(TestCase):
    """Tests for the ReportFileHandler class."""
    
    def test_estimate_file_size(self):
        """Test estimating file size."""
        data = {'key': 'value'}
        
        # Size should be larger than the JSON string length
        json_size = len(json.dumps(data))
        estimated_size = ReportFileHandler.estimate_file_size(data)
        
        self.assertGreater(estimated_size, json_size)
    
    def test_validate_file_size_valid(self):
        """Test validating file size within limits."""
        # Size within limit should not raise error
        max_size = getattr(settings, 'MAX_REPORT_SIZE', 10 * 1024 * 1024)
        valid_size = max_size - 1
        
        # Should not raise error
        ReportFileHandler.validate_file_size(valid_size)
    
    def test_validate_file_size_invalid(self):
        """Test validating file size exceeding limits."""
        # Size exceeding limit should raise error
        max_size = getattr(settings, 'MAX_REPORT_SIZE', 10 * 1024 * 1024)
        invalid_size = max_size + 1
        
        with self.assertRaises(ValidationError):
            ReportFileHandler.validate_file_size(invalid_size)
    
    def test_get_file_extension(self):
        """Test getting file extension for different formats."""
        test_cases = {
            'excel': 'xlsx',
            'pdf': 'pdf',
            'csv': 'csv',
            'unknown': ''  # Default for unknown format
        }
        
        for format_name, expected_ext in test_cases.items():
            self.assertEqual(
                ReportFileHandler.get_file_extension(format_name),
                expected_ext
            )
    
    def test_get_content_type(self):
        """Test getting content type for different formats."""
        test_cases = {
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'unknown': 'application/octet-stream'  # Default for unknown format
        }
        
        for format_name, expected_type in test_cases.items():
            self.assertEqual(
                ReportFileHandler.get_content_type(format_name),
                expected_type
            )


class ReportCacheTests(TestCase):
    """Tests for the ReportCache class."""
    
    def setUp(self):
        self.customer_id = 1
        self.start_date = '2023-01-01'
        self.end_date = '2023-01-31'
        self.format = 'preview'
        self.test_data = {'test': 'data'}
        
        # Clear cache before each test
        cache.clear()
    
    def test_get_cache_key(self):
        """Test generating cache key."""
        expected_key = f'billing_report_{self.customer_id}_{self.start_date}_{self.end_date}_{self.format}'
        actual_key = ReportCache.get_cache_key(
            self.customer_id, self.start_date, self.end_date, self.format
        )
        self.assertEqual(actual_key, expected_key)
    
    def test_cache_and_retrieve_report(self):
        """Test caching and retrieving a report."""
        # Cache the report
        ReportCache.cache_report(
            self.customer_id, self.start_date, self.end_date, 
            self.test_data, self.format
        )
        
        # Retrieve from cache
        cached_data = ReportCache.get_cached_report(
            self.customer_id, self.start_date, self.end_date, self.format
        )
        
        self.assertEqual(cached_data, self.test_data)
    
    def test_retrieve_nonexistent_report(self):
        """Test retrieving a report that doesn't exist in cache."""
        # Try to retrieve non-existent report
        cached_data = ReportCache.get_cached_report(
            self.customer_id, self.start_date, self.end_date, self.format
        )
        
        self.assertIsNone(cached_data)
    
    @patch('django.core.cache.cache.set')
    def test_cache_timeout(self, mock_cache_set):
        """Test cache timeout setting."""
        # This tests if correct timeout is used when caching
        ReportCache.cache_report(
            self.customer_id, self.start_date, self.end_date, 
            self.test_data, self.format
        )
        
        # Get the default timeout from settings
        timeout = getattr(settings, 'REPORT_CACHE_TIMEOUT', 3600)
        
        # Verify cache.set was called with correct arguments
        mock_cache_set.assert_called_once()
        self.assertEqual(mock_cache_set.call_args[1]['timeout'], timeout)


class ReportFormatterTests(TestCase):
    """Tests for the ReportFormatter class."""
    
    def test_format_currency(self):
        """Test currency formatting."""
        test_cases = [
            (Decimal('10.00'), '$10.00'),
            (Decimal('10.50'), '$10.50'),
            (Decimal('10'), '$10.00'),
            ('10.75', '$10.75'),
            (0, '$0.00'),
        ]
        
        for value, expected in test_cases:
            self.assertEqual(
                ReportFormatter.format_currency(value),
                expected
            )
    
    def test_format_currency_invalid_input(self):
        """Test currency formatting with invalid input."""
        test_cases = [
            ('not a number', '$0.00'),
            (None, '$0.00'),
            ({}, '$0.00'),
        ]
        
        for value, expected in test_cases:
            self.assertEqual(
                ReportFormatter.format_currency(value),
                expected
            )
    
    def test_format_date(self):
        """Test date formatting."""
        date = datetime(2023, 1, 15)
        expected = date.strftime(settings.DATE_FORMAT)
        
        self.assertEqual(
            ReportFormatter.format_date(date),
            expected
        )
    
    def test_format_date_string(self):
        """Test date formatting with a string."""
        date_str = '2023-01-15'
        
        # Should return the string as is
        self.assertEqual(
            ReportFormatter.format_date(date_str),
            date_str
        )
    
    def test_format_service_description(self):
        """Test service description formatting."""
        service = {
            'service_name': 'Test Service',
            'amount': '10.50'
        }
        expected = 'Test Service: $10.50'
        
        self.assertEqual(
            ReportFormatter.format_service_description(service),
            expected
        )


class LogReportGenerationTests(TestCase):
    """Tests for the log_report_generation decorator."""
    
    def test_log_report_generation_success(self):
        """Test the decorator logs successful function execution."""
        
        # Create a mock function
        @log_report_generation
        def mock_function(*args, **kwargs):
            return 'success'
        
        with patch('billing.utils.logger.info') as mock_info, \
             patch('billing.utils.logger.error') as mock_error:
            
            # Call the decorated function
            result = mock_function('arg1', kwarg1='value1')
            
            # Verify function was called and returned correctly
            self.assertEqual(result, 'success')
            
            # Verify logging happened
            self.assertEqual(mock_info.call_count, 2)
            self.assertEqual(mock_error.call_count, 0)
    
    def test_log_report_generation_error(self):
        """Test the decorator logs function execution errors."""
        
        # Create a mock function that raises an exception
        @log_report_generation
        def mock_function(*args, **kwargs):
            raise ValueError('test error')
        
        with patch('billing.utils.logger.info') as mock_info, \
             patch('billing.utils.logger.error') as mock_error:
            
            # Call the decorated function
            with self.assertRaises(ValueError):
                mock_function('arg1', kwarg1='value1')
            
            # Verify logging happened
            self.assertEqual(mock_info.call_count, 1)
            self.assertEqual(mock_error.call_count, 1)