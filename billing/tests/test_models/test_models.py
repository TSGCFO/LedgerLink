# billing/tests/test_models.py

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from billing.models import BillingReport, BillingReportDetail
from billing.tests.factories import BillingReportFactory, BillingReportDetailFactory
from customers.tests.factories import CustomerFactory
from orders.tests.factories import OrderFactory

pytestmark = pytest.mark.django_db

class TestBillingReportModel:
    """
    Test cases for the BillingReport model.
    """
    
    def test_create_billing_report(self):
        """Test creating a billing report."""
        report = BillingReportFactory.create()
        assert report.pk is not None
        assert BillingReport.objects.count() == 1
        assert BillingReport.objects.first().customer == report.customer
    
    def test_billing_report_str_method(self):
        """Test the string representation of a billing report."""
        customer = CustomerFactory.create(company_name="Test Company")
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
        report = BillingReportFactory.create(
            customer=customer,
            start_date=start_date,
            end_date=end_date
        )
        assert str(report) == f"Report for Test Company ({start_date} to {end_date})"
    
    def test_billing_report_validation_date_order(self):
        """Test that start date must be before end date."""
        today = timezone.now().date()
        customer = CustomerFactory.create()
        
        with pytest.raises(ValidationError):
            report = BillingReport(
                customer=customer,
                start_date=today,
                end_date=today - timedelta(days=1),
                total_amount=Decimal('100.00'),
                report_data={"orders": [], "total_amount": "100.00"}
            )
            report.save()
    
    def test_billing_report_validation_future_date(self):
        """Test that start date cannot be in the future."""
        today = timezone.now().date()
        customer = CustomerFactory.create()
        
        with pytest.raises(ValidationError):
            report = BillingReport(
                customer=customer,
                start_date=today + timedelta(days=1),
                end_date=today + timedelta(days=30),
                total_amount=Decimal('100.00'),
                report_data={"orders": [], "total_amount": "100.00"}
            )
            report.save()
    
    def test_billing_report_with_valid_json_data(self):
        """Test saving a billing report with valid JSON data."""
        customer = CustomerFactory.create()
        today = timezone.now().date()
        
        report_data = {
            "orders": [
                {
                    "order_id": 1,
                    "services": [
                        {
                            "service_id": 1,
                            "service_name": "Service A",
                            "amount": "50.00"
                        }
                    ],
                    "total_amount": "50.00"
                }
            ],
            "total_amount": "50.00",
            "service_totals": {
                "Service A": "50.00"
            }
        }
        
        report = BillingReport(
            customer=customer,
            start_date=today - timedelta(days=30),
            end_date=today,
            total_amount=Decimal('50.00'),
            report_data=report_data
        )
        report.save()
        
        # Reload from database to ensure data is saved properly
        saved_report = BillingReport.objects.get(pk=report.pk)
        assert saved_report.report_data == report_data
        assert saved_report.total_amount == Decimal('50.00')
    
    def test_billing_report_total_amount_minimum(self):
        """Test that total_amount cannot be negative."""
        customer = CustomerFactory.create()
        today = timezone.now().date()
        
        with pytest.raises(ValidationError):
            report = BillingReport(
                customer=customer,
                start_date=today - timedelta(days=30),
                end_date=today,
                total_amount=Decimal('-10.00'),
                report_data={"orders": [], "total_amount": "-10.00"}
            )
            report.save()
    
    def test_billing_report_ordering(self):
        """Test that billing reports are ordered by -generated_at."""
        customer = CustomerFactory.create()
        
        # Create reports with different generated_at times
        report1 = BillingReportFactory.create(
            customer=customer,
            generated_at=timezone.now() - timedelta(days=2)
        )
        report2 = BillingReportFactory.create(
            customer=customer,
            generated_at=timezone.now() - timedelta(days=1)
        )
        report3 = BillingReportFactory.create(
            customer=customer,
            generated_at=timezone.now()
        )
        
        reports = BillingReport.objects.all()
        assert reports[0] == report3
        assert reports[1] == report2
        assert reports[2] == report1


class TestBillingReportDetailModel:
    """
    Test cases for the BillingReportDetail model.
    """
    
    def test_create_billing_report_detail(self):
        """Test creating a billing report detail."""
        detail = BillingReportDetailFactory.create()
        assert detail.pk is not None
        assert BillingReportDetail.objects.count() == 1
        assert BillingReportDetail.objects.first().report == detail.report
    
    def test_billing_report_detail_str_method(self):
        """Test the string representation of a billing report detail."""
        report = BillingReportFactory.create()
        order = OrderFactory.create(transaction_id="ORD-12345")
        detail = BillingReportDetailFactory.create(report=report, order=order)
        assert str(detail) == f"Detail for {report} - Order {order.transaction_id}"
    
    def test_billing_report_detail_with_service_breakdown(self):
        """Test saving a billing report detail with service breakdown."""
        report = BillingReportFactory.create()
        order = OrderFactory.create()
        
        service_breakdown = {
            "services": [
                {
                    "service_id": 1,
                    "service_name": "Service A",
                    "amount": "30.00"
                },
                {
                    "service_id": 2,
                    "service_name": "Service B",
                    "amount": "20.00"
                }
            ]
        }
        
        detail = BillingReportDetail(
            report=report,
            order=order,
            service_breakdown=service_breakdown,
            total_amount=Decimal('50.00')
        )
        detail.save()
        
        # Reload from database to ensure data is saved properly
        saved_detail = BillingReportDetail.objects.get(pk=detail.pk)
        assert saved_detail.service_breakdown == service_breakdown
        assert saved_detail.total_amount == Decimal('50.00')
    
    def test_billing_report_detail_total_amount_minimum(self):
        """Test that total_amount cannot be negative."""
        report = BillingReportFactory.create()
        order = OrderFactory.create()
        
        with pytest.raises(ValidationError):
            detail = BillingReportDetail(
                report=report,
                order=order,
                service_breakdown={"services": []},
                total_amount=Decimal('-10.00')
            )
            detail.save()
    
    def test_billing_report_detail_related_name(self):
        """Test the related_name for report->details relationship."""
        report = BillingReportFactory.create()
        
        # Create multiple details for the same report
        detail1 = BillingReportDetailFactory.create(report=report)
        detail2 = BillingReportDetailFactory.create(report=report)
        detail3 = BillingReportDetailFactory.create(report=report)
        
        # Access details from report
        assert report.details.count() == 3
        assert detail1 in report.details.all()
        assert detail2 in report.details.all()
        assert detail3 in report.details.all()
    
    def test_report_detail_delete_cascade(self):
        """Test that deleting a report cascades to details."""
        report = BillingReportFactory.create()
        detail = BillingReportDetailFactory.create(report=report)
        
        # Verify detail exists
        assert BillingReportDetail.objects.filter(pk=detail.pk).exists()
        
        # Delete report
        report.delete()
        
        # Verify detail is deleted
        assert not BillingReportDetail.objects.filter(pk=detail.pk).exists()