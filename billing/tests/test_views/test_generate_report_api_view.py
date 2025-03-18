"""
Tests for the GenerateReportAPIView.
"""

import pytest
import json
import io
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError

from billing.views import GenerateReportAPIView
from billing.services import BillingReportService
from customers.models import Customer

pytestmark = pytest.mark.django_db

class TestGenerateReportAPIView:
    """Test the GenerateReportAPIView."""
    
    @pytest.fixture
    def api_client(self):
        """Return an API client for testing."""
        return APIClient()
    
    @pytest.fixture
    def url(self):
        """Return the URL for the view."""
        return reverse('generate-report')  # Adjust to match your URL name
    
    def test_valid_request_preview_format(self, api_client, url, billing_customer, monkeypatch):
        """Test generating a report with valid data in preview format."""
        # Mock the generate_report method to return test data
        mock_result = {
            'orders': [],
            'service_totals': {},
            'total_amount': '0.00',
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'record_count': 0
            }
        }
        
        mock_generate_report = MagicMock(return_value=mock_result)
        monkeypatch.setattr(BillingReportService, 'generate_report', mock_generate_report)
        
        # Prepare request data
        data = {
            'customer': billing_customer.id,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'preview'
        }
        
        # Make request
        response = api_client.post(url, data=data, format='json')
        
        # Check response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'data' in response.data
        assert response.data['data']['customer_name'] == billing_customer.company_name
        assert 'preview_data' in response.data['data']
        
        # Verify the service was called with correct parameters
        mock_generate_report.assert_called_once_with(
            customer_id=billing_customer.id,
            start_date=data['start_date'],
            end_date=data['end_date'],
            output_format='preview'
        )
    
    def test_valid_request_excel_format(self, api_client, url, billing_customer, monkeypatch):
        """Test generating a report with valid data in Excel format."""
        # Mock the generate_report method to return a file-like object
        mock_file = io.BytesIO(b'Excel file content')
        mock_generate_report = MagicMock(return_value=mock_file)
        monkeypatch.setattr(BillingReportService, 'generate_report', mock_generate_report)
        
        # Mock the ReportFileHandler methods
        monkeypatch.setattr(
            'billing.utils.ReportFileHandler.get_content_type',
            lambda format: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        monkeypatch.setattr(
            'billing.utils.ReportFileHandler.get_file_extension',
            lambda format: 'xlsx'
        )
        
        # Prepare request data
        data = {
            'customer': billing_customer.id,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'excel'
        }
        
        # Make request
        response = api_client.post(url, data=data, format='json')
        
        # Check response
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert response['Content-Disposition'] == 'attachment; filename="billing_report.xlsx"'
        
        # Verify the service was called with correct parameters
        mock_generate_report.assert_called_once_with(
            customer_id=billing_customer.id,
            start_date=data['start_date'],
            end_date=data['end_date'],
            output_format='excel'
        )
    
    def test_invalid_request_data(self, api_client, url):
        """Test validation of request data."""
        # Prepare invalid request data (missing fields)
        data = {
            # Missing customer, start_date, end_date
            'output_format': 'preview'
        }
        
        # Make request
        response = api_client.post(url, data=data, format='json')
        
        # Check response
        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'error' in response.data
        
        # Check error messages
        errors = response.data['error']
        assert 'customer' in errors
        assert 'start_date' in errors
        assert 'end_date' in errors
    
    def test_validation_error_handling(self, api_client, url, billing_customer, monkeypatch):
        """Test handling of ValidationError in the service."""
        # Mock the generate_report method to raise ValidationError
        def mock_generate_report(*args, **kwargs):
            raise ValidationError("Test validation error")
        
        monkeypatch.setattr(BillingReportService, 'generate_report', mock_generate_report)
        
        # Prepare request data
        data = {
            'customer': billing_customer.id,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'preview'
        }
        
        # Make request
        response = api_client.post(url, data=data, format='json')
        
        # Check response
        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'error' in response.data
        assert 'Test validation error' in str(response.data['error'])
    
    def test_customer_not_found(self, api_client, url, monkeypatch):
        """Test handling of Customer.DoesNotExist error."""
        # Mock Customer.objects.get to raise Customer.DoesNotExist
        def mock_get(*args, **kwargs):
            if 'id' in kwargs and kwargs['id'] == 9999:
                raise Customer.DoesNotExist("Customer not found")
            return MagicMock()
        
        monkeypatch.setattr(Customer.objects, 'get', mock_get)
        
        # Prepare request data with non-existent customer ID
        data = {
            'customer': 9999,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'preview'
        }
        
        # Make request
        response = api_client.post(url, data=data, format='json')
        
        # Check response
        assert response.status_code == 404
        assert response.data['success'] is False
        assert response.data['error'] == 'Customer not found'
    
    def test_general_exception_handling(self, api_client, url, billing_customer, monkeypatch):
        """Test handling of general exceptions."""
        # Mock the generate_report method to raise a general exception
        def mock_generate_report(*args, **kwargs):
            raise Exception("Unexpected error")
        
        monkeypatch.setattr(BillingReportService, 'generate_report', mock_generate_report)
        
        # Prepare request data
        data = {
            'customer': billing_customer.id,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'preview'
        }
        
        # Make request
        response = api_client.post(url, data=data, format='json')
        
        # Check response
        assert response.status_code == 500
        assert response.data['success'] is False
        assert response.data['error'] == 'Failed to generate report'