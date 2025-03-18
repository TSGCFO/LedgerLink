"""
Tests for the BillingReportListView.
"""

import pytest
import json
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from billing.models import BillingReport
from billing.views import BillingReportListView

pytestmark = pytest.mark.django_db

class TestBillingReportListView:
    """Test the BillingReportListView."""
    
    @pytest.fixture
    def api_client(self):
        """Return an API client for testing."""
        return APIClient()
    
    @pytest.fixture
    def url(self):
        """Return the URL for the view."""
        return reverse('billing-reports-list')  # Adjust to match your URL name
    
    def test_list_all_reports(self, api_client, url, basic_billing_report):
        """Test listing all billing reports."""
        # Create another billing report for testing
        second_report = BillingReport.objects.create(
            customer=basic_billing_report.customer,
            start_date=timezone.now().date() - timedelta(days=15),
            end_date=timezone.now().date(),
            total_amount=100.00,
            report_data={"orders": [], "total_amount": "100.00"}
        )
        
        # Make request
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == 200
        assert response.data['success'] is True
        
        # There should be at least two reports
        assert response.data['count'] >= 2
        
        # Check that our reports are in the results
        report_ids = [report['id'] for report in response.data['data']]
        assert basic_billing_report.id in report_ids
        assert second_report.id in report_ids
    
    def test_filter_by_customer(self, api_client, url, basic_billing_report, billing_customer):
        """Test filtering reports by customer."""
        # Create another customer and report
        from customers.tests.factories import CustomerFactory
        other_customer = CustomerFactory(company_name="Other Customer")
        
        other_report = BillingReport.objects.create(
            customer=other_customer,
            start_date=timezone.now().date() - timedelta(days=15),
            end_date=timezone.now().date(),
            total_amount=100.00,
            report_data={"orders": [], "total_amount": "100.00"}
        )
        
        # Make request with customer filter
        response = api_client.get(f"{url}?customer={billing_customer.id}")
        
        # Check response
        assert response.status_code == 200
        assert response.data['success'] is True
        
        # Should only have reports for the filtered customer
        for report in response.data['data']:
            assert report['customer'] == billing_customer.id
        
        # Other customer's report should not be in the results
        report_ids = [report['id'] for report in response.data['data']]
        assert other_report.id not in report_ids
    
    def test_filter_by_date_range(self, api_client, url, billing_customer):
        """Test filtering reports by date range."""
        # Create reports with different date ranges
        today = timezone.now().date()
        
        # Report 1: Last month
        report1 = BillingReport.objects.create(
            customer=billing_customer,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=31),
            total_amount=100.00,
            report_data={"orders": [], "total_amount": "100.00"}
        )
        
        # Report 2: This month
        report2 = BillingReport.objects.create(
            customer=billing_customer,
            start_date=today - timedelta(days=30),
            end_date=today,
            total_amount=200.00,
            report_data={"orders": [], "total_amount": "200.00"}
        )
        
        # Test filtering by start date
        start_filter = (today - timedelta(days=40)).isoformat()
        response = api_client.get(f"{url}?start_date={start_filter}")
        
        assert response.status_code == 200
        report_ids = [report['id'] for report in response.data['data']]
        assert report2.id in report_ids
        assert report1.id not in report_ids
        
        # Test filtering by end date
        end_filter = (today - timedelta(days=30)).isoformat()
        response = api_client.get(f"{url}?end_date={end_filter}")
        
        assert response.status_code == 200
        report_ids = [report['id'] for report in response.data['data']]
        assert report1.id in report_ids
        assert report2.id not in report_ids
    
    def test_error_handling(self, api_client, url, monkeypatch):
        """Test error handling in the view."""
        # Mock the queryset method to raise an exception
        def mock_get(*args, **kwargs):
            raise ValueError("Simulated error")
        
        # Patch the get method of the view
        monkeypatch.setattr(BillingReportListView, 'get', mock_get)
        
        # Make request
        response = api_client.get(url)
        
        # Check error response
        assert response.status_code == 500
        assert response.data['success'] is False
        assert 'error' in response.data