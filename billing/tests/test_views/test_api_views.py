import pytest
import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from billing.views import BillingReportListView, GenerateReportAPIView
from billing.models import BillingReport
from customers.models import Customer

User = get_user_model()


class BillingReportListViewTests(APITestCase):
    """Tests for the BillingReportListView API."""
    
    def setUp(self):
        """Set up test data for API view tests."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="API Test Co",
            contact_email="api@test.com",
            phone_number="555-111-2222"
        )
        
        # Create test billing reports
        self.report1 = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() - timedelta(days=1),
            total_amount=Decimal('100.00'),
            report_data={
                'orders': [],
                'total_amount': '100.00'
            },
            created_by=self.user,
            updated_by=self.user
        )
        
        self.report2 = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=31),
            total_amount=Decimal('200.00'),
            report_data={
                'orders': [],
                'total_amount': '200.00'
            },
            created_by=self.user,
            updated_by=self.user
        )
        
        # Setup client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL for the API view
        self.url = '/api/v1/billing/'
    
    def test_get_all_reports(self):
        """Test retrieving all billing reports."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 2)
    
    def test_filter_by_customer(self):
        """Test filtering reports by customer."""
        # Create another customer with report
        other_customer = Customer.objects.create(
            company_name="Other Co",
            contact_email="other@test.com",
            phone_number="555-333-4444"
        )
        
        BillingReport.objects.create(
            customer=other_customer,
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() - timedelta(days=1),
            total_amount=Decimal('300.00'),
            report_data={
                'orders': [],
                'total_amount': '300.00'
            },
            created_by=self.user,
            updated_by=self.user
        )
        
        # Filter by original customer
        response = self.client.get(f"{self.url}?customer={self.customer.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 2)
        
        # All reports should belong to the filtered customer
        for report in response.data['data']:
            self.assertEqual(report['customer'], self.customer.id)
    
    def test_filter_by_date_range(self):
        """Test filtering reports by date range."""
        # Filter by start_date
        start_date = (timezone.now().date() - timedelta(days=45)).isoformat()
        response = self.client.get(f"{self.url}?start_date={start_date}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)  # Should only return report1
        
        # Filter by end_date
        end_date = (timezone.now().date() - timedelta(days=20)).isoformat()
        response = self.client.get(f"{self.url}?end_date={end_date}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)  # Should return both reports
    
    def test_error_handling(self):
        """Test error handling in the view."""
        # Use patch to force an exception
        with patch('billing.models.BillingReport.objects.select_related') as mock_select:
            mock_select.side_effect = Exception("Test exception")
            
            response = self.client.get(self.url)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['success'], False)
            self.assertIn('error', response.data)


class GenerateReportAPIViewTests(APITestCase):
    """Tests for the GenerateReportAPIView API."""
    
    def setUp(self):
        """Set up test data for API view tests."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="API Test Co",
            contact_email="api@test.com",
            phone_number="555-111-2222"
        )
        
        # Setup client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL for the API view
        self.url = '/api/v1/billing/api/generate-report/'
        
        # Sample valid request data
        self.valid_data = {
            'customer': self.customer.id,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'preview'
        }
    
    @patch('billing.views.BillingReportService.generate_report')
    def test_generate_report_preview(self, mock_generate):
        """Test generating a report with preview format."""
        # Mock the report generation
        preview_data = {
            'orders': [],
            'service_totals': {},
            'total_amount': '0.00',
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'record_count': 0
            }
        }
        mock_generate.return_value = preview_data
        
        # Make request
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['customer_name'], self.customer.company_name)
        self.assertEqual(response.data['data']['total_amount'], '0.00')
    
    @patch('billing.views.BillingReportService.generate_report')
    def test_generate_report_excel(self, mock_generate):
        """Test generating a report with Excel format."""
        # Mock the report generation to return a BytesIO object
        from io import BytesIO
        excel_data = BytesIO(b'fake excel data')
        mock_generate.return_value = excel_data
        
        # Make request with Excel format
        data = self.valid_data.copy()
        data['output_format'] = 'excel'
        
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="billing_report.xlsx"'
        )
    
    @patch('billing.views.BillingReportService.generate_report')
    def test_generate_report_pdf(self, mock_generate):
        """Test generating a report with PDF format."""
        # Mock the report generation to return a BytesIO object with PDF signature
        from io import BytesIO
        pdf_data = BytesIO(b'%PDF-1.5\nfake pdf data')
        mock_generate.return_value = pdf_data
        
        # Make request with PDF format
        data = self.valid_data.copy()
        data['output_format'] = 'pdf'
        
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="billing_report.pdf"'
        )
    
    def test_invalid_data(self):
        """Test request with invalid data."""
        # Missing customer
        data = self.valid_data.copy()
        del data['customer']
        
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Invalid date range (start after end)
        data = self.valid_data.copy()
        data['start_date'] = timezone.now().date().isoformat()
        data['end_date'] = (timezone.now().date() - timedelta(days=1)).isoformat()
        
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_nonexistent_customer(self):
        """Test request with non-existent customer."""
        data = self.valid_data.copy()
        data['customer'] = 99999  # Non-existent customer ID
        
        response = self.client.post(
            self.url,
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('billing.views.BillingReportService.generate_report')
    def test_service_error(self, mock_generate):
        """Test handling service errors."""
        # Mock the report generation to raise an exception
        mock_generate.side_effect = Exception("Test service error")
        
        response = self.client.post(
            self.url,
            self.valid_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'Failed to generate report')