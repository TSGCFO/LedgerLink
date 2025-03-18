"""
Tests for the ReportRequestSerializer.
"""

import pytest
from datetime import timedelta
from django.utils import timezone

from billing.serializers import ReportRequestSerializer
from customers.models import Customer

pytestmark = pytest.mark.django_db

class TestReportRequestSerializer:
    """Test the ReportRequestSerializer."""
    
    def test_valid_data(self, billing_customer):
        """Test that valid data passes validation."""
        # Prepare data
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
        
        data = {
            'customer': billing_customer.id,
            'start_date': start_date,
            'end_date': end_date,
            'output_format': 'preview'  # One of the valid choices
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert serializer.is_valid(), f"Serializer validation errors: {serializer.errors}"
        
        # Check validated data
        assert serializer.validated_data['customer'] == billing_customer.id
        assert serializer.validated_data['start_date'] == start_date
        assert serializer.validated_data['end_date'] == end_date
        assert serializer.validated_data['output_format'] == 'preview'
    
    def test_start_date_after_end_date(self, billing_customer):
        """Test validation fails if start date is after end date."""
        # Prepare data with invalid date range
        start_date = timezone.now().date()
        end_date = start_date - timedelta(days=1)
        
        data = {
            'customer': billing_customer.id,
            'start_date': start_date,
            'end_date': end_date,
            'output_format': 'preview'
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'date_range' in serializer.errors
    
    def test_nonexistent_customer(self):
        """Test validation fails if customer does not exist."""
        # Use a non-existent customer ID
        data = {
            'customer': 9999,  # Non-existent ID
            'start_date': timezone.now().date() - timedelta(days=30),
            'end_date': timezone.now().date(),
            'output_format': 'preview'
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'customer' in serializer.errors
    
    def test_invalid_output_format(self, billing_customer):
        """Test validation fails with invalid output format."""
        data = {
            'customer': billing_customer.id,
            'start_date': timezone.now().date() - timedelta(days=30),
            'end_date': timezone.now().date(),
            'output_format': 'invalid_format'  # Invalid choice
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'output_format' in serializer.errors
    
    def test_missing_required_fields(self):
        """Test validation fails if required fields are missing."""
        # Empty data
        serializer = ReportRequestSerializer(data={})
        assert not serializer.is_valid()
        
        # Check all required fields are in errors
        required_fields = ['customer', 'start_date', 'end_date']
        for field in required_fields:
            assert field in serializer.errors
    
    def test_default_output_format(self, billing_customer):
        """Test default output format is 'preview'."""
        # Prepare data without output_format
        data = {
            'customer': billing_customer.id,
            'start_date': timezone.now().date() - timedelta(days=30),
            'end_date': timezone.now().date()
            # output_format is omitted
        }
        
        serializer = ReportRequestSerializer(data=data)
        assert serializer.is_valid(), f"Serializer validation errors: {serializer.errors}"
        
        # Check default value
        assert serializer.validated_data['output_format'] == 'preview'