"""
Tests for the BillingReportDetail model.
"""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from billing.models import BillingReportDetail

pytestmark = pytest.mark.django_db

class TestBillingReportDetailModel:
    """Test the BillingReportDetail model."""
    
    def test_create_billing_report_detail(self, basic_billing_report, billing_order):
        """Test creating a billing report detail."""
        service_breakdown = {
            "services": [
                {
                    "service_id": 1,
                    "service_name": "Shipping",
                    "amount": "10.50"
                }
            ]
        }
        
        detail = BillingReportDetail.objects.create(
            report=basic_billing_report,
            order=billing_order,
            service_breakdown=service_breakdown,
            total_amount=Decimal('10.50')
        )
        
        assert detail.report == basic_billing_report
        assert detail.order == billing_order
        assert detail.service_breakdown == service_breakdown
        assert detail.total_amount == Decimal('10.50')
    
    def test_string_representation(self, basic_billing_report, billing_order):
        """Test the string representation of a billing report detail."""
        detail = BillingReportDetail.objects.create(
            report=basic_billing_report,
            order=billing_order,
            service_breakdown={"services": []},
            total_amount=Decimal('10.50')
        )
        
        expected_str = f"Detail for {basic_billing_report} - Order {billing_order.transaction_id}"
        assert str(detail) == expected_str
    
    def test_negative_total_amount(self, basic_billing_report, billing_order):
        """Test validation fails if total amount is negative."""
        detail = BillingReportDetail(
            report=basic_billing_report,
            order=billing_order,
            service_breakdown={"services": []},
            total_amount=Decimal('-10.50')
        )
        
        with pytest.raises(ValidationError):
            detail.full_clean()
    
    def test_cascade_delete_from_report(self, basic_billing_report, billing_order):
        """Test detail gets deleted when parent report is deleted."""
        detail = BillingReportDetail.objects.create(
            report=basic_billing_report,
            order=billing_order,
            service_breakdown={"services": []},
            total_amount=Decimal('10.50')
        )
        
        # Get the detail ID for later verification
        detail_id = detail.id
        
        # Delete the parent report
        basic_billing_report.delete()
        
        # Verify the detail was deleted
        assert BillingReportDetail.objects.filter(id=detail_id).count() == 0
    
    def test_cascade_delete_from_order(self, basic_billing_report, billing_order):
        """Test detail gets deleted when related order is deleted."""
        detail = BillingReportDetail.objects.create(
            report=basic_billing_report,
            order=billing_order,
            service_breakdown={"services": []},
            total_amount=Decimal('10.50')
        )
        
        # Get the detail ID for later verification
        detail_id = detail.id
        
        # Delete the related order
        billing_order.delete()
        
        # Verify the detail was deleted
        assert BillingReportDetail.objects.filter(id=detail_id).count() == 0