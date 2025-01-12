# ai_core/code_generation/test_generator.py
from typing import Dict, List, Any
from pathlib import Path
from django.template.loader import render_to_string
from ..components import BaseComponent, ComponentConfig


class TestGenerator(BaseComponent):
    """
    Generates test cases for Django components.
    """

    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.test_templates_dir = config.settings.get('test_templates_dir', 'ai_core/templates/ai_core/test_templates')

    def _setup(self):
        """Initialize the test generator"""
        pass

    def generate_model_tests(self, model_spec: Dict[str, Any]) -> str:
        """
        Generates test cases for a Django model.
        Args:
            model_spec: Model specification dictionary
        Returns:
            Generated test code as string
        """
        template_context = {
            'model_name': model_spec['name'],
            'fields': model_spec['fields'],
            'meta_options': model_spec.get('meta', {}),
            'test_cases': self._generate_model_test_cases(model_spec)
        }

        return render_to_string(f'{self.test_templates_dir}/model_test.py.txt', template_context)

    def generate_view_tests(self, view_spec: Dict[str, Any]) -> str:
        """
        Generates test cases for a Django view.
        Args:
            view_spec: View specification dictionary
        Returns:
            Generated test code as string
        """
        template_context = {
            'view_name': view_spec['name'],
            'base_class': view_spec['type'],
            'model': view_spec.get('model'),
            'test_cases': self._generate_view_test_cases(view_spec)
        }

        return render_to_string(f'{self.test_templates_dir}/view_test.py.txt', template_context)

    def _generate_model_test_cases(self, model_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates test cases for model validation and methods.
        Args:
            model_spec: Model specification
        Returns:
            List of test case specifications
        """
        test_cases = []

        # Field validation tests
        for field in model_spec['fields']:
            test_cases.extend(self._generate_field_test_cases(field))

        # Model method tests
        for method in model_spec.get('methods', []):
            test_cases.extend(self._generate_method_test_cases(method))

        return test_cases

    def _generate_view_test_cases(self, view_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates test cases for view functionality.
        Args:
            view_spec: View specification
        Returns:
            List of test case specifications
        """
        test_cases = []

        # Basic view tests
        test_cases.append({
            'name': f'test_{view_spec["name"].lower()}_get',
            'method': 'GET',
            'url': self._get_view_url(view_spec),
            'expected_status': 200
        })

        # View-specific tests based on type
        if view_spec['type'] in ['CreateView', 'UpdateView', 'DeleteView']:
            test_cases.extend(self._generate_form_view_tests(view_spec))

        return test_cases

    def _generate_field_test_cases(self, field: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates test cases for a model field.
        Args:
            field: Field specification
        Returns:
            List of test case specifications
        """
        test_cases = []

        # Required field test
        if field.get('required', False):
            test_cases.append({
                'name': f'test_{field["name"]}_required',
                'type': 'validation',
                'field': field['name'],
                'value': None,
                'should_fail': True
            })

        # Unique field test
        if field.get('unique', False):
            test_cases.append({
                'name': f'test_{field["name"]}_unique',
                'type': 'validation',
                'field': field['name'],
                'duplicate': True,
                'should_fail': True
            })

        return test_cases

    def _generate_method_test_cases(self, method: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates test cases for a model method.
        Args:
            method: Method specification
        Returns:
            List of test case specifications
        """
        return [{
            'name': f'test_{method["name"]}',
            'type': 'method',
            'method_name': method['name'],
            'params': method.get('params', ''),
            'expected_result': None  # To be implemented based on method analysis
        }]

    def _get_view_url(self, view_spec: Dict[str, Any]) -> str:
        """
        Determines the URL pattern for a view.
        Args:
            view_spec: View specification
        Returns:
            URL pattern string
        """
        model_name = view_spec.get('model', '').lower()
        view_type = view_spec['type'].lower().replace('view', '')

        if view_type in ['list', 'create']:
            return f'/{model_name}/'
        else:
            return f'/{model_name}/1/'  # Assumes an object with ID 1 exists

    def _generate_form_view_tests(self, view_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates test cases for form-based views.
        Args:
            view_spec: View specification
        Returns:
            List of test case specifications
        """
        test_cases = []

        if view_spec['type'] == 'CreateView':
            test_cases.extend([
                {
                    'name': f'test_{view_spec["name"].lower()}_post_valid',
                    'method': 'POST',
                    'url': self._get_view_url(view_spec),
                    'data': {},  # To be filled with valid data
                    'expected_status': 302  # Redirect after success
                },
                {
                    'name': f'test_{view_spec["name"].lower()}_post_invalid',
                    'method': 'POST',
                    'url': self._get_view_url(view_spec),
                    'data': {},  # To be filled with invalid data
                    'expected_status': 200  # Form redisplay
                }
            ])

        return test_cases