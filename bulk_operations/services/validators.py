# bulk_operations/services/validators.py
from typing import Dict, List, Any
import pandas as pd
from django.core.exceptions import ValidationError
from django.apps import apps


class BulkImportValidator:
    """
    Service for validating bulk import data.
    """

    def __init__(self, template_type: str, data: pd.DataFrame):
        self.template_type = template_type
        self.data = data
        self.errors = []
        self.validated_data = []

    def validate(self) -> bool:
        """
        Validate the imported data against template definition.
        Returns True if validation passes, False otherwise.
        """
        try:
            from .template_generator import CSVTemplateGenerator
            definition = CSVTemplateGenerator.get_template_definition(self.template_type)
            field_types = CSVTemplateGenerator.get_field_types(self.template_type)

            # Validate required fields
            self._validate_required_fields(definition['required_fields'])

            # Validate data types
            self._validate_data_types(field_types)

            # Validate foreign keys
            self._validate_foreign_keys(field_types)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append({
                'row': 'N/A',
                'field': 'N/A',
                'error': f"Validation error: {str(e)}"
            })
            return False

    def _validate_required_fields(self, required_fields: List[str]):
        """
        Validate that all required fields are present and not empty.
        """
        for field in required_fields:
            if field not in self.data.columns:
                self.errors.append({
                    'row': 'N/A',
                    'field': field,
                    'error': f"Required field '{field}' is missing"
                })
            else:
                missing_values = self.data[field].isnull()
                for idx in missing_values[missing_values].index:
                    self.errors.append({
                        'row': idx + 2,  # Add 2 for header row and 1-based indexing
                        'field': field,
                        'error': f"Required field '{field}' is empty"
                    })

    def _validate_data_types(self, field_types: Dict[str, str]):
        """
        Validate data types for each field.
        """
        for field, field_type in field_types.items():
            if field not in self.data.columns:
                continue

            for idx, value in self.data[field].items():
                if pd.isnull(value):
                    continue

                try:
                    if field_type == 'integer':
                        pd.to_numeric(value, downcast='integer')
                    elif field_type == 'decimal':
                        pd.to_numeric(value, downcast='float')
                    elif field_type == 'boolean':
                        pd.to_numeric(value, downcast='boolean')
                    elif field_type in ('date', 'datetime'):
                        pd.to_datetime(value)
                except:
                    self.errors.append({
                        'row': idx + 2,
                        'field': field,
                        'error': f"Invalid {field_type} value: {value}"
                    })

    def _validate_foreign_keys(self, field_types: Dict[str, str]):
        """
        Validate foreign key references.
        """
        for field, field_type in field_types.items():
            if field_type != 'foreign_key' or field not in self.data.columns:
                continue

            model_name = CSVTemplateGenerator.get_template_definition(self.template_type)['model']
            model = apps.get_model(model_name)
            related_model = model._meta.get_field(field).remote_field.model

            # Get all unique values for the foreign key field
            unique_values = self.data[field].dropna().unique()
            existing_values = set(related_model.objects.filter(
                id__in=unique_values
            ).values_list('id', flat=True))

            # Check for invalid references
            for idx, value in self.data[field].items():
                if pd.isnull(value):
                    continue
                if int(value) not in existing_values:
                    self.errors.append({
                        'row': idx + 2,
                        'field': field,
                        'error': f"Invalid reference: {value} does not exist"
                    })