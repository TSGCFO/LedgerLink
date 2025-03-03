"""
Unit tests for Customer models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Customer
from test_utils.factories import CustomerFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestCustomerModel:
    """Test cases for the Customer model."""

    def test_customer_creation(self, test_user):
        """Test that a customer can be created with valid data."""
        customer = CustomerFactory(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            created_by=test_user
        )
        assert customer.pk is not None
        assert customer.company_name == "Test Company"
        assert customer.contact_name == "John Doe"
        assert customer.contact_email == "john@example.com"
        assert customer.created_by == test_user

    def test_customer_str_representation(self, test_customer):
        """Test that the string representation of a customer is as expected."""
        expected_str = test_customer.company_name
        assert str(test_customer) == expected_str

    def test_customer_created_at_auto_populated(self, test_customer):
        """Test that created_at is automatically populated."""
        assert test_customer.created_at is not None

    def test_customer_updated_at_auto_populated(self, test_customer):
        """Test that updated_at is automatically populated."""
        assert test_customer.updated_at is not None

    def test_customer_email_validation(self, test_user):
        """Test that customer email validation works."""
        # Create with invalid email
        customer = Customer(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="invalid-email",
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            customer.full_clean()

    def test_duplicate_company_name_allowed(self, test_user):
        """Test that duplicate company names are allowed."""
        company_name = "Duplicate Company"
        CustomerFactory(company_name=company_name, created_by=test_user)
        # This should not raise an error
        CustomerFactory(company_name=company_name, created_by=test_user)

    def test_customer_without_created_by_raises_error(self):
        """Test that a customer cannot be created without a created_by user."""
        with pytest.raises(IntegrityError):
            CustomerFactory(created_by=None)

    def test_customer_ordering(self, test_user):
        """Test that customers are ordered by company_name by default."""
        # Create customers with names in non-alphabetical order
        CustomerFactory(company_name="Zebra Corp", created_by=test_user)
        CustomerFactory(company_name="Alpha Inc", created_by=test_user)
        CustomerFactory(company_name="Middle LLC", created_by=test_user)
        
        # Retrieve ordered customers
        customers = Customer.objects.all()
        
        # Check ordering
        assert customers[0].company_name == "Alpha Inc"
        assert customers[1].company_name == "Middle LLC"
        assert customers[2].company_name == "Zebra Corp"