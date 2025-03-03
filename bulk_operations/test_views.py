"""
Unit tests for Bulk Operations views.
"""

import io
import csv
import json
import pytest
from django.urls import reverse
from rest_framework import status
import pandas as pd
from unittest.mock import patch, MagicMock

from test_utils.mixins import APITestMixin
from .services.template_generator import CSVTemplateGenerator

pytestmark = pytest.mark.django_db


class TestBulkOperationViewSet(APITestMixin):
    """Tests for the BulkOperationViewSet."""

    def setUp(self):
        super().setUp()
        self.list_url = reverse('bulk-operations-list')
        self.template_info_url = reverse('bulk-operations-template-info', kwargs={'template_type': 'customer'})
        
        # Mock template definitions
        self.mocked_templates = [
            {'name': 'customer', 'description': 'Customer import template'},
            {'name': 'product', 'description': 'Product import template'}
        ]
        
        self.mocked_template_def = {
            'fields': ['company_name', 'contact_email', 'contact_phone'],
            'required_fields': ['company_name', 'contact_email']
        }
        
        self.mocked_field_types = {
            'company_name': 'string',
            'contact_email': 'email',
            'contact_phone': 'string'
        }

    @patch('bulk_operations.views.CSVTemplateGenerator')
    def test_list_templates(self, mock_generator):
        """Test retrieving a list of available templates."""
        # Setup mock
        mock_generator.get_available_templates.return_value = self.mocked_templates
        
        # Make request
        response = self.get_json_response(self.list_url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']['templates']) == 2
        assert response['data']['supportedFormats'] == ['csv', 'xlsx']
        assert response['data']['maxFileSize'] == 10 * 1024 * 1024  # 10MB
        
        # Verify mock was called
        mock_generator.get_available_templates.assert_called_once()

    @patch('bulk_operations.views.CSVTemplateGenerator')
    def test_template_info(self, mock_generator):
        """Test retrieving detailed information about a specific template."""
        # Setup mocks
        mock_generator.get_template_definition.return_value = self.mocked_template_def
        mock_generator.get_field_types.return_value = self.mocked_field_types
        
        # Make request
        response = self.get_json_response(self.template_info_url)
        
        # Check response
        assert response['success'] is True
        assert response['data']['templateType'] == 'customer'
        assert response['data']['fields'] == self.mocked_template_def['fields']
        assert response['data']['requiredFields'] == self.mocked_template_def['required_fields']
        assert response['data']['fieldTypes'] == self.mocked_field_types
        
        # Verify mocks were called
        mock_generator.get_template_definition.assert_called_once_with('customer')
        mock_generator.get_field_types.assert_called_once_with('customer')

    @patch('bulk_operations.views.CSVTemplateGenerator')
    def test_template_info_not_found(self, mock_generator):
        """Test retrieving information for a non-existent template."""
        # Setup mock to raise KeyError
        mock_generator.get_template_definition.side_effect = KeyError('Template not found')
        
        # Make request
        invalid_url = reverse('bulk-operations-template-info', kwargs={'template_type': 'nonexistent'})
        response = self.get_json_response(invalid_url, status_code=status.HTTP_404_NOT_FOUND)
        
        # Check response
        assert response['success'] is False
        assert 'not found' in response['error']


class TestTemplateDownloadView(APITestMixin):
    """Tests for the TemplateDownloadView."""

    def setUp(self):
        super().setUp()
        self.download_url = reverse('template-download', kwargs={'template_type': 'customer'})
        
        # Mock template headers
        self.mocked_headers = ['company_name', 'contact_email', 'contact_phone']

    @patch('bulk_operations.views.CSVTemplateGenerator')
    def test_template_download(self, mock_generator):
        """Test downloading a template CSV file."""
        # Setup mock
        mock_generator.generate_template_header.return_value = self.mocked_headers
        
        # Make request
        response = self.client.get(self.download_url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert response['Content-Disposition'] == 'attachment; filename="customer_template.csv"'
        
        # Parse CSV content
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        
        assert headers == self.mocked_headers
        
        # Verify mock was called
        mock_generator.generate_template_header.assert_called_once_with('customer')

    @patch('bulk_operations.views.CSVTemplateGenerator')
    def test_template_download_not_found(self, mock_generator):
        """Test downloading a non-existent template."""
        # Setup mock to raise KeyError
        mock_generator.generate_template_header.side_effect = KeyError('Template not found')
        
        # Make request
        invalid_url = reverse('template-download', kwargs={'template_type': 'nonexistent'})
        response = self.get_json_response(invalid_url, status_code=status.HTTP_404_NOT_FOUND)
        
        # Check response
        assert response['success'] is False
        assert 'not found' in response['error']


class TestBulkImportView(APITestMixin):
    """Tests for the BulkImportView."""

    def setUp(self):
        super().setUp()
        self.import_url = reverse('bulk-import', kwargs={'template_type': 'customer'})
        
        # Create sample CSV content
        self.csv_header = ['company_name', 'contact_email', 'contact_phone']
        self.csv_data = [
            ['Test Company 1', 'test1@example.com', '123-456-7890'],
            ['Test Company 2', 'test2@example.com', '987-654-3210']
        ]
        
        # Create a CSV file in memory
        self.csv_file = io.StringIO()
        writer = csv.writer(self.csv_file)
        writer.writerow(self.csv_header)
        writer.writerows(self.csv_data)
        self.csv_file.seek(0)
        
        # Mock serializer
        self.mock_serializer = MagicMock()
        self.mock_serializer.is_valid.return_value = True

    @patch('bulk_operations.views.BulkSerializerFactory')
    @patch('bulk_operations.views.pd.read_csv')
    def test_bulk_import_csv(self, mock_read_csv, mock_factory):
        """Test successful CSV import."""
        # Setup mocks
        df = pd.DataFrame(self.csv_data, columns=self.csv_header)
        mock_read_csv.return_value = df
        
        # Mock serializer factory
        mock_factory.get_serializer.return_value = self.mock_serializer
        
        # Create file to upload
        file = io.BytesIO(self.csv_file.getvalue().encode('utf-8'))
        file.name = 'test_import.csv'
        
        # Make request
        response = self.client.post(
            self.import_url,
            {'file': file},
            format='multipart'
        )
        response_data = json.loads(response.content)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response_data['success'] is True
        assert response_data['import_summary']['total_rows'] == 2
        assert response_data['import_summary']['successful'] == 2
        assert response_data['import_summary']['failed'] == 0
        
        # Verify mocks were called
        mock_read_csv.assert_called_once()
        mock_factory.get_serializer.assert_called_once_with('customer')
        assert self.mock_serializer.is_valid.call_count == 2
        assert self.mock_serializer.save.call_count == 2

    def test_bulk_import_no_file(self):
        """Test import with no file provided."""
        # Make request without file
        response = self.client.post(self.import_url, {}, format='multipart')
        response_data = json.loads(response.content)
        
        # Check response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_data['success'] is False
        assert 'No file provided' in response_data['error']

    @patch('bulk_operations.views.pd.read_csv')
    def test_bulk_import_invalid_rows(self, mock_read_csv):
        """Test import with invalid rows."""
        # Setup mocks
        df = pd.DataFrame(self.csv_data, columns=self.csv_header)
        mock_read_csv.return_value = df
        
        # Create invalid serializer
        invalid_serializer = MagicMock()
        invalid_serializer.is_valid.return_value = False
        invalid_serializer.errors = {'company_name': ['This field is required']}
        
        # Mock serializer factory
        with patch('bulk_operations.views.BulkSerializerFactory.get_serializer') as mock_get_serializer:
            mock_get_serializer.return_value = invalid_serializer
            
            # Create file to upload
            file = io.BytesIO(self.csv_file.getvalue().encode('utf-8'))
            file.name = 'test_import.csv'
            
            # Make request
            response = self.client.post(
                self.import_url,
                {'file': file},
                format='multipart'
            )
            response_data = json.loads(response.content)
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            assert response_data['success'] is False
            assert response_data['import_summary']['total_rows'] == 2
            assert response_data['import_summary']['successful'] == 0
            assert response_data['import_summary']['failed'] == 2
            assert len(response_data['errors']) == 2
            
            # Verify mocks were called
            assert invalid_serializer.is_valid.call_count == 2
            assert invalid_serializer.save.call_count == 0