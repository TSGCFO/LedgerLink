import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from customers.models import Customer
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from ..models import BillingReport, OrderCost, ServiceCost
from ..views import BillingReportViewSet


class BillingReportViewSetTest(APITestCase):
    """Tests for BillingReportViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create test billing reports
        self.report1 = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=31),
            total_amount=Decimal('100.00'),
            service_totals={
                "1": {"service_name": "Service 1", "amount": 100.00}
            }
        )
        
        self.report2 = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() - timedelta(days=1),
            total_amount=Decimal('200.00'),
            service_totals={
                "1": {"service_name": "Service 1", "amount": 100.00},
                "2": {"service_name": "Service 2", "amount": 100.00}
            }
        )
        
        # URLs
        self.list_url = reverse('billingreport-list')
        self.detail_url1 = reverse('billingreport-detail', kwargs={'pk': self.report1.id})
        self.detail_url2 = reverse('billingreport-detail', kwargs={'pk': self.report2.id})
        self.generate_url = reverse('billingreport-generate')
        self.download_url1 = reverse('billingreport-download', kwargs={'pk': self.report1.id})
        self.customer_summary_url = reverse('billingreport-customer-summary')
        
    def test_list_reports(self):
        """Test listing billing reports"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two reports in the response
        
    def test_list_reports_with_filters(self):
        """Test listing billing reports with filters"""
        # Test customer filter
        response = self.client.get(f"{self.list_url}?customer_id={self.customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Test date filter
        date_str = (timezone.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        response = self.client.get(f"{self.list_url}?start_date={date_str}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only report2 should match
        
        # Test ordering
        response = self.client.get(f"{self.list_url}?order_by=total_amount")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.report1.id)  # report1 has lower amount
        
    def test_retrieve_report(self):
        """Test retrieving a single billing report"""
        response = self.client.get(self.detail_url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.report1.id)
        self.assertEqual(float(response.data['total_amount']), 100.00)
        
    def test_generate_report(self):
        """Test generating a new billing report"""
        # Create test data for order
        order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF12345",
            status="shipped",
            priority="medium"
        )
        
        # Create test service and customer service
        service = Service.objects.create(
            name="Test Service",
            charge_type="single"
        )
        
        customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=service,
            unit_price=Decimal('100.00')
        )
        
        # Mock the BillingCalculator.generate_report method
        with mock.patch('Billing_V2.views.BillingCalculator') as mock_calculator:
            mock_instance = mock.MagicMock()
            mock_calculator.return_value = mock_instance
            
            # Set up the mock report
            mock_report = BillingReport(
                customer=self.customer,
                start_date=timezone.now() - timedelta(days=30),
                end_date=timezone.now(),
                total_amount=Decimal('300.00')
            )
            mock_report.to_dict = mock.MagicMock(return_value={
                'id': 3,
                'customer_id': self.customer.id,
                'total_amount': 300.0,
                'service_totals': {"1": {"service_name": "Test Service", "amount": 300.0}}
            })
            mock_instance.generate_report.return_value = mock_report
            mock_instance.to_csv.return_value = "order_id,service_id,service_name,amount"
            
            # Test generating report with JSON format
            data = {
                'customer_id': self.customer.id,
                'start_date': '2023-01-01',
                'end_date': '2023-01-31',
                'output_format': 'json'
            }
            
            response = self.client.post(self.generate_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['customer_id'], self.customer.id)
            
            # Test generating report with CSV format
            data['output_format'] = 'csv'
            response = self.client.post(self.generate_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'text/csv')
            
    def test_download_report(self):
        """Test downloading a billing report"""
        # Mock the BillingCalculator.to_csv method
        with mock.patch('Billing_V2.views.BillingCalculator') as mock_calculator:
            mock_instance = mock.MagicMock()
            mock_calculator.return_value = mock_instance
            mock_instance.to_csv.return_value = "order_id,service_id,service_name,amount"
            
            # Test downloading in CSV format
            response = self.client.get(f"{self.download_url1}?format=csv")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'text/csv')
            
            # Test downloading in JSON format
            response = self.client.get(f"{self.download_url1}?format=json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['id'], self.report1.id)
            
    def test_customer_summary(self):
        """Test getting customer summary"""
        response = self.client.get(self.customer_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have one entry for our test customer
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['customer_id'], self.customer.id)
        self.assertEqual(response.data[0]['report_count'], 2)
        self.assertEqual(response.data[0]['total_amount'], 300.0)  # 100 + 200