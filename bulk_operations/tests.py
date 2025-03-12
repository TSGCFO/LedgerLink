from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import io
import json
import csv

from .services.template_generator import CSVTemplateGenerator
from .services.validators import BulkImportValidator
from .serializers import (
    BulkSerializerFactory, 
    CustomerBulkSerializer, 
    OrderBulkSerializer,
    MaterialBulkSerializer
)
from customers.models import Customer


class TemplateGeneratorTests(TestCase):
    """Test cases for the CSVTemplateGenerator class"""

    def test_get_available_templates(self):
        """Test that all available templates are returned"""
        templates = CSVTemplateGenerator.get_available_templates()
        
        # Check that we have at least the expected templates
        template_types = [t['type'] for t in templates]
        expected_types = [
            'customers', 'orders', 'products', 'services', 
            'materials', 'inserts', 'cad_shipping', 'us_shipping'
        ]
        
        for template_type in expected_types:
            self.assertIn(template_type, template_types)
            
        # Check that each template has the expected fields
        for template in templates:
            self.assertIn('type', template)
            self.assertIn('name', template)
            self.assertIn('description', template)
            self.assertIn('fieldCount', template)
            
    def test_get_template_definition(self):
        """Test getting a specific template definition"""
        # Test for customers template
        definition = CSVTemplateGenerator.get_template_definition('customers')
        
        # Should have fields and required_fields
        self.assertIn('fields', definition)
        self.assertIn('required_fields', definition)
        
        # Required fields should be a subset of all fields
        for field in definition['required_fields']:
            self.assertIn(field, definition['fields'])
            
        # Test for non-existent template
        with self.assertRaises(KeyError):
            CSVTemplateGenerator.get_template_definition('non_existent_template')
            
    def test_get_field_types(self):
        """Test getting field types for a template"""
        field_types = CSVTemplateGenerator.get_field_types('materials')
        
        # Check specific fields have correct types
        self.assertEqual(field_types['name'], 'string')
        self.assertEqual(field_types['unit_price'], 'decimal')
        
        # Test for non-existent template
        with self.assertRaises(KeyError):
            CSVTemplateGenerator.get_field_types('non_existent_template')
            
    def test_generate_template_header(self):
        """Test generating a template header"""
        header = CSVTemplateGenerator.generate_template_header('customers')
        
        # Header should be a list of strings
        self.assertIsInstance(header, list)
        for field in header:
            self.assertIsInstance(field, str)
            
        # Should include required fields
        self.assertIn('company_name', header)
        self.assertIn('legal_business_name', header)
        self.assertIn('email', header)


class BulkValidatorTests(TestCase):
    """Test cases for the BulkImportValidator class"""
    
    def setUp(self):
        """Set up test data"""
        # Valid customer data
        self.valid_customer_data = pd.DataFrame({
            'company_name': ['Test Company 1', 'Test Company 2'],
            'legal_business_name': ['Legal Name 1', 'Legal Name 2'],
            'email': ['test1@example.com', 'test2@example.com'],
            'phone': ['123-456-7890', '098-765-4321'],
        })
        
        # Invalid customer data (missing required field)
        self.invalid_customer_data = pd.DataFrame({
            'company_name': ['Test Company 1', 'Test Company 2'],
            'legal_business_name': ['Legal Name 1', None],  # Missing required field
            'email': ['test1@example.com', 'test2@example.com'],
        })
        
        # Invalid data types
        self.invalid_types_data = pd.DataFrame({
            'company_name': ['Test Company 1', 'Test Company 2'],
            'legal_business_name': ['Legal Name 1', 'Legal Name 2'],
            'email': ['test1@example.com', 'invalid_email'],  # Invalid email
        })

    def test_validate_required_fields(self):
        """Test validation of required fields"""
        # Valid data should pass validation
        validator = BulkImportValidator('customers', self.valid_customer_data)
        validator._validate_required_fields(['company_name', 'legal_business_name', 'email'])
        self.assertEqual(len(validator.errors), 0)
        
        # Invalid data should fail validation
        validator = BulkImportValidator('customers', self.invalid_customer_data)
        validator._validate_required_fields(['company_name', 'legal_business_name', 'email'])
        self.assertGreaterEqual(len(validator.errors), 1)
        
        # Check that error includes row and field info
        error = validator.errors[0]
        self.assertIn('row', error)
        self.assertIn('field', error)
        self.assertIn('error', error)
        
    def test_validate_data_types(self):
        """Test validation of data types"""
        # Test with integer field
        int_data = pd.DataFrame({
            'id': [1, 'not_an_int']
        })
        validator = BulkImportValidator('customers', int_data)
        validator._validate_data_types({'id': 'integer'})
        self.assertGreaterEqual(len(validator.errors), 1)
        
        # Test with decimal field
        decimal_data = pd.DataFrame({
            'price': [10.99, 'not_a_decimal']
        })
        validator = BulkImportValidator('customers', decimal_data)
        validator._validate_data_types({'price': 'decimal'})
        self.assertGreaterEqual(len(validator.errors), 1)
        
        # Test with date field
        date_data = pd.DataFrame({
            'date': ['2023-01-01', 'not_a_date']
        })
        validator = BulkImportValidator('customers', date_data)
        validator._validate_data_types({'date': 'date'})
        self.assertGreaterEqual(len(validator.errors), 1)


class BulkSerializerTests(TestCase):
    """Test cases for the Bulk Serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
    
    def test_customer_bulk_serializer(self):
        """Test the CustomerBulkSerializer"""
        data = {
            'company_name': 'Bulk Test Company',
            'legal_business_name': 'Bulk Legal Name',
            'email': 'bulk@example.com',
            'phone': '555-555-5555',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip': '12345',
            'country': 'Test Country',
        }
        
        serializer = CustomerBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Test with missing required field
        invalid_data = data.copy()
        del invalid_data['company_name']
        serializer = CustomerBulkSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)
        
        # Test with invalid email
        invalid_data = data.copy()
        invalid_data['email'] = 'not_an_email'
        serializer = CustomerBulkSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        
    def test_material_bulk_serializer(self):
        """Test the MaterialBulkSerializer"""
        data = {
            'name': 'Bulk Test Material',
            'description': 'A test material',
            'unit_price': '10.99',
        }
        
        serializer = MaterialBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Test with missing required field
        invalid_data = data.copy()
        del invalid_data['name']
        serializer = MaterialBulkSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        
        # Test with invalid price
        invalid_data = data.copy()
        invalid_data['unit_price'] = 'not_a_price'
        serializer = MaterialBulkSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('unit_price', serializer.errors)
        
    def test_order_bulk_serializer(self):
        """Test the OrderBulkSerializer"""
        data = {
            'transaction_id': 12345,
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'ship_to_name': 'Recipient Name',
            'ship_to_address': '123 Delivery St',
            'ship_to_city': 'Delivery City',
            'ship_to_state': 'DS',
            'ship_to_zip': '54321',
            'status': 'draft',
            'priority': 'medium',
        }
        
        serializer = OrderBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Test foreign key validation
        invalid_data = data.copy()
        invalid_data['customer'] = 999999  # Non-existent customer
        serializer = OrderBulkSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer', serializer.errors)
        
        # Test choice field validation
        invalid_data = data.copy()
        invalid_data['status'] = 'invalid_status'
        serializer = OrderBulkSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        
    def test_bulk_serializer_factory(self):
        """Test the BulkSerializerFactory"""
        # Test getting valid serializers
        self.assertEqual(BulkSerializerFactory.get_serializer('customers'), CustomerBulkSerializer)
        self.assertEqual(BulkSerializerFactory.get_serializer('orders'), OrderBulkSerializer)
        self.assertEqual(BulkSerializerFactory.get_serializer('materials'), MaterialBulkSerializer)
        
        # Test getting invalid serializer
        with self.assertRaises(KeyError):
            BulkSerializerFactory.get_serializer('non_existent_template')


class BulkOperationsAPITests(APITestCase):
    """Test cases for the Bulk Operations API endpoints"""
    
    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.template_list_url = reverse('bulkoperation-list')
        self.template_info_url = reverse('bulkoperation-template-info', kwargs={'template_type': 'materials'})
        self.invalid_template_info_url = reverse('bulkoperation-template-info', kwargs={'template_type': 'invalid'})
        self.download_url = reverse('template-download', kwargs={'template_type': 'materials'})
        self.invalid_download_url = reverse('template-download', kwargs={'template_type': 'invalid'})
        self.import_url = reverse('bulk-import', kwargs={'template_type': 'materials'})
        
        # Create CSV test file
        self.csv_data = io.StringIO()
        writer = csv.writer(self.csv_data)
        writer.writerow(['name', 'description', 'unit_price'])
        writer.writerow(['Test Material', 'Material for testing', '15.99'])
        writer.writerow(['Another Material', 'Another test item', '24.50'])
        self.csv_file = SimpleUploadedFile(
            'materials.csv', 
            self.csv_data.getvalue().encode(), 
            content_type='text/csv'
        )
        
        # Create invalid CSV test file (missing required field)
        self.invalid_csv_data = io.StringIO()
        writer = csv.writer(self.invalid_csv_data)
        writer.writerow(['description', 'unit_price'])  # Missing 'name'
        writer.writerow(['Material for testing', '15.99'])
        self.invalid_csv_file = SimpleUploadedFile(
            'invalid_materials.csv', 
            self.invalid_csv_data.getvalue().encode(), 
            content_type='text/csv'
        )
        
    def test_list_templates(self):
        """Test the template listing endpoint"""
        response = self.client.get(self.template_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should contain templates and supported formats
        self.assertIn('templates', response.data['data'])
        self.assertIn('supportedFormats', response.data['data'])
        self.assertIn('maxFileSize', response.data['data'])
        
        # Should include at least 'materials' template
        templates = [t['type'] for t in response.data['data']['templates']]
        self.assertIn('materials', templates)
        
    def test_template_info(self):
        """Test the template info endpoint"""
        # Test valid template
        response = self.client.get(self.template_info_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should include fields, required fields, and field types
        self.assertIn('fields', response.data['data'])
        self.assertIn('requiredFields', response.data['data'])
        self.assertIn('fieldTypes', response.data['data'])
        
        # Should have correct template type
        self.assertEqual(response.data['data']['templateType'], 'materials')
        
        # Test invalid template
        response = self.client.get(self.invalid_template_info_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        
    def test_download_template(self):
        """Test the template download endpoint"""
        # Test valid template
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # CSV content should include header with expected fields
        content = response.content.decode('utf-8')
        self.assertIn('name', content)
        self.assertIn('description', content)
        self.assertIn('unit_price', content)
        
        # Test invalid template
        response = self.client.get(self.invalid_download_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_import_validation(self):
        """Test validation during import"""
        # Test import with no file
        response = self.client.post(self.import_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('No file provided', response.data['error'])
        
        # Test import with invalid file format
        invalid_file = SimpleUploadedFile(
            'materials.txt', 
            b'This is not a CSV file', 
            content_type='text/plain'
        )
        response = self.client.post(self.import_url, {'file': invalid_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Unsupported file format', response.data['error'])
        
        # Test import with invalid CSV content
        response = self.client.post(self.import_url, {'file': self.invalid_csv_file})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should indicate import errors
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
        
    def test_successful_import(self):
        """Test successful file import"""
        # Import valid CSV file
        response = self.client.post(self.import_url, {'file': self.csv_file})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should indicate success
        self.assertTrue(response.data['success'])
        self.assertIn('import_summary', response.data)
        self.assertEqual(response.data['import_summary']['successful'], 2)
        self.assertEqual(response.data['import_summary']['failed'], 0)
        
        # Records should be created in the database
        from materials.models import Material
        materials = Material.objects.all()
        self.assertEqual(materials.count(), 2)
        
        # Verify data was correctly imported
        material_names = [m.name for m in materials]
        self.assertIn('Test Material', material_names)
        self.assertIn('Another Material', material_names)
        
        # Verify unit prices were correctly imported
        material = Material.objects.get(name='Test Material')
        self.assertEqual(float(material.unit_price), 15.99)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to the API"""
        self.client.logout()
        
        response = self.client.get(self.template_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(self.template_info_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(self.import_url, {'file': self.csv_file})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_file_size_limit(self):
        """Test file size limit enforcement"""
        # Create a file larger than the limit (10MB)
        large_data = 'a' * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            'large_file.csv', 
            large_data.encode(), 
            content_type='text/csv'
        )
        
        response = self.client.post(self.import_url, {'file': large_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('size exceeds', response.data['error'])
