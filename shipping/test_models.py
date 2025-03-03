"""
Unit tests for Shipping models.
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from shipping.models import CADShipping, USShipping
from test_utils.factories import OrderFactory, CustomerFactory, CADShippingFactory, USShippingFactory

pytestmark = pytest.mark.django_db


class TestCADShippingModel:
    """Test cases for the CADShipping model."""

    def test_cad_shipping_creation(self):
        """Test that a CAD shipping record can be created with valid data."""
        cad_shipping = CADShippingFactory()
        assert cad_shipping.pk is not None
        assert cad_shipping.transaction is not None
        assert cad_shipping.customer is not None
        assert cad_shipping.ship_to_name is not None
        assert cad_shipping.ship_to_postal_code is not None

    def test_cad_shipping_str_representation(self):
        """Test string representation of CAD shipping."""
        order = OrderFactory(order_number='CAD-TEST-123')
        cad_shipping = CADShippingFactory(transaction=order)
        
        expected_str = f"CAD Shipping for Order {order.pk}"
        assert str(cad_shipping) == expected_str

    def test_cad_shipping_requires_transaction(self):
        """Test that CAD shipping requires a transaction (Order)."""
        with pytest.raises(IntegrityError):
            CADShipping.objects.create(
                customer=CustomerFactory(),
                ship_to_name="Test Recipient",
                ship_to_postal_code="A1B 2C3"
            )

    def test_cad_shipping_requires_customer(self):
        """Test that CAD shipping requires a customer."""
        with pytest.raises(IntegrityError):
            CADShipping.objects.create(
                transaction=OrderFactory(),
                ship_to_name="Test Recipient",
                ship_to_postal_code="A1B 2C3",
                customer=None
            )

    def test_cad_shipping_numeric_fields(self):
        """Test numeric fields in CAD shipping."""
        cad_shipping = CADShippingFactory(
            pre_tax_shipping_charge=Decimal('10.50'),
            tax1amount=Decimal('1.37'),
            weight=Decimal('5.25'),
            box_length=Decimal('12.0'),
            box_width=Decimal('8.0'),
            box_height=Decimal('6.0')
        )
        
        # Reload from database to ensure data was saved correctly
        cad_shipping.refresh_from_db()
        
        assert cad_shipping.pre_tax_shipping_charge == Decimal('10.50')
        assert cad_shipping.tax1amount == Decimal('1.37')
        assert cad_shipping.weight == Decimal('5.25')
        assert cad_shipping.box_length == Decimal('12.0')
        assert cad_shipping.box_width == Decimal('8.0')
        assert cad_shipping.box_height == Decimal('6.0')

    def test_cad_shipping_unique_transaction(self):
        """Test that a transaction can have only one CAD shipping record."""
        order = OrderFactory()
        CADShippingFactory(transaction=order)
        
        # Attempting to create another CAD shipping record for the same order
        with pytest.raises(IntegrityError):
            CADShippingFactory(transaction=order)


class TestUSShippingModel:
    """Test cases for the USShipping model."""

    def test_us_shipping_creation(self):
        """Test that a US shipping record can be created with valid data."""
        us_shipping = USShippingFactory()
        assert us_shipping.pk is not None
        assert us_shipping.transaction is not None
        assert us_shipping.customer is not None
        assert us_shipping.ship_to_name is not None
        assert us_shipping.ship_to_zip is not None

    def test_us_shipping_str_representation(self):
        """Test string representation of US shipping."""
        order = OrderFactory(order_number='US-TEST-456')
        us_shipping = USShippingFactory(transaction=order)
        
        expected_str = f"US Shipping for Order {order.pk}"
        assert str(us_shipping) == expected_str

    def test_us_shipping_requires_transaction(self):
        """Test that US shipping requires a transaction (Order)."""
        with pytest.raises(IntegrityError):
            USShipping.objects.create(
                customer=CustomerFactory(),
                ship_to_name="Test Recipient",
                ship_to_zip="12345"
            )

    def test_us_shipping_requires_customer(self):
        """Test that US shipping requires a customer."""
        with pytest.raises(IntegrityError):
            USShipping.objects.create(
                transaction=OrderFactory(),
                ship_to_name="Test Recipient",
                ship_to_zip="12345",
                customer=None
            )

    def test_us_shipping_numeric_fields(self):
        """Test numeric fields in US shipping."""
        us_shipping = USShippingFactory(
            weight_lbs=Decimal('3.75'),
            length_in=Decimal('10.0'),
            width_in=Decimal('7.0'),
            height_in=Decimal('5.0'),
            base_chg=Decimal('15.99'),
            rate=Decimal('1.25')
        )
        
        # Reload from database to ensure data was saved correctly
        us_shipping.refresh_from_db()
        
        assert us_shipping.weight_lbs == Decimal('3.75')
        assert us_shipping.length_in == Decimal('10.0')
        assert us_shipping.width_in == Decimal('7.0')
        assert us_shipping.height_in == Decimal('5.0')
        assert us_shipping.base_chg == Decimal('15.99')
        assert us_shipping.rate == Decimal('1.25')

    def test_us_shipping_status_fields(self):
        """Test status fields in US shipping."""
        us_shipping = USShippingFactory(
            current_status='in_transit',
            delivery_status='attempted'
        )
        
        # Reload from database to ensure data was saved correctly
        us_shipping.refresh_from_db()
        
        assert us_shipping.current_status == 'in_transit'
        assert us_shipping.delivery_status == 'attempted'

    def test_us_shipping_date_fields(self):
        """Test date fields in US shipping."""
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        us_shipping = USShippingFactory(
            ship_date=yesterday,
            first_attempt_date=today,
            delivery_date=None,
            days_to_first_deliver=1
        )
        
        # Reload from database to ensure data was saved correctly
        us_shipping.refresh_from_db()
        
        assert us_shipping.ship_date == yesterday
        assert us_shipping.first_attempt_date == today
        assert us_shipping.delivery_date is None
        assert us_shipping.days_to_first_deliver == 1

    def test_us_shipping_unique_transaction(self):
        """Test that a transaction can have only one US shipping record."""
        order = OrderFactory()
        USShippingFactory(transaction=order)
        
        # Attempting to create another US shipping record for the same order
        with pytest.raises(IntegrityError):
            USShippingFactory(transaction=order)