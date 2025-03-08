from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from billing.models import BillingReport, BillingReportDetail
from .factories import (
    BillingReportFactory, BillingReportDetailFactory,
    CustomerFactory, OrderFactory, UserFactory
)


class BillingReportModelTests(TestCase):
    """Tests for the BillingReport model."""
    
    def setUp(self):
        self.customer = CustomerFactory()
        self.user = UserFactory()
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
    
    def test_billing_report_creation(self):
        """Test basic creation of a BillingReport model."""
        report = BillingReportFactory()
        self.assertIsNotNone(report.id)
        self.assertEqual(str(report), 
            f"Report for {report.customer.company_name} ({report.start_date} to {report.end_date})")
        
    def test_report_data_json_field(self):
        """Test that the report_data JSON field works correctly."""
        report = BillingReportFactory()
        
        # Check that report_data is a dict
        self.assertIsInstance(report.report_data, dict)
        
        # Check that it contains expected keys
        self.assertIn('orders', report.report_data)
        self.assertIn('total_amount', report.report_data)
        
        # Verify we can access nested data
        self.assertIsInstance(report.report_data['orders'], list)
        if report.report_data['orders']:
            order = report.report_data['orders'][0]
            self.assertIn('order_id', order)
            self.assertIn('services', order)
            
    def test_validation_start_date_before_end_date(self):
        """Test that start_date must be before end_date."""
        # Valid case: start_date before end_date
        report = BillingReport(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=Decimal('100.00'),
            report_data={'orders': [], 'total_amount': '100.00'},
            created_by=self.user,
            updated_by=self.user
        )
        report.clean()  # Should not raise ValidationError
        
        # Invalid case: start_date after end_date
        report = BillingReport(
            customer=self.customer,
            start_date=self.end_date,
            end_date=self.start_date,
            total_amount=Decimal('100.00'),
            report_data={'orders': [], 'total_amount': '100.00'},
            created_by=self.user,
            updated_by=self.user
        )
        with self.assertRaises(ValidationError):
            report.clean()
            
    def test_validation_future_start_date(self):
        """Test that start_date cannot be in the future."""
        # Invalid case: start_date in future
        future_date = timezone.now().date() + timedelta(days=1)
        report = BillingReport(
            customer=self.customer,
            start_date=future_date,
            end_date=future_date + timedelta(days=10),
            total_amount=Decimal('100.00'),
            report_data={'orders': [], 'total_amount': '100.00'},
            created_by=self.user,
            updated_by=self.user
        )
        with self.assertRaises(ValidationError):
            report.clean()
    
    def test_validation_date_range_limit(self):
        """Test that date range cannot exceed MAX_REPORT_DATE_RANGE."""
        from django.conf import settings
        max_range = getattr(settings, 'MAX_REPORT_DATE_RANGE', 365)
        
        # Valid case: within range limit
        report = BillingReport(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.start_date + timedelta(days=max_range - 1),
            total_amount=Decimal('100.00'),
            report_data={'orders': [], 'total_amount': '100.00'},
            created_by=self.user,
            updated_by=self.user
        )
        report.clean()  # Should not raise ValidationError
        
        # Invalid case: exceeds range limit
        report = BillingReport(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.start_date + timedelta(days=max_range + 1),
            total_amount=Decimal('100.00'),
            report_data={'orders': [], 'total_amount': '100.00'},
            created_by=self.user,
            updated_by=self.user
        )
        with self.assertRaises(ValidationError):
            report.clean()
    
    def test_total_amount_positive(self):
        """Test that total_amount must be positive."""
        # Create report with negative amount - should fail validation
        with self.assertRaises(ValidationError):
            report = BillingReport(
                customer=self.customer,
                start_date=self.start_date,
                end_date=self.end_date,
                total_amount=Decimal('-100.00'),
                report_data={'orders': [], 'total_amount': '-100.00'},
                created_by=self.user,
                updated_by=self.user
            )
            report.full_clean()
    
    def test_relationship_with_details(self):
        """Test the relationship between BillingReport and BillingReportDetail."""
        report = BillingReportFactory()
        
        # Create multiple details for this report
        detail1 = BillingReportDetailFactory(report=report)
        detail2 = BillingReportDetailFactory(report=report)
        detail3 = BillingReportDetailFactory(report=report)
        
        # Verify related name works correctly
        self.assertEqual(report.details.count(), 3)
        self.assertIn(detail1, report.details.all())
        self.assertIn(detail2, report.details.all())
        self.assertIn(detail3, report.details.all())


class BillingReportDetailModelTests(TestCase):
    """Tests for the BillingReportDetail model."""
    
    def setUp(self):
        self.report = BillingReportFactory()
        self.order = OrderFactory(customer=self.report.customer)
    
    def test_billing_report_detail_creation(self):
        """Test basic creation of a BillingReportDetail model."""
        detail = BillingReportDetailFactory(report=self.report, order=self.order)
        self.assertIsNotNone(detail.id)
        
        # Test string representation
        expected_str = f"Detail for {self.report} - Order {self.order.transaction_id}"
        self.assertEqual(str(detail), expected_str)
        
    def test_service_breakdown_json_field(self):
        """Test that the service_breakdown JSON field works correctly."""
        detail = BillingReportDetailFactory(report=self.report, order=self.order)
        
        # Check that service_breakdown is a dict
        self.assertIsInstance(detail.service_breakdown, dict)
        
        # Verify we can access nested data
        for service_key, service_data in detail.service_breakdown.items():
            self.assertIn('service_id', service_data)
            self.assertIn('service_name', service_data)
            self.assertIn('amount', service_data)
    
    def test_total_amount_positive(self):
        """Test that total_amount must be positive."""
        # Create detail with negative amount - should fail validation
        with self.assertRaises(ValidationError):
            detail = BillingReportDetail(
                report=self.report,
                order=self.order,
                total_amount=Decimal('-100.00'),
                service_breakdown={}
            )
            detail.full_clean()