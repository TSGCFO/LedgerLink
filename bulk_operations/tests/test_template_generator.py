from django.test import TestCase
from bulk_operations.services.template_generator import CSVTemplateGenerator


class CSVTemplateGeneratorTest(TestCase):
    """Test suite for the CSVTemplateGenerator service."""

    def test_get_available_templates(self):
        """Test getting the list of available templates."""
        templates = CSVTemplateGenerator.get_available_templates()
        
        # Check that we have the expected number of templates
        self.assertEqual(len(templates), 8)
        
        # Check that the expected template types are present
        template_types = [t['type'] for t in templates]
        expected_types = [
            'customers', 'orders', 'products', 'services',
            'materials', 'inserts', 'cad_shipping', 'us_shipping'
        ]
        self.assertEqual(set(template_types), set(expected_types))
        
        # Check that each template has the required metadata
        for template in templates:
            self.assertIn('name', template)
            self.assertIn('description', template)
            self.assertIn('fieldCount', template)
            self.assertIsInstance(template['fieldCount'], int)
            self.assertGreater(template['fieldCount'], 0)

    def test_get_template_definition_valid(self):
        """Test getting template definition for valid template types."""
        # Test 'customers' template
        definition = CSVTemplateGenerator.get_template_definition('customers')
        self.assertIn('fields', definition)
        self.assertIn('required_fields', definition)
        self.assertIsInstance(definition['fields'], list)
        self.assertIsInstance(definition['required_fields'], list)
        
        # Check that required fields are a subset of all fields
        self.assertTrue(all(field in definition['fields'] for field in definition['required_fields']))
        
        # Check required fields for customers template
        required_fields = definition['required_fields']
        self.assertIn('company_name', required_fields)
        self.assertIn('legal_business_name', required_fields)
        self.assertIn('email', required_fields)
        
        # Test 'materials' template
        definition = CSVTemplateGenerator.get_template_definition('materials')
        required_fields = definition['required_fields']
        self.assertIn('name', required_fields)
        self.assertIn('unit_price', required_fields)

    def test_get_template_definition_invalid(self):
        """Test getting template definition for invalid template types."""
        with self.assertRaises(KeyError):
            CSVTemplateGenerator.get_template_definition('nonexistent_template')

    def test_get_field_types(self):
        """Test getting field types for templates."""
        # Test 'customers' template
        field_types = CSVTemplateGenerator.get_field_types('customers')
        self.assertIsInstance(field_types, dict)
        self.assertEqual(field_types['company_name'], 'string')
        self.assertEqual(field_types['email'], 'string')
        
        # Test 'materials' template
        field_types = CSVTemplateGenerator.get_field_types('materials')
        self.assertEqual(field_types['name'], 'string')
        self.assertEqual(field_types['unit_price'], 'decimal')
        
        # Test 'orders' template which has complex types
        field_types = CSVTemplateGenerator.get_field_types('orders')
        self.assertEqual(field_types['transaction_id'], 'integer')
        self.assertEqual(field_types['close_date'], 'datetime')
        self.assertEqual(field_types['sku_quantity'], 'json')
        self.assertEqual(field_types['status'], 'choice')

    def test_generate_template_header(self):
        """Test generating template headers."""
        # Test 'customers' template
        header = CSVTemplateGenerator.generate_template_header('customers')
        self.assertIsInstance(header, list)
        self.assertIn('company_name', header)
        self.assertIn('legal_business_name', header)
        self.assertIn('email', header)
        
        # Test 'materials' template
        header = CSVTemplateGenerator.generate_template_header('materials')
        self.assertEqual(set(header), set(['name', 'description', 'unit_price']))
        
        # Check invalid template
        with self.assertRaises(KeyError):
            CSVTemplateGenerator.generate_template_header('nonexistent_template')

    def test_template_field_consistency(self):
        """Test that fields are consistent across methods."""
        for template_type in ['customers', 'orders', 'materials', 'inserts']:
            # Get fields via various methods
            definition = CSVTemplateGenerator.get_template_definition(template_type)
            field_types = CSVTemplateGenerator.get_field_types(template_type)
            header = CSVTemplateGenerator.generate_template_header(template_type)
            
            # Check that all methods return the same fields
            self.assertEqual(set(definition['fields']), set(field_types.keys()))
            self.assertEqual(set(definition['fields']), set(header))