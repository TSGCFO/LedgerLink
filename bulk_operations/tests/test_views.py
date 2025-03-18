from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
import json
import pandas as pd
import io
import csv

User = get_user_model()


class BulkOperationViewSetTest(APITestCase):
    """Test suite for the BulkOperationViewSet."""

    def setUp(self):
        """Set up test data."""
        # Create a test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs
        self.list_url = reverse('bulk-operations-list')
        self.template_info_url = reverse('bulk-operations-template-info', kwargs={'template_type': 'materials'})

    def test_list_templates(self):
        """Test listing available templates."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('templates', response.data['data'])
        self.assertIn('supportedFormats', response.data['data'])
        self.assertIn('maxFileSize', response.data['data'])
        
        # Check that we have the expected template types
        template_types = [t['type'] for t in response.data['data']['templates']]
        expected_types = [
            'customers', 'orders', 'products', 'services',
            'materials', 'inserts', 'cad_shipping', 'us_shipping'
        ]
        self.assertEqual(set(template_types), set(expected_types))

    def test_template_info(self):
        """Test getting detailed template information."""
        response = self.client.get(self.template_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['templateType'], 'materials')
        self.assertIn('fields', response.data['data'])
        self.assertIn('requiredFields', response.data['data'])
        self.assertIn('fieldTypes', response.data['data'])
        
        # Check required fields
        required_fields = response.data['data']['requiredFields']
        self.assertIn('name', required_fields)
        self.assertIn('unit_price', required_fields)
        
        # Check field types
        field_types = response.data['data']['fieldTypes']
        self.assertEqual(field_types['name'], 'string')
        self.assertEqual(field_types['unit_price'], 'decimal')

    def test_template_info_invalid(self):
        """Test getting template info for an invalid template type."""
        url = reverse('bulk-operations-template-info', kwargs={'template_type': 'nonexistent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)


class TemplateDownloadViewTest(APITestCase):
    """Test suite for the TemplateDownloadView."""

    def setUp(self):
        """Set up test data."""
        # Create a test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL
        self.materials_template_url = reverse('template-download', kwargs={'template_type': 'materials'})
        self.customers_template_url = reverse('template-download', kwargs={'template_type': 'customers'})

    def test_download_materials_template(self):
        """Test downloading a materials template."""
        response = self.client.get(self.materials_template_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="materials_template.csv"'
        )
        
        # Parse the CSV content
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        header = next(csv_reader)
        
        # Check that the header contains the expected fields
        expected_fields = ['name', 'description', 'unit_price']
        self.assertEqual(set(header), set(expected_fields))

    def test_download_customers_template(self):
        """Test downloading a customers template."""
        response = self.client.get(self.customers_template_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Parse the CSV content
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        header = next(csv_reader)
        
        # Check that the header contains required fields
        self.assertIn('company_name', header)
        self.assertIn('legal_business_name', header)
        self.assertIn('email', header)

    def test_download_invalid_template(self):
        """Test downloading an invalid template."""
        url = reverse('template-download', kwargs={'template_type': 'nonexistent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)


class BulkImportViewTest(APITestCase):
    """Test suite for the BulkImportView."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL
        self.materials_import_url = reverse('bulk-import', kwargs={'template_type': 'materials'})
        
        # Create test CSV file for materials
        self.materials_csv = self._create_materials_csv()

    def _create_materials_csv(self):
        """Create a test CSV file for materials."""
        csv_data = 'name,description,unit_price\n'
        csv_data += 'Test Material 1,Test Description 1,10.50\n'
        csv_data += 'Test Material 2,Test Description 2,15.75\n'
        
        return SimpleUploadedFile(
            'materials.csv',
            csv_data.encode('utf-8'),
            content_type='text/csv'
        )

    def test_import_no_file(self):
        """Test import with no file provided."""
        response = self.client.post(self.materials_import_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'No file provided')

    def test_import_with_file(self):
        """Test import with a valid CSV file."""
        response = self.client.post(
            self.materials_import_url,
            {'file': self.materials_csv},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertIn('message', response.data)
        self.assertIn('import_summary', response.data)
        
        # Check the import summary
        summary = response.data['import_summary']
        self.assertEqual(summary['total_rows'], 2)
        
        # Note: The actual success/failure of records would depend on the database state
        # and constraints, which are difficult to fully mock in this test environment.
        # A full integration test would be needed to verify the actual import process.