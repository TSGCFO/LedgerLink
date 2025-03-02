import unittest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import io

from billing.utils import (
    ReportDataValidator, 
    ReportFileHandler, 
    ReportCache, 
    ReportFormatter
)

class ReportDataValidatorTests(unittest.TestCase):
    """Tests for the ReportDataValidator class"""
    
    def setUp(self):
        # Create a valid sample report data for testing
        self.valid_report_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Shipping',
                            'amount': '10.50'
                        },
                        {
                            'service_id': 2,
                            'service_name': 'Handling',
                            'amount': '5.25'
                        }
                    ],
                    'total_amount': '15.75'
                },
                {
                    'order_id': 'ORD-002',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Shipping',
                            'amount': '8.30'
                        }
                    ],
                    'total_amount': '8.30'
                }
            ],
            'total_amount': '24.05'
        }
    
    def test_validate_valid_report_data(self):
        """Test validation of valid report data"""
        # Should not raise any exception
        ReportDataValidator.validate_report_data(self.valid_report_data)
    
    def test_validate_invalid_report_type(self):
        """Test validation fails with non-dict report data"""
        invalid_data = ['not a dict']
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_missing_required_field(self):
        """Test validation fails with missing required fields"""
        # Missing total_amount field
        invalid_data = {
            'orders': []
        }
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_invalid_orders_type(self):
        """Test validation fails with invalid orders type"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['orders'] = 'not a list'
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_invalid_order_type(self):
        """Test validation fails with invalid order type"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['orders'] = ['not a dict']
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_missing_order_field(self):
        """Test validation fails with missing order field"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['orders'] = [{'services': [], 'total_amount': '0'}]  # Missing order_id
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_invalid_services_type(self):
        """Test validation fails with invalid services type"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['orders'] = [{
            'order_id': 'ORD-001',
            'services': 'not a list',
            'total_amount': '0'
        }]
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_invalid_service_type(self):
        """Test validation fails with invalid service type"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['orders'] = [{
            'order_id': 'ORD-001',
            'services': ['not a dict'],
            'total_amount': '0'
        }]
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_missing_service_field(self):
        """Test validation fails with missing service field"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['orders'] = [{
            'order_id': 'ORD-001',
            'services': [{'service_id': 1, 'amount': '10'}],  # Missing service_name
            'total_amount': '10'
        }]
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_negative_total_amount(self):
        """Test validation fails with negative total amount"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['total_amount'] = '-10'
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_inconsistent_total_amount(self):
        """Test validation fails with inconsistent total amount"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['total_amount'] = '100'  # Doesn't match sum of order amounts
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)
    
    def test_validate_invalid_amount_format(self):
        """Test validation fails with invalid amount format"""
        invalid_data = self.valid_report_data.copy()
        invalid_data['total_amount'] = 'not a number'
        with self.assertRaises(ValidationError):
            ReportDataValidator.validate_report_data(invalid_data)


class ReportFileHandlerTests(unittest.TestCase):
    """Tests for the ReportFileHandler class"""
    
    def test_estimate_file_size(self):
        """Test file size estimation"""
        test_data = {'key': 'value'}
        json_size = len(json.dumps(test_data))
        estimated_size = ReportFileHandler.estimate_file_size(test_data)
        self.assertEqual(estimated_size, json_size * 1.5)
    
    def test_estimate_file_size_error(self):
        """Test file size estimation with error"""
        test_data = MagicMock()
        test_data.__str__ = MagicMock(side_effect=Exception("Test error"))
        
        # Should return infinity on error
        result = ReportFileHandler.estimate_file_size(test_data)
        self.assertEqual(result, float('inf'))
    
    @patch('billing.utils.getattr')
    def test_validate_file_size_within_limit(self, mock_getattr):
        """Test file size validation within limit"""
        mock_getattr.return_value = 100  # Max size of 100 bytes
        
        # Should not raise any exception
        ReportFileHandler.validate_file_size(50)
    
    @patch('billing.utils.getattr')
    def test_validate_file_size_exceeds_limit(self, mock_getattr):
        """Test file size validation exceeding limit"""
        mock_getattr.return_value = 100  # Max size of 100 bytes
        
        with self.assertRaises(ValidationError):
            ReportFileHandler.validate_file_size(150)
    
    def test_get_file_extension(self):
        """Test getting file extension"""
        self.assertEqual(ReportFileHandler.get_file_extension('excel'), 'xlsx')
        self.assertEqual(ReportFileHandler.get_file_extension('pdf'), 'pdf')
        self.assertEqual(ReportFileHandler.get_file_extension('csv'), 'csv')
        self.assertEqual(ReportFileHandler.get_file_extension('invalid'), '')
    
    def test_get_content_type(self):
        """Test getting content type"""
        self.assertEqual(
            ReportFileHandler.get_content_type('excel'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertEqual(
            ReportFileHandler.get_content_type('pdf'),
            'application/pdf'
        )
        self.assertEqual(
            ReportFileHandler.get_content_type('csv'),
            'text/csv'
        )
        self.assertEqual(
            ReportFileHandler.get_content_type('invalid'),
            'application/octet-stream'
        )


class ReportCacheTests(unittest.TestCase):
    """Tests for the ReportCache class"""
    
    def test_get_cache_key(self):
        """Test generating cache key"""
        key = ReportCache.get_cache_key(1, '2023-01-01', '2023-01-31', 'preview')
        expected_key = 'billing_report_1_2023-01-01_2023-01-31_preview'
        self.assertEqual(key, expected_key)
    
    @patch('billing.utils.cache')
    def test_get_cached_report(self, mock_cache):
        """Test retrieving cached report"""
        mock_data = {'test': 'data'}
        mock_cache.get.return_value = mock_data
        
        result = ReportCache.get_cached_report(1, '2023-01-01', '2023-01-31')
        expected_key = 'billing_report_1_2023-01-01_2023-01-31_preview'
        
        mock_cache.get.assert_called_once_with(expected_key)
        self.assertEqual(result, mock_data)
    
    @patch('billing.utils.cache')
    @patch('billing.utils.getattr')
    def test_cache_report(self, mock_getattr, mock_cache):
        """Test caching a report"""
        mock_getattr.return_value = 3600  # Cache timeout
        mock_data = {'test': 'data'}
        
        ReportCache.cache_report(1, '2023-01-01', '2023-01-31', mock_data)
        expected_key = 'billing_report_1_2023-01-01_2023-01-31_preview'
        
        mock_cache.set.assert_called_once_with(
            expected_key, mock_data, timeout=3600
        )


class ReportFormatterTests(unittest.TestCase):
    """Tests for the ReportFormatter class"""
    
    def test_format_currency(self):
        """Test currency formatting"""
        self.assertEqual(ReportFormatter.format_currency('10.5'), '$10.50')
        self.assertEqual(ReportFormatter.format_currency(10.5), '$10.50')
        self.assertEqual(ReportFormatter.format_currency(Decimal('10.5')), '$10.50')
        self.assertEqual(ReportFormatter.format_currency(0), '$0.00')
        self.assertEqual(ReportFormatter.format_currency('invalid'), '$0.00')
    
    @patch('billing.utils.settings')
    def test_format_date(self, mock_settings):
        """Test date formatting"""
        mock_settings.DATE_FORMAT = '%Y-%m-%d'
        
        # Create a mock date object
        mock_date = MagicMock()
        mock_date.strftime.return_value = '2023-01-15'
        
        result = ReportFormatter.format_date(mock_date)
        mock_date.strftime.assert_called_once_with('%Y-%m-%d')
        self.assertEqual(result, '2023-01-15')
    
    def test_format_date_string(self):
        """Test date formatting with string input"""
        result = ReportFormatter.format_date('2023-01-15')
        self.assertEqual(result, '2023-01-15')
    
    def test_format_service_description(self):
        """Test service description formatting"""
        service = {
            'service_name': 'Shipping',
            'amount': '10.5'
        }
        result = ReportFormatter.format_service_description(service)
        self.assertEqual(result, 'Shipping: $10.50')


if __name__ == '__main__':
    unittest.main()