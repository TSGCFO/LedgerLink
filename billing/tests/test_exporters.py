import unittest
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase
import io
import csv
import json

from billing.exporters import (
    generate_excel_report,
    generate_pdf_report,
    generate_csv_report
)


class ExportersTestBase(TestCase):
    """Base class for exporter tests with shared sample data."""
    
    def setUp(self):
        # Sample report data for testing
        self.report_data = {
            'customer_id': 1,
            'customer_name': 'Test Customer',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Service 1',
                            'amount': '10.50'
                        },
                        {
                            'service_id': 2,
                            'service_name': 'Service 2',
                            'amount': '20.75'
                        }
                    ],
                    'total_amount': '31.25'
                },
                {
                    'order_id': 'ORD-002',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Service 1',
                            'amount': '15.00'
                        }
                    ],
                    'total_amount': '15.00'
                }
            ],
            'total_amount': '46.25'
        }


class ExcelExporterTests(ExportersTestBase):
    """Tests for the Excel report generator."""
    
    @patch('billing.exporters.Workbook')
    def test_generate_excel_report(self, mock_workbook_class):
        """Test generating an Excel report."""
        # Setup mock workbook
        mock_workbook = Mock()
        mock_workbook_class.return_value = mock_workbook
        
        # Setup mock worksheet
        mock_ws = Mock()
        mock_workbook.active = mock_ws
        
        # Setup mock cell
        mock_cell = Mock()
        mock_ws.cell.return_value = mock_cell
        
        # Setup mock column dimensions
        mock_column = Mock()
        mock_column_letter = Mock()
        mock_column[0].column_letter = 'A'
        mock_ws.columns = [[mock_column]]
        mock_ws.column_dimensions = {'A': Mock()}
        
        # Call function
        output = generate_excel_report(self.report_data)
        
        # Verify workbook was created
        mock_workbook_class.assert_called_once()
        
        # Verify worksheet title
        self.assertEqual(mock_ws.title, "Billing Report")
        
        # Verify headers were added (at least the first call to cell)
        mock_ws.cell.assert_called()
        
        # Verify workbook was saved
        mock_workbook.save.assert_called_once()
        
        # Verify output is a BytesIO object
        self.assertIsInstance(output, io.BytesIO)
    
    @patch('billing.exporters.Workbook')
    def test_excel_report_content(self, mock_workbook_class):
        """Test Excel report contains correct content."""
        # Setup mocks
        mock_workbook = Mock()
        mock_workbook_class.return_value = mock_workbook
        
        mock_ws = Mock()
        mock_workbook.active = mock_ws
        
        mock_cell = Mock()
        mock_ws.cell.return_value = mock_cell
        
        mock_column = Mock()
        mock_column[0].column_letter = 'A'
        mock_ws.columns = [[mock_column]]
        mock_ws.column_dimensions = {'A': Mock()}
        
        # Track cell assignments
        cell_values = {}
        
        def side_effect(row, column, value=None):
            cell_key = (row, column)
            cell = Mock()
            if value is not None:
                cell_values[cell_key] = value
                cell.value = value
            return cell
        
        mock_ws.cell.side_effect = side_effect
        
        # Call function
        generate_excel_report(self.report_data)
        
        # Verify headers (row 1)
        self.assertEqual(cell_values.get((1, 1)), "Order ID")
        self.assertEqual(cell_values.get((1, 2)), "Service Name")
        self.assertEqual(cell_values.get((1, 3)), "Amount")
        
        # Count number of data rows
        expected_rows = 0
        for order in self.report_data['orders']:
            expected_rows += len(order['services'])
            
        # Verify total records (header + data rows + total row)
        self.assertEqual(len(cell_values), (3 * (expected_rows + 2)))  # 3 columns, plus header and total rows
        
        # Check that a "Total" row exists
        total_values = [v for k, v in cell_values.items() if v == "Total"]
        self.assertEqual(len(total_values), 1)
    
    def test_excel_report_handles_error(self):
        """Test error handling in Excel report generation."""
        with patch('billing.exporters.Workbook', side_effect=Exception("Test exception")):
            # Should re-raise the exception
            with self.assertRaises(Exception):
                generate_excel_report(self.report_data)


class PdfExporterTests(ExportersTestBase):
    """Tests for the PDF report generator."""
    
    @patch('billing.exporters.SimpleDocTemplate')
    @patch('billing.exporters.Table')
    @patch('billing.exporters.Paragraph')
    @patch('billing.exporters.getSampleStyleSheet')
    def test_generate_pdf_report(self, mock_styles, mock_paragraph, mock_table, mock_doc_class):
        """Test generating a PDF report."""
        # Setup mocks
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc
        
        mock_styles.return_value = {
            'Title': 'Title Style',
            'Normal': 'Normal Style'
        }
        
        # Call function
        output = generate_pdf_report(self.report_data)
        
        # Verify document was created
        mock_doc_class.assert_called_once()
        
        # Verify table creation
        mock_table.assert_called_once()
        
        # Verify paragraphs were created (at least 3: title and 2 subtitle lines)
        self.assertGreaterEqual(mock_paragraph.call_count, 3)
        
        # Verify document was built
        mock_doc.build.assert_called_once()
        
        # Verify output is a BytesIO object
        self.assertIsInstance(output, io.BytesIO)
    
    @patch('billing.exporters.SimpleDocTemplate')
    @patch('billing.exporters.Table')
    @patch('billing.exporters.Paragraph')
    @patch('billing.exporters.getSampleStyleSheet')
    def test_pdf_report_content(self, mock_styles, mock_paragraph, mock_table, mock_doc_class):
        """Test PDF report contains correct content."""
        # Setup mocks
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc
        
        mock_styles.return_value = {
            'Title': 'Title Style',
            'Normal': 'Normal Style'
        }
        
        mock_paragraph.side_effect = lambda text, style: f"Paragraph: {text}"
        
        # Capture table data
        mock_table.side_effect = lambda data: {"table_data": data}
        
        # Call function
        generate_pdf_report(self.report_data)
        
        # Check document build arguments (elements list)
        doc_build_args = mock_doc.build.call_args[0][0]
        
        # Verify title is included
        self.assertTrue(any("Billing Report" in str(arg) for arg in doc_build_args))
        
        # Verify customer name is included
        self.assertTrue(any("Test Customer" in str(arg) for arg in doc_build_args))
        
        # Verify table is included
        table_items = [arg for arg in doc_build_args if isinstance(arg, dict) and 'table_data' in arg]
        self.assertEqual(len(table_items), 1)
        
        # Examine table data
        table_data = table_items[0]['table_data']
        
        # Check for header row
        self.assertEqual(table_data[0], ["Order ID", "Service Name", "Amount"])
        
        # Verify number of rows matches the data plus header and total
        expected_rows = 1  # Header
        for order in self.report_data['orders']:
            expected_rows += len(order['services'])
        expected_rows += 1  # Total row
        
        self.assertEqual(len(table_data), expected_rows)
    
    def test_pdf_report_handles_error(self):
        """Test error handling in PDF report generation."""
        with patch('billing.exporters.SimpleDocTemplate', side_effect=Exception("Test exception")):
            # Should re-raise the exception
            with self.assertRaises(Exception):
                generate_pdf_report(self.report_data)


class CsvExporterTests(ExportersTestBase):
    """Tests for the CSV report generator."""
    
    def test_generate_csv_report(self):
        """Test generating a CSV report."""
        # Call function
        output = generate_csv_report(self.report_data)
        
        # Reset output position
        output.seek(0)
        
        # Parse CSV
        reader = csv.reader(output)
        rows = list(reader)
        
        # Verify header
        self.assertEqual(rows[0], ["Order ID", "Service Name", "Amount"])
        
        # Verify data rows
        row_index = 1
        for order in self.report_data['orders']:
            for service in order['services']:
                self.assertEqual(rows[row_index][0], order['order_id'])
                self.assertEqual(rows[row_index][1], service['service_name'])
                self.assertEqual(rows[row_index][2], f"{float(service['amount']):.2f}")
                row_index += 1
        
        # Verify total row
        self.assertEqual(rows[-1][0], "Total")
        self.assertEqual(rows[-1][2], f"{float(self.report_data['total_amount']):.2f}")
        
        # Verify correct number of rows
        expected_rows = 1  # Header
        for order in self.report_data['orders']:
            expected_rows += len(order['services'])
        expected_rows += 1  # Total row
        
        self.assertEqual(len(rows), expected_rows)
    
    def test_csv_report_handles_error(self):
        """Test error handling in CSV report generation."""
        with patch('billing.exporters.csv.writer', side_effect=Exception("Test exception")):
            # Should re-raise the exception
            with self.assertRaises(Exception):
                generate_csv_report(self.report_data)


if __name__ == '__main__':
    unittest.main()