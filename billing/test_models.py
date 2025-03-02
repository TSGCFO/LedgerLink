from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, timedelta

from customers.models import Customer
from orders.models import Order
from billing.models import BillingReport, BillingReportDetail

User = get_user_model()

class BillingReportModelTests(TestCase):
    """Tests for the BillingReport model"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name='Test Company',
            contact_email='contact@example.com',
            phone_number='123-456-7890'
        )
        
        # Test dates
        self.today = timezone.now().date()
        self.start_date = self.today - timedelta(days=30)
        self.end_date = self.today - timedelta(days=1)
        
        # Sample report data
        self.report_data = {
            'orders': [
                {
                    'order_id': 'ORD-001',
                    'services': [
                        {
                            'service_id': 1,
                            'service_name': 'Shipping',
                            'amount': '10.50'
                        }
                    ],
                    'total_amount': '10.50'
                }
            ],
            'total_amount': '10.50'
        }
    
    def test_create_billing_report(self):
        """Test creating a billing report"""
        report = BillingReport.objects.create(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=Decimal('10.50'),
            report_data=self.report_data,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.start_date, self.start_date)
        self.assertEqual(report.end_date, self.end_date)
        self.assertEqual(report.total_amount, Decimal('10.50'))
        self.assertEqual(report.report_data, self.report_data)
        self.assertEqual(report.created_by, self.user)
        self.assertEqual(report.updated_by, self.user)
        
        # Check auto-populated fields
        self.assertIsNotNone(report.generated_at)
        self.assertIsNotNone(report.created_at)
        self.assertIsNotNone(report.updated_at)
    
    def test_string_representation(self):
        """Test the string representation of a billing report"""
        report = BillingReport.objects.create(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=Decimal('10.50'),
            report_data=self.report_data
        )
        
        expected_str = f"Report for {self.customer.company_name} ({self.start_date} to {self.end_date})"
        self.assertEqual(str(report), expected_str)
    
    def test_start_date_after_end_date(self):
        """Test validation fails if start date is after end date"""
        report = BillingReport(
            customer=self.customer,
            start_date=self.end_date,
            end_date=self.start_date,
            total_amount=Decimal('10.50'),
            report_data=self.report_data
        )
        
        with self.assertRaises(ValidationError):
            report.full_clean()
    
    def test_future_start_date(self):
        """Test validation fails if start date is in the future"""
        future_date = self.today + timedelta(days=1)
        
        report = BillingReport(
            customer=self.customer,
            start_date=future_date,
            end_date=future_date + timedelta(days=1),
            total_amount=Decimal('10.50'),
            report_data=self.report_data
        )
        
        with self.assertRaises(ValidationError):
            report.full_clean()
    
    def test_date_range_too_large(self):
        """Test validation fails if date range is too large"""
        # Set a very large date range
        with self.settings(MAX_REPORT_DATE_RANGE=10):
            report = BillingReport(
                customer=self.customer,
                start_date=self.today - timedelta(days=20),
                end_date=self.today,
                total_amount=Decimal('10.50'),
                report_data=self.report_data
            )
            
            with self.assertRaises(ValidationError):
                report.full_clean()
    
    def test_negative_total_amount(self):
        """Test validation fails if total amount is negative"""
        report = BillingReport(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=Decimal('-10.50'),
            report_data=self.report_data
        )
        
        with self.assertRaises(ValidationError):
            report.full_clean()


class BillingReportDetailModelTests(TestCase):
    """Tests for the BillingReportDetail model"""
    
    def setUp(self):
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name='Test Company',
            contact_email='contact@example.com',
            phone_number='123-456-7890'
        )
        
        # Create a test order
        self.order = Order.objects.create(
            customer=self.customer,
            transaction_id='ORD-001',
            reference_number='REF-001',
            close_date=timezone.now()
        )
        
        # Create a test billing report
        self.report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() - timedelta(days=1),
            total_amount=Decimal('10.50'),
            report_data={
                'orders': [
                    {
                        'order_id': 'ORD-001',
                        'services': [
                            {
                                'service_id': 1,
                                'service_name': 'Shipping',
                                'amount': '10.50'
                            }
                        ],
                        'total_amount': '10.50'
                    }
                ],
                'total_amount': '10.50'
            }
        )
        
        # Sample service breakdown
        self.service_breakdown = {
            'services': [
                {
                    'service_id': 1,
                    'service_name': 'Shipping',
                    'amount': '10.50'
                }
            ]
        }
    
    def test_create_billing_report_detail(self):
        """Test creating a billing report detail"""
        detail = BillingReportDetail.objects.create(
            report=self.report,
            order=self.order,
            service_breakdown=self.service_breakdown,
            total_amount=Decimal('10.50')
        )
        
        self.assertEqual(detail.report, self.report)
        self.assertEqual(detail.order, self.order)
        self.assertEqual(detail.service_breakdown, self.service_breakdown)
        self.assertEqual(detail.total_amount, Decimal('10.50'))
    
    def test_string_representation(self):
        """Test the string representation of a billing report detail"""
        detail = BillingReportDetail.objects.create(
            report=self.report,
            order=self.order,
            service_breakdown=self.service_breakdown,
            total_amount=Decimal('10.50')
        )
        
        expected_str = f"Detail for {self.report} - Order {self.order.transaction_id}"
        self.assertEqual(str(detail), expected_str)
    
    def test_negative_total_amount(self):
        """Test validation fails if total amount is negative"""
        detail = BillingReportDetail(
            report=self.report,
            order=self.order,
            service_breakdown=self.service_breakdown,
            total_amount=Decimal('-10.50')
        )
        
        with self.assertRaises(ValidationError):
            detail.full_clean()