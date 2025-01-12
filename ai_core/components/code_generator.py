# ai_core/components/code_generator.py
from pathlib import Path
from django.template.loader import render_to_string
from typing import Dict, Any, Optional
from .base import BaseComponent, ComponentConfig
from ..models import CodePattern
from django.db import DatabaseError


class CodeGenerator(BaseComponent):
    """
    Generates Django code based on specifications and learned patterns.
    """

    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.patterns = {}
        self.template_dir = config.settings.get('template_dir', 'ai_core/code_templates')

    def _setup(self) -> None:
        import logging
    
        logger = logging.getLogger(__name__)
    
        try:
            self.patterns = self._load_patterns()
        except DatabaseError as e:
            logger.warning(f"Database tables not ready: {e}. Continuing with empty patterns.")
            self.patterns = {}
    
    def _load_patterns(self) -> Dict[str, list]:
        try:
            patterns = {}
            for pattern in CodePattern.objects.all():
                if pattern.pattern_type not in patterns:
                    patterns[pattern.pattern_type] = []
                patterns[pattern.pattern_type].append(pattern.pattern_data)
            return patterns
        except DatabaseError:
            return {}

    def generate_model(self, model_spec: Dict[str, Any]) -> str:
        """
        Generates Django model code based on specifications.
        Args:
            model_spec: Dictionary containing model specifications
        Returns:
            Generated model code as string
        """
        template_context = {
            'model_name': model_spec['name'],
            'fields': self._process_fields(model_spec.get('fields', [])),
            'meta_options': model_spec.get('meta', {}),
            'methods': self._generate_methods(model_spec)
        }

        return render_to_string(f'{self.template_dir}/model.py.txt', template_context)

    def generate_view(self, view_spec: Dict[str, Any]) -> str:
        """
        Generates Django view code based on specifications.
        Args:
            view_spec: Dictionary containing view specifications
        Returns:
            Generated view code as string
        """
        template_context = {
            'view_name': view_spec['name'],
            'base_class': view_spec['type'],
            'model': view_spec.get('model'),
            'methods': view_spec.get('methods', []),
            'mixins': view_spec.get('mixins', [])
        }

        return render_to_string(f'{self.template_dir}/view.py.txt', template_context)

    def _process_fields(self, fields: list) -> list:
        """
        Processes and validates model field specifications.
        Args:
            fields: List of field specifications
        Returns:
            Processed field specifications
        """
        processed_fields = []
        for field in fields:
            field_pattern = self._find_matching_pattern('model_field', field)
            if field_pattern:
                field['template'] = field_pattern['template']
            processed_fields.append(field)
        return processed_fields

    def _find_matching_pattern(self, pattern_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finds matching code pattern from learned patterns.
        Args:
            pattern_type: Type of pattern to find
            data: Data to match against patterns
        Returns:
            Matching pattern or None
        """
        if pattern_type not in self.patterns:
            return None

        for pattern in self.patterns[pattern_type]:
            if self._pattern_matches(pattern, data):
                return pattern
        return None

    def _pattern_matches(self, pattern: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Check if a pattern matches the given data.
        Args:
            pattern: Pattern to match against
            data: Data to check
        Returns:
            True if pattern matches, False otherwise
        """
        return all(
            key in data and data[key] == value
            for key, value in pattern.items()
            if key != 'template'
        )

    def _generate_methods(self, model_spec: Dict[str, Any]) -> list:
        """
        Generate model methods based on specifications.
        Args:
            model_spec: Model specifications including methods
        Returns:
            List of generated method specifications
        """
        methods = []
        for method_spec in model_spec.get('methods', []):
            method_pattern = self._find_matching_pattern('model_method', method_spec)
            if method_pattern:
                methods.append({
                    'name': method_spec['name'],
                    'params': method_spec.get('params', ''),
                    'body': method_pattern['template'].format(**method_spec)
                })
        return methods