from django.test import TestCase
import io
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from bulk_operations.services.import_handler import BulkImportHandler
from bulk_operations.services.validators import BulkImportValidator
from bulk_operations.serializers import BulkSerializerFactory, MaterialBulkSerializer
from materials.models import Material


class BulkImportHandlerTests(TestCase):
    """Test cases for the BulkImportHandler class"""

    def setUp(self):
        """Set up test data"""
        # Create test CSV data
        self.csv_data = io.StringIO()
        self.csv_data.write("name,description,unit_price\n")
        self.csv_data.write("Test Material,A material for testing,25.99\n")
        self.csv_data.write("Second Material,Another test material,15.50\n")
        self.csv_data.seek(0)
        
        # Create an invalid CSV (missing required field)
        self.invalid_csv_data = io.StringIO()
        self.invalid_csv_data.write("description,unit_price\n")  # Missing 'name'
        self.invalid_csv_data.write("A material for testing,25.99\n")
        self.invalid_csv_data.seek(0)
        
        # Create test Excel data
        self.excel_data = io.BytesIO()
        df = pd.DataFrame({
            'name': ['Excel Material', 'Second Excel Material'],
            'description': ['Excel test material', 'Another excel test'],
            'unit_price': [19.99, 29.99]
        })
        df.to_excel(self.excel_data, index=False)
        self.excel_data.seek(0)
        
        # Create malformed CSV
        self.malformed_csv_data = io.StringIO()
        self.malformed_csv_data.write("name,description,unit_price\n")
        self.malformed_csv_data.write("Test Material,A material for testing\n")  # Missing value
        self.malformed_csv_data.seek(0)
        
        # Create SimpleUploadedFile for view testing
        self.csv_data.seek(0)
        self.csv_file = SimpleUploadedFile(
            'materials.csv',
            self.csv_data.read().encode(),
            content_type='text/csv'
        )
        
    def test_init_with_valid_format(self):
        """Test initialization with valid format"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        self.assertEqual(handler.template_type, 'materials')
        self.assertEqual(handler.file_format, 'csv')
        self.assertEqual(handler.file_obj, self.csv_data)
        
        # Excel format
        handler = BulkImportHandler('materials', self.excel_data, 'xlsx')
        self.assertEqual(handler.file_format, 'xlsx')
        
    def test_init_with_invalid_format(self):
        """Test initialization with invalid format"""
        with self.assertRaises(ValueError) as context:
            BulkImportHandler('materials', self.csv_data, 'pdf')
        
        self.assertIn('Unsupported file format', str(context.exception))
        self.assertIn('csv', str(context.exception))
        self.assertIn('xlsx', str(context.exception))
        self.assertIn('xls', str(context.exception))
        
    def test_get_supported_formats(self):
        """Test getting supported formats"""
        formats = BulkImportHandler.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertIn('csv', formats)
        self.assertIn('xlsx', formats)
        self.assertIn('xls', formats)
        
    def test_get_max_file_size(self):
        """Test getting max file size"""
        max_size = BulkImportHandler.get_max_file_size()
        self.assertEqual(max_size, 10 * 1024 * 1024)  # 10MB
        
    def test_parse_csv_file(self):
        """Test parsing CSV file"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        result = handler.parse_file()
        
        self.assertTrue(result)
        self.assertIsNotNone(handler.df)
        self.assertEqual(len(handler.df), 2)
        self.assertIn('name', handler.df.columns)
        self.assertIn('description', handler.df.columns)
        self.assertIn('unit_price', handler.df.columns)
        
    def test_parse_excel_file(self):
        """Test parsing Excel file"""
        handler = BulkImportHandler('materials', self.excel_data, 'xlsx')
        result = handler.parse_file()
        
        self.assertTrue(result)
        self.assertIsNotNone(handler.df)
        self.assertEqual(len(handler.df), 2)
        self.assertIn('name', handler.df.columns)
        self.assertIn('description', handler.df.columns)
        self.assertIn('unit_price', handler.df.columns)
        
    def test_parse_malformed_file(self):
        """Test parsing malformed file"""
        handler = BulkImportHandler('materials', self.malformed_csv_data, 'csv')
        result = handler.parse_file()
        
        # Should still parse but with errors
        self.assertTrue(result)
        self.assertIsNotNone(handler.df)
        self.assertEqual(len(handler.df), 1)  # One row
        
    def test_validate_valid_data(self):
        """Test validation of valid data"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.parse_file()
        
        with patch.object(BulkImportValidator, 'validate', return_value=True):
            result = handler.validate()
            self.assertTrue(result)
            self.assertEqual(len(handler.errors), 0)
        
    def test_validate_invalid_data(self):
        """Test validation of invalid data"""
        handler = BulkImportHandler('materials', self.invalid_csv_data, 'csv')
        handler.parse_file()
        
        # Mock validator to return errors
        mock_validator = MagicMock()
        mock_validator.validate.return_value = False
        mock_validator.errors = [
            {'row': 2, 'field': 'name', 'error': 'This field is required'}
        ]
        
        with patch('bulk_operations.services.import_handler.BulkImportValidator', return_value=mock_validator):
            result = handler.validate()
            self.assertFalse(result)
            self.assertEqual(len(handler.errors), 1)
            self.assertEqual(handler.errors[0]['field'], 'name')
            
    def test_validate_without_parsing(self):
        """Test validation automatically triggers parsing"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        
        with patch.object(BulkImportValidator, 'validate', return_value=True):
            result = handler.validate()
            self.assertTrue(result)
            self.assertIsNotNone(handler.df)
            
    def test_import_data_successful(self):
        """Test successful data import"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.parse_file()
        handler.validator = BulkImportValidator('materials', handler.df)
        
        # Mock serializer
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.save.return_value = Material(name="Test Material")
        
        with patch('bulk_operations.serializers.BulkSerializerFactory.get_serializer', 
                   return_value=lambda data: mock_serializer):
            success_count, failed_count = handler.import_data()
            
            self.assertEqual(success_count, 2)
            self.assertEqual(failed_count, 0)
            self.assertEqual(len(handler.imported_records), 2)
            self.assertEqual(len(handler.errors), 0)
            
    def test_import_data_with_errors(self):
        """Test data import with serializer errors"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.parse_file()
        handler.validator = BulkImportValidator('materials', handler.df)
        
        # First row succeeds, second row fails
        mock_serializer_success = MagicMock()
        mock_serializer_success.is_valid.return_value = True
        mock_serializer_success.save.return_value = Material(name="Test Material")
        
        mock_serializer_fail = MagicMock()
        mock_serializer_fail.is_valid.return_value = False
        mock_serializer_fail.errors = {'unit_price': ['Enter a number.']}
        
        serializers = [mock_serializer_success, mock_serializer_fail]
        
        with patch('bulk_operations.serializers.BulkSerializerFactory.get_serializer', 
                   return_value=lambda data: serializers.pop(0)):
            success_count, failed_count = handler.import_data()
            
            self.assertEqual(success_count, 1)
            self.assertEqual(failed_count, 1)
            self.assertEqual(len(handler.imported_records), 1)
            self.assertEqual(len(handler.errors), 1)
            self.assertEqual(handler.errors[0]['field'], 'unit_price')
            
    def test_import_data_without_validation(self):
        """Test import_data requires validation first"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        
        with self.assertRaises(ValueError) as context:
            handler.import_data()
            
        self.assertIn('must be validated', str(context.exception))
        
    def test_import_data_with_validation_errors(self):
        """Test import_data with validation errors"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.parse_file()
        handler.validator = BulkImportValidator('materials', handler.df)
        handler.errors = [{'row': 2, 'field': 'name', 'error': 'This field is required'}]
        
        with self.assertRaises(ValueError) as context:
            handler.import_data()
            
        self.assertIn('with validation errors', str(context.exception))
        
    def test_get_import_summary(self):
        """Test getting import summary"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.parse_file()
        handler.imported_records = [MagicMock(), MagicMock()]
        handler.errors = [{'row': 3, 'field': 'unit_price', 'error': 'Invalid value'}]
        
        summary = handler.get_import_summary()
        
        self.assertEqual(summary['template_type'], 'materials')
        self.assertEqual(summary['total_rows'], 2)
        self.assertEqual(summary['successful'], 2)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(len(summary['errors']), 1)
        self.assertFalse(summary['has_more_errors'])
        
    def test_get_import_summary_with_many_errors(self):
        """Test getting import summary with many errors"""
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.parse_file()
        handler.errors = [{'row': i, 'field': 'field', 'error': f'Error {i}'} for i in range(150)]
        
        summary = handler.get_import_summary()
        
        self.assertEqual(len(summary['errors']), 100)  # Limited to 100
        self.assertTrue(summary['has_more_errors'])
        
    @patch('bulk_operations.services.import_handler.BulkImportHandler.parse_file')
    @patch('bulk_operations.services.import_handler.BulkImportHandler.validate')
    @patch('bulk_operations.services.import_handler.BulkImportHandler.import_data')
    def test_process_successful(self, mock_import, mock_validate, mock_parse):
        """Test end-to-end process with successful flow"""
        mock_parse.return_value = True
        mock_validate.return_value = True
        mock_import.return_value = (2, 0)
        
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.df = pd.DataFrame([{}, {}])  # Mock 2 rows
        handler.imported_records = [MagicMock(), MagicMock()]
        
        result = handler.process()
        
        mock_parse.assert_called_once()
        mock_validate.assert_called_once()
        mock_import.assert_called_once()
        
        self.assertEqual(result['successful'], 2)
        self.assertEqual(result['failed'], 0)
        
    @patch('bulk_operations.services.import_handler.BulkImportHandler.parse_file')
    def test_process_parsing_failure(self, mock_parse):
        """Test process with parsing failure"""
        mock_parse.return_value = False
        
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.errors = [{'row': 'N/A', 'field': 'N/A', 'error': 'Parsing error'}]
        
        result = handler.process()
        
        mock_parse.assert_called_once()
        
        self.assertEqual(result['successful'], 0)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(len(result['errors']), 1)
        
    @patch('bulk_operations.services.import_handler.BulkImportHandler.parse_file')
    @patch('bulk_operations.services.import_handler.BulkImportHandler.validate')
    def test_process_validation_failure(self, mock_validate, mock_parse):
        """Test process with validation failure"""
        mock_parse.return_value = True
        mock_validate.return_value = False
        
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.df = pd.DataFrame([{}, {}])  # Mock 2 rows
        handler.errors = [{'row': 2, 'field': 'name', 'error': 'Required field'}]
        
        result = handler.process()
        
        mock_parse.assert_called_once()
        mock_validate.assert_called_once()
        
        self.assertEqual(result['successful'], 0)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(len(result['errors']), 1)
        
    @patch('bulk_operations.services.import_handler.BulkImportHandler.parse_file')
    @patch('bulk_operations.services.import_handler.BulkImportHandler.validate')
    @patch('bulk_operations.services.import_handler.BulkImportHandler.import_data')
    def test_process_import_exception(self, mock_import, mock_validate, mock_parse):
        """Test process with import exception"""
        mock_parse.return_value = True
        mock_validate.return_value = True
        mock_import.side_effect = Exception("Import failed")
        
        handler = BulkImportHandler('materials', self.csv_data, 'csv')
        handler.df = pd.DataFrame([{}, {}])  # Mock 2 rows
        
        result = handler.process()
        
        mock_parse.assert_called_once()
        mock_validate.assert_called_once()
        mock_import.assert_called_once()
        
        self.assertEqual(result['successful'], 0)
        self.assertEqual(result['failed'], 2)
        self.assertEqual(len(result['errors']), 1)
        self.assertIn('Import process error', result['errors'][0]['error'])
    
    def test_real_import_integration(self):
        """Integration test with real Material model"""
        # Use transaction.atomic to roll back test data
        with transaction.atomic():
            handler = BulkImportHandler('materials', self.csv_data, 'csv')
            
            # Patch serializer factory to return actual MaterialBulkSerializer
            with patch('bulk_operations.services.import_handler.BulkSerializerFactory.get_serializer', 
                      return_value=MaterialBulkSerializer):
                
                # Process import
                result = handler.process()
                
                # Check results
                self.assertEqual(result['successful'], 2)
                self.assertEqual(result['failed'], 0)
                
                # Verify material was created in the database
                materials = Material.objects.all()
                self.assertEqual(materials.count(), 2)
                
                # Check first material
                material = Material.objects.get(name="Test Material")
                self.assertEqual(material.description, "A material for testing")
                self.assertEqual(float(material.unit_price), 25.99)
                
                # Check second material
                material = Material.objects.get(name="Second Material")
                self.assertEqual(material.description, "Another test material")
                self.assertEqual(float(material.unit_price), 15.50)
                
                # Force rollback by raising an exception
                raise Exception("Rolling back test transaction")