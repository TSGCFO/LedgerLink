# billing/tests/test_views.py

import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from billing.models import BillingReport
from billing.tests.factories import BillingReportFactory, UserFactory
from customers.tests.factories import CustomerFactory

pytestmark = pytest.mark.django_db

class TestBillingReportListView:
    """
    Test cases for the BillingReportListView.
    """
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_list_reports(self, api_client):
        """Test listing billing reports."""
        # Create multiple reports
        reports = [BillingReportFactory.create() for _ in range(3)]
        
        # Make API request
        url = reverse('billing-reports-list')
        response = api_client.get(url)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['count'] == 3
        
        # Verify reports are returned
        report_ids = [r['id'] for r in response.data['data']]
        for report in reports:
            assert report.id in report_ids
    
    def test_filter_by_customer(self, api_client):
        """Test filtering reports by customer."""
        # Create customers and reports
        customer1 = CustomerFactory.create()
        customer2 = CustomerFactory.create()
        
        report1 = BillingReportFactory.create(customer=customer1)
        report2 = BillingReportFactory.create(customer=customer1)
        report3 = BillingReportFactory.create(customer=customer2)
        
        # Filter for customer1
        url = reverse('billing-reports-list')
        response = api_client.get(f"{url}?customer={customer1.id}")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Verify only customer1's reports are returned
        report_ids = [r['id'] for r in response.data['data']]
        assert report1.id in report_ids
        assert report2.id in report_ids
        assert report3.id not in report_ids
    
    def test_filter_by_date_range(self, api_client):
        """Test filtering reports by date range."""
        # Create reports with different date ranges
        today = timezone.now().date()
        
        report1 = BillingReportFactory.create(
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=31)
        )
        report2 = BillingReportFactory.create(
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=16)
        )
        report3 = BillingReportFactory.create(
            start_date=today - timedelta(days=15),
            end_date=today
        )
        
        # Filter by start date
        url = reverse('billing-reports-list')
        start_date = (today - timedelta(days=30)).isoformat()
        response = api_client.get(f"{url}?start_date={start_date}")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Verify only reports with start_date >= filter are returned
        report_ids = [r['id'] for r in response.data['data']]
        assert report1.id not in report_ids
        assert report2.id in report_ids
        assert report3.id in report_ids
        
        # Filter by end date
        url = reverse('billing-reports-list')
        end_date = (today - timedelta(days=16)).isoformat()
        response = api_client.get(f"{url}?end_date={end_date}")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Verify only reports with end_date <= filter are returned
        report_ids = [r['id'] for r in response.data['data']]
        assert report1.id in report_ids
        assert report2.id in report_ids
        assert report3.id not in report_ids
    
    def test_error_handling(self, api_client):
        """Test error handling in list view."""
        # Create a URL that will generate an error (invalid customer ID)
        url = reverse('billing-reports-list')
        with patch('billing.views.BillingReport.objects.select_related',
                  side_effect=Exception('Database error')):
            response = api_client.get(url)
        
        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert 'error' in response.data


class TestGenerateReportAPIView:
    """
    Test cases for the GenerateReportAPIView.
    """
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_invalid_request_data(self, api_client):
        """Test validation of request data."""
        # Missing required fields
        url = reverse('generate-report')
        data = {
            'customer': 1
            # Missing start_date and end_date
        }
        
        response = api_client.post(url, data, format='json')
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'error' in response.data
    
    def test_invalid_date_range(self, api_client):
        """Test validation of date range."""
        customer = CustomerFactory.create()
        today = timezone.now().date()
        
        url = reverse('generate-report')
        data = {
            'customer': customer.id,
            'start_date': today.isoformat(),
            'end_date': (today - timedelta(days=1)).isoformat()
        }
        
        response = api_client.post(url, data, format='json')
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'error' in response.data
    
    def test_nonexistent_customer(self, api_client):
        """Test validation of customer existence."""
        non_existent_id = 99999
        today = timezone.now().date()
        
        url = reverse('generate-report')
        data = {
            'customer': non_existent_id,
            'start_date': (today - timedelta(days=30)).isoformat(),
            'end_date': today.isoformat()
        }
        
        response = api_client.post(url, data, format='json')
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'error' in response.data
    
    @patch('billing.views.BillingReportService')
    def test_preview_format(self, mock_service_class, api_client):
        """Test generating report with preview format."""
        # Setup mock service
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Mock the generate_report method to return a sample result
        mock_result = {
            'total_amount': '500.00',
            'service_totals': {
                'Service A': '300.00',
                'Service B': '200.00'
            },
            'orders': [{'order_id': 1, 'services': [], 'total_amount': '500.00'}]
        }
        mock_service.generate_report.return_value = mock_result
        
        # Create test data
        customer = CustomerFactory.create(company_name="Test Company")
        today = timezone.now().date()
        
        url = reverse('generate-report')
        data = {
            'customer': customer.id,
            'start_date': (today - timedelta(days=30)).isoformat(),
            'end_date': today.isoformat(),
            'output_format': 'preview'
        }
        
        response = api_client.post(url, data, format='json')
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['customer_name'] == customer.company_name
        assert response.data['data']['start_date'] == data['start_date']
        assert response.data['data']['end_date'] == data['end_date']
        assert response.data['data']['total_amount'] == '500.00'
        assert 'preview_data' in response.data['data']
        assert 'generated_at' in response.data['data']
        
        # Verify service called with correct parameters
        mock_service.generate_report.assert_called_once_with(
            customer_id=customer.id,
            start_date=today - timedelta(days=30),
            end_date=today,
            output_format='preview'
        )
    
    @patch('billing.views.BillingReportService')
    def test_file_format(self, mock_service_class, api_client):
        """Test generating report with file format (excel)."""
        # Setup mock service
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Mock the generate_report method to return a BytesIO object
        mock_bytes = MagicMock()
        mock_bytes.getvalue.return_value = b'excel data'
        mock_service.generate_report.return_value = mock_bytes
        
        # Create test data
        customer = CustomerFactory.create()
        today = timezone.now().date()
        
        url = reverse('generate-report')
        data = {
            'customer': customer.id,
            'start_date': (today - timedelta(days=30)).isoformat(),
            'end_date': today.isoformat(),
            'output_format': 'excel'
        }
        
        response = api_client.post(url, data, format='json')
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert response['Content-Disposition'] == 'attachment; filename="billing_report.xlsx"'
        assert response.content == b'excel data'
        
        # Verify service called with correct parameters
        mock_service.generate_report.assert_called_once_with(
            customer_id=customer.id,
            start_date=today - timedelta(days=30),
            end_date=today,
            output_format='excel'
        )
    
    @patch('billing.views.BillingReportService')
    def test_error_handling(self, mock_service_class, api_client):
        """Test error handling in generate report view."""
        # Setup mock service to raise an exception
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.generate_report.side_effect = Exception("Report generation error")
        
        # Create test data
        customer = CustomerFactory.create()
        today = timezone.now().date()
        
        url = reverse('generate-report')
        data = {
            'customer': customer.id,
            'start_date': (today - timedelta(days=30)).isoformat(),
            'end_date': today.isoformat()
        }
        
        response = api_client.post(url, data, format='json')
        
        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert 'error' in response.data