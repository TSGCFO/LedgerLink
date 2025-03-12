# bulk_operations/services/import_handler.py
import io
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, BinaryIO
from django.apps import apps
from django.db import transaction
from django.core.exceptions import ValidationError

from .validators import BulkImportValidator
from .template_generator import CSVTemplateGenerator
from ..serializers import BulkSerializerFactory


class BulkImportHandler:
    """
    Service for handling bulk import operations.
    """

    SUPPORTED_FORMATS = ['csv', 'xlsx', 'xls']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self, template_type: str, file_obj: BinaryIO, file_format: str = 'csv'):
        """
        Initialize import handler with template type and file.
        
        Args:
            template_type: Type of template being imported
            file_obj: File-like object with the data
            file_format: Format of the file (csv, xlsx, xls)
        """
        self.template_type = template_type
        self.file_obj = file_obj
        self.file_format = file_format.lower()
        
        if self.file_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_format}. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}")
        
        self.df = None
        self.errors = []
        self.imported_records = []
        self.validator = None
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported file formats."""
        return cls.SUPPORTED_FORMATS
    
    @classmethod
    def get_max_file_size(cls) -> int:
        """Get maximum allowed file size in bytes."""
        return cls.MAX_FILE_SIZE
    
    def parse_file(self) -> bool:
        """
        Parse the input file into a DataFrame.
        Returns True if successful, False otherwise.
        """
        try:
            # Reset file position
            self.file_obj.seek(0)
            
            if self.file_format == 'csv':
                self.df = pd.read_csv(self.file_obj)
            elif self.file_format in ['xlsx', 'xls']:
                self.df = pd.read_excel(self.file_obj)
                
            # Clean column names (strip whitespace)
            self.df.columns = self.df.columns.str.strip()
            
            return True
            
        except Exception as e:
            self.errors.append({
                'row': 'N/A',
                'field': 'N/A',
                'error': f"File parsing error: {str(e)}"
            })
            return False
    
    def validate(self) -> bool:
        """
        Validate the imported data against the template definition.
        Returns True if validation passes, False otherwise.
        """
        if self.df is None:
            if not self.parse_file():
                return False
        
        self.validator = BulkImportValidator(self.template_type, self.df)
        validation_success = self.validator.validate()
        
        if not validation_success:
            self.errors.extend(self.validator.errors)
        
        return validation_success
    
    @transaction.atomic
    def import_data(self) -> Tuple[int, int]:
        """
        Import the validated data into the database.
        Returns a tuple of (successful_count, failed_count).
        """
        if not self.validator or self.df is None:
            raise ValueError("Data must be validated before importing")
        
        if self.errors:
            raise ValueError(f"Cannot import data with validation errors ({len(self.errors)} errors)")
        
        serializer_class = BulkSerializerFactory.get_serializer(self.template_type)
        if not serializer_class:
            raise ValueError(f"No serializer available for template type: {self.template_type}")
        
        success_count = 0
        failed_count = 0
        
        # Process each row
        for idx, row in self.df.iterrows():
            try:
                # Clean the data
                row_data = row.dropna().to_dict()
                
                # Create and validate serializer
                serializer = serializer_class(data=row_data)
                if serializer.is_valid():
                    # Save the record
                    instance = serializer.save()
                    self.imported_records.append(instance)
                    success_count += 1
                else:
                    # Add serializer errors
                    for field, errors in serializer.errors.items():
                        self.errors.append({
                            'row': idx + 2,  # Add 2 for header row and 1-based indexing
                            'field': field,
                            'error': ' '.join(errors)
                        })
                    failed_count += 1
            except Exception as e:
                self.errors.append({
                    'row': idx + 2,
                    'field': 'N/A',
                    'error': f"Import error: {str(e)}"
                })
                failed_count += 1
        
        return success_count, failed_count
    
    def get_import_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the import operation.
        """
        return {
            'template_type': self.template_type,
            'total_rows': len(self.df) if self.df is not None else 0,
            'successful': len(self.imported_records),
            'failed': len(self.errors),
            'errors': self.errors[:100],  # Limit to first 100 errors
            'has_more_errors': len(self.errors) > 100
        }
    
    def process(self) -> Dict[str, Any]:
        """
        Process the import: parse, validate, and import the data.
        Returns import summary.
        """
        # Parse file
        if not self.parse_file():
            return {
                'template_type': self.template_type,
                'total_rows': 0,
                'successful': 0,
                'failed': 0,
                'errors': self.errors,
                'has_more_errors': False
            }
        
        # Validate data
        if not self.validate():
            return {
                'template_type': self.template_type,
                'total_rows': len(self.df) if self.df is not None else 0,
                'successful': 0,
                'failed': len(self.errors),
                'errors': self.errors[:100],
                'has_more_errors': len(self.errors) > 100
            }
        
        # Import data
        try:
            success_count, failed_count = self.import_data()
        except Exception as e:
            self.errors.append({
                'row': 'N/A',
                'field': 'N/A',
                'error': f"Import process error: {str(e)}"
            })
            return {
                'template_type': self.template_type,
                'total_rows': len(self.df),
                'successful': 0,
                'failed': len(self.df),
                'errors': self.errors[:100],
                'has_more_errors': len(self.errors) > 100
            }
        
        return self.get_import_summary()