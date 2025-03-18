# billing/tests/test_serializers/test_serializers.py

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from billing.serializers import BillingReportSerializer, ReportRequestSerializer
from billing.tests.factories import BillingReportFactory, UserFactory
from customers.tests.factories import CustomerFactory

pytestmark = pytest.mark.django_db

class TestBillingReportSerializer:
    """
    Test cases for the BillingReportSerializer.
    """
    
    def test_serialization(self):
        """Test serializing a billing report object."""
        user = UserFactory.create(first_name="John", last_name="Doe")
        report = BillingReportFactory.create(
            created_by=user,
            updated_by=user
        )
        serializer = BillingReportSerializer(report)
        data = serializer.data
        
        # Test that key fields are included in serialization
        assert data['id'] == report.pk
        assert data['customer'] == report.customer.id
        assert data['customer_name'] == report.customer.company_name
        assert data['start_date'] == report.start_date.isoformat()
        assert data['end_date'] == report.end_date.isoformat()
        assert data['total_amount'] == str(report.total_amount)
        assert 'generated_at' in data
        assert data['created_by'] == user.id
        assert data['created_by_name'] == "John Doe"
        assert data['updated_by'] == user.id
        assert data['updated_by_name'] == "John Doe"
    
    def test_get_customer_name(self):
        """Test the get_customer_name method."""
        customer = CustomerFactory.create(company_name="Test Company LLC")
        report = BillingReportFactory.create(customer=customer)
        serializer = BillingReportSerializer(report)
        assert serializer.data['customer_name'] == "Test Company LLC"
    
    def test_get_created_by_name_when_null(self):
        """Test the get_created_by_name method when created_by is None."""
        report = BillingReportFactory.create(created_by=None)
        serializer = BillingReportSerializer(report)
        assert serializer.data['created_by_name'] is None
    
    def test_get_updated_by_name_when_null(self):
        """Test the get_updated_by_name method when updated_by is None."""
        report = BillingReportFactory.create(updated_by=None)
        serializer = BillingReportSerializer(report)
        assert serializer.data['updated_by_name'] is None
    
    def test_read_only_fields(self):
        """Test that certain fields are read-only."""
        customer = CustomerFactory.create()
        report = BillingReportFactory.create(customer=customer)
        
        data = {
            'id': 999,
            'customer': customer.id,
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'total_amount': '500.00',
            'generated_at': '2023-02-01T12:00:00Z',
            'created_by': 999,
            'updated_by': 999,
            'created_at': '2023-02-01T12:00:00Z',
            'updated_at': '2023-02-01T12:00:00Z'
        }
        
        serializer = BillingReportSerializer(report, data=data)
        assert serializer.is_valid()
        
        # Read-only fields should not be updated
        updated_report = serializer.save()
        assert updated_report.id == report.id  # not 999
        assert updated_report.generated_at == report.generated_at  # not changed
        assert updated_report.created_by == report.created_by  # not changed
        assert updated_report.updated_by == report.updated_by  # not changed
        assert updated_report.created_at == report.created_at  # not changed
        # updated_at might change due to auto_now, so we don't check it


class TestReportRequestSerializer:
    """
    Test cases for the ReportRequestSerializer.
    """
    
    def test_valid_data(self):
        """Test validation with valid data."""
        customer = CustomerFactory.create()
        
        data = {
            'customer': customer.id,
            'start_date': (timezone.now().date() - timedelta(days=30)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'preview'
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['customer'] == customer.id
        assert serializer.validated_data['output_format'] == 'preview'
    
    def test_validate_date_order(self):
        """Test validation of start_date before end_date."""
        customer = CustomerFactory.create()
        today = timezone.now().date()
        
        data = {
            'customer': customer.id,
            'start_date': today.isoformat(),
            'end_date': (today - timedelta(days=1)).isoformat(),
            'output_format': 'preview'
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'date_range' in serializer.errors
    
    def test_validate_customer_exists(self):
        """Test validation that customer exists."""
        non_existent_id = 99999
        
        data = {
            'customer': non_existent_id,
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'output_format': 'preview'
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'customer' in serializer.errors
    
    def test_default_output_format(self):
        """Test the default output_format value."""
        customer = CustomerFactory.create()
        
        data = {
            'customer': customer.id,
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
            # No output_format specified
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['output_format'] == 'preview'
    
    def test_output_format_choices(self):
        """Test validation of output_format choices."""
        customer = CustomerFactory.create()
        
        data = {
            'customer': customer.id,
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'output_format': 'invalid_format'
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'output_format' in serializer.errors