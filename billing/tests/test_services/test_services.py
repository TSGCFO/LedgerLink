import unittest
from unittest.mock import patch, MagicMock, call
from django.core.exceptions import ValidationError
from datetime import datetime
import json

from billing.services import BillingReportService

class BillingReportServiceTests(unittest.TestCase):
    """Tests for the BillingReportService class"""
    
    def setUp(self):
        # Sample test data
        self.customer_id = 1
        self.start_date = '2023-01-01'
        self.end_date = '2023-01-31'
        self.user = MagicMock()
        self.service = BillingReportService(self.user)
        
        # Sample report data
        self.report_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Shipping',
                            'amount': '10.50'
                        }
                    ],
                    'total_amount': '10.50'
                }
            ],
            'total_amount': '10.50'
        }
        
        # Sample preview data
        self.preview_data = {
            'orders': self.report_data['orders'],
            'service_totals': {
                '1': {
                    'name': 'Shipping',
                    'amount': 10.5,
                    'order_count': 1
                }
            },
            'total_amount': '10.50',
            'metadata': {
                'generated_at': '2023-01-15T00:00:00',
                'record_count': 1
            }
        }
    
    @patch('billing.services.ReportCache.get_cached_report')
    def test_generate_report_from_cache(self, mock_get_cached):
        """Test generating a report from cache"""
        mock_get_cached.return_value = self.preview_data
        
        result = self.service.generate_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        mock_get_cached.assert_called_once_with(
            self.customer_id,
            self.start_date,
            self.end_date,
            'preview'
        )
        self.assertEqual(result, self.preview_data)
    
    @patch('billing.services.ReportCache.get_cached_report')
    @patch('billing.services.BillingReportService._generate_report_data')
    @patch('billing.services.ReportDataValidator.validate_report_data')
    @patch('billing.services.BillingReportService._save_report')
    @patch('billing.services.BillingReportService._generate_preview')
    @patch('billing.services.ReportCache.cache_report')
    def test_generate_preview_report(
        self, mock_cache, mock_preview, mock_save, 
        mock_validate, mock_generate_data, mock_get_cached
    ):
        """Test generating a preview report"""
        # Setup mocks
        mock_get_cached.return_value = None
        mock_generate_data.return_value = self.report_data
        mock_preview.return_value = self.preview_data
        
        # Call the method
        result = self.service.generate_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Verify all the right methods were called
        mock_get_cached.assert_called_once()
        mock_generate_data.assert_called_once_with(
            self.customer_id, self.start_date, self.end_date
        )
        mock_validate.assert_called_once_with(self.report_data)
        mock_save.assert_called_once_with(
            self.customer_id, self.start_date, self.end_date, self.report_data
        )
        mock_preview.assert_called_once_with(self.report_data)
        mock_cache.assert_called_once_with(
            self.customer_id, self.start_date, self.end_date, 
            self.preview_data, 'preview'
        )
        
        # Verify result
        self.assertEqual(result, self.preview_data)
    
    @patch('billing.services.ReportCache.get_cached_report')
    @patch('billing.services.BillingReportService._generate_report_data')
    @patch('billing.services.ReportDataValidator.validate_report_data')
    @patch('billing.services.ReportFileHandler.estimate_file_size')
    @patch('billing.services.ReportFileHandler.validate_file_size')
    @patch('billing.services.BillingReportService._save_report')
    @patch('billing.services.BillingReportService._generate_excel')
    def test_generate_excel_report(
        self, mock_excel, mock_save, mock_validate_size, 
        mock_estimate_size, mock_validate, mock_generate_data, mock_get_cached
    ):
        """Test generating an Excel report"""
        # Setup mocks
        mock_get_cached.return_value = None
        mock_generate_data.return_value = self.report_data
        mock_estimate_size.return_value = 1000  # 1KB
        mock_excel.return_value = b'excel_data'
        
        # Call the method
        result = self.service.generate_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            output_format='excel'
        )
        
        # Verify all the right methods were called
        mock_get_cached.assert_called_once()
        mock_generate_data.assert_called_once()
        mock_validate.assert_called_once_with(self.report_data)
        mock_estimate_size.assert_called_once_with(self.report_data)
        mock_validate_size.assert_called_once_with(1000)
        mock_save.assert_called_once()
        mock_excel.assert_called_once_with(self.report_data)
        
        # Verify result
        self.assertEqual(result, b'excel_data')
    
    @patch('billing.services.ReportCache.get_cached_report')
    @patch('billing.services.BillingReportService._generate_report_data')
    @patch('billing.services.ReportDataValidator.validate_report_data')
    @patch('billing.services.ReportFileHandler.estimate_file_size')
    @patch('billing.services.ReportFileHandler.validate_file_size')
    @patch('billing.services.BillingReportService._save_report')
    @patch('billing.services.BillingReportService._generate_pdf')
    def test_generate_pdf_report(
        self, mock_pdf, mock_save, mock_validate_size, 
        mock_estimate_size, mock_validate, mock_generate_data, mock_get_cached
    ):
        """Test generating a PDF report"""
        # Setup mocks
        mock_get_cached.return_value = None
        mock_generate_data.return_value = self.report_data
        mock_estimate_size.return_value = 1000  # 1KB
        mock_pdf.return_value = b'pdf_data'
        
        # Call the method
        result = self.service.generate_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            output_format='pdf'
        )
        
        # Verify result
        self.assertEqual(result, b'pdf_data')
    
    @patch('billing.services.ReportCache.get_cached_report')
    @patch('billing.services.BillingReportService._generate_report_data')
    @patch('billing.services.ReportDataValidator.validate_report_data')
    @patch('billing.services.ReportFileHandler.estimate_file_size')
    @patch('billing.services.ReportFileHandler.validate_file_size')
    @patch('billing.services.BillingReportService._save_report')
    @patch('billing.services.BillingReportService._generate_csv')
    def test_generate_csv_report(
        self, mock_csv, mock_save, mock_validate_size, 
        mock_estimate_size, mock_validate, mock_generate_data, mock_get_cached
    ):
        """Test generating a CSV report"""
        # Setup mocks
        mock_get_cached.return_value = None
        mock_generate_data.return_value = self.report_data
        mock_estimate_size.return_value = 1000  # 1KB
        mock_csv.return_value = 'csv_data'
        
        # Call the method
        result = self.service.generate_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            output_format='csv'
        )
        
        # Verify result
        self.assertEqual(result, 'csv_data')
    
    @patch('billing.services.ReportCache.get_cached_report')
    @patch('billing.services.BillingReportService._generate_report_data')
    def test_generate_report_invalid_format(self, mock_generate_data, mock_get_cached):
        """Test generating a report with invalid format"""
        mock_get_cached.return_value = None
        mock_generate_data.return_value = self.report_data
        
        with self.assertRaises(ValidationError):
            self.service.generate_report(
                self.customer_id,
                self.start_date,
                self.end_date,
                output_format='invalid'
            )
    
    @patch('billing.services.BillingReport.objects.create')
    def test_save_report(self, mock_create):
        """Test saving a report to the database"""
        mock_report = MagicMock()
        mock_create.return_value = mock_report
        
        result = self.service._save_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            self.report_data
        )
        
        mock_create.assert_called_once_with(
            customer_id=self.customer_id,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=self.report_data['total_amount'],
            report_data=self.report_data,
            created_by=self.user,
            updated_by=self.user
        )
        self.assertEqual(result, mock_report)
    
    def test_save_report_no_user(self):
        """Test saving a report with no user (development mode)"""
        service = BillingReportService(user=None)
        
        result = service._save_report(
            self.customer_id,
            self.start_date,
            self.end_date,
            self.report_data
        )
        
        self.assertIsNone(result)
    
    @patch('billing.services.generate_billing_report')
    def test_generate_report_data(self, mock_generate):
        """Test generating report data"""
        mock_generate.return_value = self.report_data
        
        result = self.service._generate_report_data(
            self.customer_id,
            self.start_date,
            self.end_date
        )
        
        mock_generate.assert_called_once_with(
            customer_id=self.customer_id,
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.assertEqual(result, self.report_data)
    
    @patch('billing.services.timezone.now')
    def test_generate_preview(self, mock_now):
        """Test generating preview format"""
        mock_now.return_value.isoformat.return_value = '2023-01-15T00:00:00'
        
        result = self.service._generate_preview(self.report_data)
        
        expected_result = {
            'orders': self.report_data['orders'],
            'service_totals': {
                1: {
                    'name': 'Shipping',
                    'amount': 10.5,
                    'order_count': 1
                }
            },
            'total_amount': '10.50',
            'metadata': {
                'generated_at': '2023-01-15T00:00:00',
                'record_count': 1
            }
        }
        
        # Convert result['service_totals'] keys to integers for comparison
        result_service_totals = {}
        for k, v in result['service_totals'].items():
            result_service_totals[int(k)] = v
        result['service_totals'] = result_service_totals
        
        self.assertEqual(result, expected_result)
    
    @patch('billing.services.generate_excel_report')
    def test_generate_excel(self, mock_generate):
        """Test generating Excel format"""
        mock_excel_data = b'excel_data'
        mock_generate.return_value = mock_excel_data
        
        result = self.service._generate_excel(self.report_data)
        
        mock_generate.assert_called_once_with(self.report_data)
        self.assertEqual(result, mock_excel_data)
    
    @patch('billing.services.generate_pdf_report')
    def test_generate_pdf(self, mock_generate):
        """Test generating PDF format"""
        mock_pdf_data = b'pdf_data'
        mock_generate.return_value = mock_pdf_data
        
        result = self.service._generate_pdf(self.report_data)
        
        mock_generate.assert_called_once_with(self.report_data)
        self.assertEqual(result, mock_pdf_data)
    
    @patch('billing.services.generate_csv_report')
    def test_generate_csv(self, mock_generate):
        """Test generating CSV format"""
        mock_csv_data = 'csv_data'
        mock_generate.return_value = mock_csv_data
        
        result = self.service._generate_csv(self.report_data)
        
        mock_generate.assert_called_once_with(self.report_data)
        self.assertEqual(result, mock_csv_data)


if __name__ == '__main__':
    unittest.main()