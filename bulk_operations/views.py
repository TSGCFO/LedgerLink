# bulk_operations/views.py
from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
import csv
import logging
from .services.template_generator import CSVTemplateGenerator
from .serializers import BulkSerializerFactory, BulkImportResponseSerializer

logger = logging.getLogger(__name__)


class BulkOperationViewSet(viewsets.ViewSet):
    """
    ViewSet for bulk operations management.
    """

    def list(self, request):
        """
        List all available templates and their metadata.
        """
        try:
            templates = CSVTemplateGenerator.get_available_templates()
            return Response({
                'success': True,
                'data': {
                    'templates': templates,
                    'supportedFormats': ['csv', 'xlsx'],
                    'maxFileSize': 10 * 1024 * 1024  # 10MB
                }
            })
        except Exception as e:
            logger.error(f"Error in list templates: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve templates'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='template-info/(?P<template_type>[^/.]+)')
    def template_info(self, request, template_type):
        """
        Get detailed information about a specific template.
        """
        try:
            template_def = CSVTemplateGenerator.get_template_definition(template_type)
            field_types = CSVTemplateGenerator.get_field_types(template_type)

            return Response({
                'success': True,
                'data': {
                    'templateType': template_type,
                    'fields': template_def['fields'],
                    'requiredFields': template_def['required_fields'],
                    'fieldTypes': field_types
                }
            })
        except KeyError:
            return Response({
                'success': False,
                'error': f"Template type '{template_type}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in template info: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve template information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateDownloadView(views.APIView):
    """
    API endpoint for template downloads.
    """

    def get(self, request, template_type):
        try:
            # Generate template headers
            headers = CSVTemplateGenerator.generate_template_header(template_type)

            # Create the CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{template_type}_template.csv"'

            writer = csv.writer(response)
            writer.writerow(headers)

            return response

        except KeyError:
            return Response({
                'success': False,
                'error': f"Template type '{template_type}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in template download: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkImportView(views.APIView):
    """
    API endpoint for bulk imports.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, template_type):
        try:
            if 'file' not in request.FILES:
                return Response({
                    'success': False,
                    'error': 'No file provided'
                }, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['file']

            # Check file size
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                return Response({
                    'success': False,
                    'error': 'File size exceeds 10MB limit'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Read file
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    return Response({
                        'success': False,
                        'error': 'Unsupported file format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error reading file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check row limit
            if len(df) > 1000:  # Maximum 1000 rows
                return Response({
                    'success': False,
                    'error': 'File exceeds maximum row limit of 1000'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get appropriate serializer
            serializer_class = BulkSerializerFactory.get_serializer(template_type)

            errors = []
            successful_records = 0

            # Process records within transaction
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        data = row.to_dict()
                        serializer = serializer_class(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            successful_records += 1
                        else:
                            errors.append({
                                'row': index + 2,  # +2 for header row and 1-based indexing
                                'errors': serializer.errors
                            })
                    except Exception as e:
                        errors.append({
                            'row': index + 2,
                            'errors': str(e)
                        })

            # Prepare response
            success = len(errors) == 0
            response_data = {
                'success': success,
                'message': 'Import completed',
                'import_summary': {
                    'total_rows': len(df),
                    'successful': successful_records,
                    'failed': len(errors)
                }
            }

            if errors:
                response_data['errors'] = errors

            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in bulk import: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)