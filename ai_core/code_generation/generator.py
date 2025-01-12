# ai_core/code_generation/generator.py
from pathlib import Path
from django.template.loader import render_to_string
from ..models import CodePattern
from ..components import BaseComponent


class CodeGenerator(BaseComponent):
    def __init__(self, config):
        super().__init__(config)
        self.patterns = {}

    def _setup(self):
        """Load code patterns from database"""
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> dict:
        """Load and cache code patterns"""
        patterns = {}
        for pattern in CodePattern.objects.all():
            if pattern.pattern_type not in patterns:
                patterns[pattern.pattern_type] = []
            patterns[pattern.pattern_type].append(pattern.pattern_data)
        return patterns

    def generate_model(self, model_spec: dict) -> str:
        """Generate Django model code"""
        template_context = {
            'model_name': model_spec['name'],
            'fields': self._process_fields(model_spec['fields']),
            'meta_options': model_spec.get('meta', {}),
            'methods': self._generate_methods(model_spec)
        }

        return render_to_string('ai_core/code_templates/model.py.txt', template_context)

    def generate_view(self, view_spec: dict) -> str:
        """Generate Django view code"""
        template_context = {
            'view_name': view_spec['name'],
            'base_class': view_spec['type'],
            'model': view_spec.get('model'),
            'methods': view_spec.get('methods', []),
            'mixins': view_spec.get('mixins', [])
        }

        return render_to_string('ai_core/code_templates/view.py.txt', template_context)

    def _process_fields(self, fields: list) -> list:
        """Process and validate model field specifications"""
        processed_fields = []
        for field in fields:
            field_pattern = self._find_matching_pattern('model_field', field)
            if field_pattern:
                field['template'] = field_pattern['template']
            processed_fields.append(field)
        return processed_fields

    def _find_matching_pattern(self, pattern_type: str, data: dict) -> dict:
        """Find matching code pattern from learned patterns"""
        if pattern_type not in self.patterns:
            return None

        for pattern in self.patterns[pattern_type]:
            if self._pattern_matches(pattern, data):
                return pattern
        return None

    def _pattern_matches(self, pattern: dict, data: dict) -> bool:
        """Check if a pattern matches the given data"""
        # Basic pattern matching logic - can be enhanced
        return all(
            key in data and data[key] == value
            for key, value in pattern.items()
            if key != 'template'
        )

    def _generate_methods(self, model_spec: dict) -> list:
        """Generate model methods based on specifications"""
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