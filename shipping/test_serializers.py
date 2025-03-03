"""
Tests for Shipping serializers.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from shipping.serializers import CADShippingSerializer, USShippingSerializer
from test_utils.factories import OrderFactory, CustomerFactory, CADShippingFactory, USShippingFactory

pytestmark = pytest.mark.django_db


class TestCADShippingSerializer:
    """Tests for the CADShippingSerializer."""

    def test_serialization(self):
        """Test serializing a CAD shipping instance."""
        # Create a shipping instance with tax and charge values
        cad_shipping = CADShippingFactory(
            pre_tax_shipping_charge=Decimal('25.99'),
            tax1type='GST',
            tax1amount=Decimal('1.30'),
            tax2type='PST',
            tax2amount=Decimal('2.08'),
            fuel_surcharge=Decimal('3.50')
        )
        
        serializer = CADShippingSerializer(cad_shipping)
        data = serializer.data
        
        # Check basic fields
        assert data['transaction'] == cad_shipping.transaction_id
        assert data['customer'] == cad_shipping.customer_id
        assert data['ship_to_name'] == cad_shipping.ship_to_name
        assert data['carrier'] == cad_shipping.carrier
        
        # Check calculated fields
        assert Decimal(data['total_tax']) == Decimal('3.38')  # 1.30 + 2.08
        assert Decimal(data['total_charges']) == Decimal('32.87')  # 25.99 + 3.50 + 3.38

    def test_serialize_with_nested_fields(self):
        """Test that serializer includes nested order and customer details."""
        order = OrderFactory(order_number='CAD-TEST-123')
        customer = order.customer
        cad_shipping = CADShippingFactory(transaction=order, customer=customer)
        
        serializer = CADShippingSerializer(cad_shipping)
        data = serializer.data
        
        # Verify nested serialization
        assert 'order_details' in data
        assert data['order_details']['order_number'] == 'CAD-TEST-123'
        
        assert 'customer_details' in data
        assert data['customer_details']['company_name'] == customer.company_name

    def test_validate_shipping_fields_success(self):
        """Test validation succeeds with all required shipping fields."""
        data = {
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_postal_code': 'A1B 2C3'
        }
        
        serializer = CADShippingSerializer()
        validated_data = serializer.validate(data)
        
        # Should not raise ValidationError and return unchanged data
        assert validated_data == data

    def test_validate_shipping_fields_missing(self):
        """Test validation fails with missing required shipping fields."""
        # Missing ship_to_city and ship_to_state
        data = {
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Test St',
            'ship_to_postal_code': 'A1B 2C3'
        }
        
        serializer = CADShippingSerializer()
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate(data)
        
        # Check error details
        error_detail = excinfo.value.detail
        assert 'shipping' in error_detail
        assert 'Missing required shipping fields' in error_detail['shipping'][0]
        assert 'ship_to_city' in error_detail['shipping'][0]
        assert 'ship_to_state' in error_detail['shipping'][0]

    def test_validate_no_shipping_fields(self):
        """Test validation passes when no shipping fields are provided."""
        # No shipping fields at all (might be valid for a partial update)
        data = {
            'carrier': 'Canada Post',
            'tracking_number': 'CAD12345'
        }
        
        serializer = CADShippingSerializer()
        validated_data = serializer.validate(data)
        
        # Should not raise ValidationError and return unchanged data
        assert validated_data == data

    def test_get_total_tax_with_nulls(self):
        """Test get_total_tax handles null tax values."""
        cad_shipping = CADShippingFactory(
            tax1amount=None,
            tax2amount=None,
            tax3amount=None
        )
        
        serializer = CADShippingSerializer()
        total_tax = serializer.get_total_tax(cad_shipping)
        
        assert total_tax == 0

    def test_get_total_charges_with_nulls(self):
        """Test get_total_charges handles null charge values."""
        cad_shipping = CADShippingFactory(
            pre_tax_shipping_charge=None,
            tax1amount=None,
            tax2amount=None,
            tax3amount=None,
            fuel_surcharge=None
        )
        
        serializer = CADShippingSerializer()
        total_charges = serializer.get_total_charges(cad_shipping)
        
        assert total_charges == 0


class TestUSShippingSerializer:
    """Tests for the USShippingSerializer."""

    def test_serialization(self):
        """Test serializing a US shipping instance."""
        # Create a shipping instance with charge values
        us_shipping = USShippingFactory(
            base_chg=Decimal('18.50'),
            carrier_peak_charge=Decimal('2.25'),
            wizmo_peak_charge=Decimal('1.75'),
            accessorial_charges=Decimal('3.00'),
            hst=Decimal('2.10'),
            gst=Decimal('0.80')
        )
        
        serializer = USShippingSerializer(us_shipping)
        data = serializer.data
        
        # Check basic fields
        assert data['transaction'] == us_shipping.transaction_id
        assert data['customer'] == us_shipping.customer_id
        assert data['ship_to_name'] == us_shipping.ship_to_name
        assert data['service_name'] == us_shipping.service_name
        
        # Check calculated fields
        assert Decimal(data['total_charges']) == Decimal('28.40')  # Sum of all charges

    def test_serialize_with_nested_fields(self):
        """Test that serializer includes nested order and customer details."""
        order = OrderFactory(order_number='US-TEST-456')
        customer = order.customer
        us_shipping = USShippingFactory(transaction=order, customer=customer)
        
        serializer = USShippingSerializer(us_shipping)
        data = serializer.data
        
        # Verify nested serialization
        assert 'order_details' in data
        assert data['order_details']['order_number'] == 'US-TEST-456'
        
        assert 'customer_details' in data
        assert data['customer_details']['company_name'] == customer.company_name

    def test_validate_shipping_fields_success(self):
        """Test validation succeeds with all required shipping fields."""
        data = {
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345'
        }
        
        serializer = USShippingSerializer()
        validated_data = serializer.validate(data)
        
        # Should not raise ValidationError and return unchanged data
        assert validated_data == data

    def test_validate_shipping_fields_missing(self):
        """Test validation fails with missing required shipping fields."""
        # Missing ship_to_city and ship_to_address_1
        data = {
            'ship_to_name': 'Test Recipient',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345'
        }
        
        serializer = USShippingSerializer()
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate(data)
        
        # Check error details
        error_detail = excinfo.value.detail
        assert 'shipping' in error_detail
        assert 'Missing required shipping fields' in error_detail['shipping'][0]
        assert 'ship_to_address_1' in error_detail['shipping'][0]
        assert 'ship_to_city' in error_detail['shipping'][0]

    def test_validate_dates_valid(self):
        """Test date validation passes with valid dates."""
        today = date.today()
        ship_date = today - timedelta(days=5)
        delivery_date = today - timedelta(days=2)
        
        data = {
            'ship_date': ship_date,
            'delivery_date': delivery_date
        }
        
        serializer = USShippingSerializer()
        validated_data = serializer.validate(data)
        
        # Should not raise ValidationError and return unchanged data
        assert validated_data == data

    def test_validate_delivery_before_ship_date(self):
        """Test validation fails when delivery date is before ship date."""
        today = date.today()
        ship_date = today
        delivery_date = today - timedelta(days=1)  # Before ship date
        
        data = {
            'ship_date': ship_date,
            'delivery_date': delivery_date
        }
        
        serializer = USShippingSerializer()
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate(data)
        
        # Check error details
        error_detail = excinfo.value.detail
        assert 'delivery_date' in error_detail
        assert 'cannot be earlier than ship date' in error_detail['delivery_date'][0]

    def test_validate_first_attempt_before_ship_date(self):
        """Test validation fails when first attempt date is before ship date."""
        today = date.today()
        ship_date = today
        first_attempt_date = today - timedelta(days=1)  # Before ship date
        
        data = {
            'ship_date': ship_date,
            'first_attempt_date': first_attempt_date
        }
        
        serializer = USShippingSerializer()
        
        with pytest.raises(ValidationError) as excinfo:
            serializer.validate(data)
        
        # Check error details
        error_detail = excinfo.value.detail
        assert 'first_attempt_date' in error_detail
        assert 'cannot be earlier than ship date' in error_detail['first_attempt_date'][0]

    def test_get_delivery_days_from_days_field(self):
        """Test get_delivery_days uses days_to_first_deliver if available."""
        us_shipping = USShippingFactory(
            days_to_first_deliver=3,
            ship_date=date.today() - timedelta(days=5),
            delivery_date=date.today() - timedelta(days=1)  # 4 days difference
        )
        
        serializer = USShippingSerializer()
        delivery_days = serializer.get_delivery_days(us_shipping)
        
        # Should use days_to_first_deliver value
        assert delivery_days == 3

    def test_get_delivery_days_calculated(self):
        """Test get_delivery_days calculates from dates if days_to_first_deliver is None."""
        ship_date = date.today() - timedelta(days=4)
        delivery_date = date.today() - timedelta(days=1)
        
        us_shipping = USShippingFactory(
            days_to_first_deliver=None,
            ship_date=ship_date,
            delivery_date=delivery_date
        )
        
        serializer = USShippingSerializer()
        delivery_days = serializer.get_delivery_days(us_shipping)
        
        # Should calculate 3 days between ship_date and delivery_date
        assert delivery_days == 3

    def test_get_delivery_days_none(self):
        """Test get_delivery_days returns None if dates are missing."""
        us_shipping = USShippingFactory(
            days_to_first_deliver=None,
            ship_date=None,
            delivery_date=None
        )
        
        serializer = USShippingSerializer()
        delivery_days = serializer.get_delivery_days(us_shipping)
        
        # Should return None when data is missing
        assert delivery_days is None