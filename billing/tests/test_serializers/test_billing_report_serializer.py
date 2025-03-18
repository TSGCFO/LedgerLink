"""
Tests for the BillingReportSerializer.
"""

import pytest
from datetime import timedelta
from django.utils import timezone

from billing.serializers import BillingReportSerializer

pytestmark = pytest.mark.django_db

class TestBillingReportSerializer:
    """Test the BillingReportSerializer."""
    
    def test_serializer_contains_expected_fields(self, basic_billing_report):
        """Test the serializer contains the expected fields."""
        serializer = BillingReportSerializer(basic_billing_report)
        expected_fields = [
            'id', 'customer', 'customer_name', 'start_date', 'end_date',
            'generated_at', 'total_amount', 'created_by', 'created_by_name',
            'updated_by', 'updated_by_name', 'created_at', 'updated_at'
        ]
        assert all(field in serializer.data for field in expected_fields)
    
    def test_customer_name_method(self, basic_billing_report):
        """Test the customer_name method returns the correct value."""
        serializer = BillingReportSerializer(basic_billing_report)
        assert serializer.data['customer_name'] == basic_billing_report.customer.company_name
    
    def test_created_by_name_method(self, basic_billing_report):
        """Test the created_by_name method returns the correct value."""
        # Add a full name to the user if not already set
        if not basic_billing_report.created_by.first_name:
            basic_billing_report.created_by.first_name = "Test"
            basic_billing_report.created_by.last_name = "User"
            basic_billing_report.created_by.save()
            
        serializer = BillingReportSerializer(basic_billing_report)
        expected_name = basic_billing_report.created_by.get_full_name()
        assert serializer.data['created_by_name'] == expected_name
    
    def test_updated_by_name_method(self, basic_billing_report):
        """Test the updated_by_name method returns the correct value."""
        # Add a full name to the user if not already set
        if not basic_billing_report.updated_by.first_name:
            basic_billing_report.updated_by.first_name = "Test"
            basic_billing_report.updated_by.last_name = "User"
            basic_billing_report.updated_by.save()
            
        serializer = BillingReportSerializer(basic_billing_report)
        expected_name = basic_billing_report.updated_by.get_full_name()
        assert serializer.data['updated_by_name'] == expected_name
    
    def test_read_only_fields(self, billing_customer, billing_user):
        """Test that read-only fields are respected."""
        # Prepare data for serializer
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
        
        data = {
            'customer': billing_customer.id,
            'start_date': start_date,
            'end_date': end_date,
            'total_amount': '100.00',
            # Attempt to set read-only fields
            'id': 9999,
            'generated_at': timezone.now(),
            'created_by': billing_user.id,
            'updated_by': billing_user.id,
            'created_at': timezone.now(),
            'updated_at': timezone.now()
        }
        
        serializer = BillingReportSerializer(data=data)
        assert serializer.is_valid(), f"Serializer validation errors: {serializer.errors}"
        
        # Verify the read-only fields were not validated in the serializer
        assert 'id' not in serializer.validated_data
        assert 'generated_at' not in serializer.validated_data
        assert 'created_by' not in serializer.validated_data
        assert 'updated_by' not in serializer.validated_data
        assert 'created_at' not in serializer.validated_data
        assert 'updated_at' not in serializer.validated_data