"""
Unit tests for the CSVTemplateGenerator.
"""

import pytest

from bulk_operations.services.template_generator import CSVTemplateGenerator


class TestCSVTemplateGenerator:
    """Tests for the CSVTemplateGenerator service."""

    def test_get_available_templates(self):
        """Test retrieving available templates."""
        templates = CSVTemplateGenerator.get_available_templates()
        
        # Check that templates list is not empty
        assert len(templates) > 0
        
        # Verify structure of template objects
        for template in templates:
            assert 'type' in template
            assert 'name' in template
            assert 'description' in template
            assert 'fieldCount' in template
            
        # Check that specific template types exist
        template_types = [t['type'] for t in templates]
        assert 'customers' in template_types
        assert 'orders' in template_types
        assert 'products' in template_types

    def test_get_template_definition_customers(self):
        """Test getting template definition for customers."""
        definition = CSVTemplateGenerator.get_template_definition('customers')
        
        assert 'fields' in definition
        assert 'required_fields' in definition
        
        # Check that specific fields exist
        assert 'company_name' in definition['fields']
        assert 'email' in definition['fields']
        
        # Check that required fields are correctly identified
        assert 'company_name' in definition['required_fields']
        assert 'email' in definition['required_fields']

    def test_get_template_definition_orders(self):
        """Test getting template definition for orders."""
        definition = CSVTemplateGenerator.get_template_definition('orders')
        
        assert 'fields' in definition
        assert 'required_fields' in definition
        
        # Check that specific fields exist
        assert 'transaction_id' in definition['fields']
        assert 'customer' in definition['fields']
        assert 'ship_to_name' in definition['fields']
        
        # Check that required fields are correctly identified
        assert 'transaction_id' in definition['required_fields']
        assert 'customer' in definition['required_fields']

    def test_get_template_definition_invalid(self):
        """Test getting template definition for invalid template type."""
        with pytest.raises(KeyError) as excinfo:
            CSVTemplateGenerator.get_template_definition('nonexistent')
        
        # Check the error message
        assert "Template type 'nonexistent' not found" in str(excinfo.value)

    def test_get_field_types_customers(self):
        """Test getting field types for customers."""
        field_types = CSVTemplateGenerator.get_field_types('customers')
        
        # Check that it returns a dictionary
        assert isinstance(field_types, dict)
        
        # Check specific field types
        assert field_types['company_name'] == 'string'
        assert field_types['email'] == 'string'

    def test_get_field_types_orders(self):
        """Test getting field types for orders."""
        field_types = CSVTemplateGenerator.get_field_types('orders')
        
        # Check that it returns a dictionary
        assert isinstance(field_types, dict)
        
        # Check specific field types
        assert field_types['transaction_id'] == 'integer'
        assert field_types['customer'] == 'integer'
        assert field_types['close_date'] == 'datetime'
        assert field_types['status'] == 'choice'

    def test_get_field_types_invalid(self):
        """Test getting field types for invalid template type."""
        with pytest.raises(KeyError) as excinfo:
            CSVTemplateGenerator.get_field_types('nonexistent')
        
        # Check the error message
        assert "Template type 'nonexistent' not found" in str(excinfo.value)

    def test_generate_template_header_customers(self):
        """Test generating template header for customers."""
        header = CSVTemplateGenerator.generate_template_header('customers')
        
        # Check that it returns a list
        assert isinstance(header, list)
        
        # Check that specific fields are in the header
        assert 'company_name' in header
        assert 'email' in header

    def test_generate_template_header_orders(self):
        """Test generating template header for orders."""
        header = CSVTemplateGenerator.generate_template_header('orders')
        
        # Check that it returns a list
        assert isinstance(header, list)
        
        # Check that specific fields are in the header
        assert 'transaction_id' in header
        assert 'customer' in header
        assert 'ship_to_name' in header

    def test_generate_template_header_invalid(self):
        """Test generating template header for invalid template type."""
        with pytest.raises(KeyError) as excinfo:
            CSVTemplateGenerator.generate_template_header('nonexistent')
        
        # Check the error message
        assert "Template type 'nonexistent' not found" in str(excinfo.value)

    def test_field_definitions_consistency(self):
        """Test that field definitions are consistent between methods."""
        for template_type in ['customers', 'orders', 'products', 'services', 'materials', 'inserts', 'cad_shipping', 'us_shipping']:
            definition = CSVTemplateGenerator.get_template_definition(template_type)
            field_types = CSVTemplateGenerator.get_field_types(template_type)
            header = CSVTemplateGenerator.generate_template_header(template_type)
            
            # All methods should return consistent field sets
            assert set(definition['fields']) == set(field_types.keys())
            assert set(definition['fields']) == set(header)
            
            # Required fields should be a subset of all fields
            assert set(definition['required_fields']).issubset(set(definition['fields']))