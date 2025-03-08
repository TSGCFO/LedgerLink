# shipping/tests/test_serializers.py

import pytest
from datetime import datetime, timedelta
from rest_framework.exceptions import ValidationError
from shipping.serializers import CADShippingSerializer, USShippingSerializer
from .factories import CADShippingFactory, USShippingFactory
from orders.tests.factories import OrderFactory
from customers.tests.factories import CustomerFactory

pytestmark = pytest.mark.django_db

class TestCADShippingSerializer:
    """
    Test cases for the CADShippingSerializer.
    """
    
    def test_serialization(self):
        """Test serializing a CAD shipping object."""
        shipping = CADShippingFactory.create()
        serializer = CADShippingSerializer(shipping)
        data = serializer.data
        
        # Test that key fields are included in serialization
        assert data['transaction'] == shipping.transaction_id
        assert data['tracking_number'] == shipping.tracking_number
        assert data['ship_to_name'] == shipping.ship_to_name
        assert data['pre_tax_shipping_charge'] == str(shipping.pre_tax_shipping_charge)
        assert 'order_details' in data
        assert 'customer_details' in data
        assert 'total_tax' in data
        assert 'total_charges' in data
    
    def test_get_total_tax(self):
        """Test the get_total_tax method."""
        shipping = CADShippingFactory.create(
            tax1amount=10.00,
            tax2amount=5.50,
            tax3amount=2.25
        )
        serializer = CADShippingSerializer(shipping)
        assert serializer.data['total_tax'] == '17.75'  # 10.00 + 5.50 + 2.25 = 17.75
    
    def test_get_total_charges(self):
        """Test the get_total_charges method."""
        shipping = CADShippingFactory.create(
            pre_tax_shipping_charge=50.00,
            tax1amount=5.00,
            tax2amount=2.50,
            tax3amount=0.00,
            fuel_surcharge=7.50
        )
        serializer = CADShippingSerializer(shipping)
        assert serializer.data['total_charges'] == '65.00'  # 50.00 + 5.00 + 2.50 + 0.00 + 7.50 = 65.00
    
    def test_validate_required_shipping_fields(self):
        """Test validation of required shipping address fields."""
        order = OrderFactory.create()
        customer = order.customer
        
        # Missing some required shipping fields (should fail)
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'Test Name',
            'ship_to_address_1': '123 Test St',
            # Missing ship_to_city, ship_to_state, ship_to_postal_code
        }
        
        serializer = CADShippingSerializer(data=data)
        assert not serializer.is_valid()
        assert 'shipping' in serializer.errors
    
    def test_validate_success(self):
        """Test successful validation of all required fields."""
        order = OrderFactory.create()
        customer = order.customer
        
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'Test Name',
            'ship_to_address_1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_postal_code': 'A1B 2C3',
            'tracking_number': 'TRACK-1234567890',
            'pre_tax_shipping_charge': '25.50',
            'carrier': 'FedEx'
        }
        
        serializer = CADShippingSerializer(data=data)
        assert serializer.is_valid()
    
    def test_create(self):
        """Test creating a CAD shipping record from serializer."""
        order = OrderFactory.create()
        customer = order.customer
        
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'Test Name',
            'ship_to_address_1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_postal_code': 'A1B 2C3',
            'tracking_number': 'TRACK-1234567890',
            'pre_tax_shipping_charge': '25.50',
            'carrier': 'FedEx'
        }
        
        serializer = CADShippingSerializer(data=data)
        assert serializer.is_valid()
        shipping = serializer.save()
        
        assert shipping.transaction_id == order.id
        assert shipping.customer_id == customer.id
        assert shipping.ship_to_name == 'Test Name'
        assert shipping.tracking_number == 'TRACK-1234567890'
        assert float(shipping.pre_tax_shipping_charge) == 25.50
        assert shipping.carrier == 'FedEx'


class TestUSShippingSerializer:
    """
    Test cases for the USShippingSerializer.
    """
    
    def test_serialization(self):
        """Test serializing a US shipping object."""
        shipping = USShippingFactory.create()
        serializer = USShippingSerializer(shipping)
        data = serializer.data
        
        # Test that key fields are included in serialization
        assert data['transaction'] == shipping.transaction_id
        assert data['tracking_number'] == shipping.tracking_number
        assert data['ship_to_name'] == shipping.ship_to_name
        assert 'order_details' in data
        assert 'customer_details' in data
        assert 'total_charges' in data
        assert 'delivery_days' in data
    
    def test_get_total_charges(self):
        """Test the get_total_charges method."""
        shipping = USShippingFactory.create(
            base_chg=50.00,
            carrier_peak_charge=5.00,
            wizmo_peak_charge=2.50,
            accessorial_charges=7.75,
            hst=6.50,
            gst=3.25
        )
        serializer = USShippingSerializer(shipping)
        assert serializer.data['total_charges'] == '75.00'  # 50.00 + 5.00 + 2.50 + 7.75 + 6.50 + 3.25 = 75.00
    
    def test_get_delivery_days_from_field(self):
        """Test the get_delivery_days method when days_to_first_deliver is set."""
        shipping = USShippingFactory.create(days_to_first_deliver=3)
        serializer = USShippingSerializer(shipping)
        assert serializer.data['delivery_days'] == 3
    
    def test_get_delivery_days_from_dates(self):
        """Test the get_delivery_days method when calculated from dates."""
        ship_date = datetime.now().date() - timedelta(days=5)
        delivery_date = ship_date + timedelta(days=3)
        
        shipping = USShippingFactory.create(
            ship_date=ship_date,
            delivery_date=delivery_date,
            days_to_first_deliver=None
        )
        serializer = USShippingSerializer(shipping)
        assert serializer.data['delivery_days'] == 3
    
    def test_validate_required_shipping_fields(self):
        """Test validation of required shipping address fields."""
        order = OrderFactory.create()
        customer = order.customer
        
        # Missing some required shipping fields (should fail)
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'Test Name',
            'ship_to_address_1': '123 Test St',
            # Missing ship_to_city, ship_to_state, ship_to_zip
        }
        
        serializer = USShippingSerializer(data=data)
        assert not serializer.is_valid()
        assert 'shipping' in serializer.errors
    
    def test_validate_dates(self):
        """Test validation of shipping dates."""
        order = OrderFactory.create()
        customer = order.customer
        
        # Delivery date before ship date (should fail)
        ship_date = datetime.now().date()
        delivery_date = ship_date - timedelta(days=1)
        
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_date': ship_date,
            'delivery_date': delivery_date
        }
        
        serializer = USShippingSerializer(data=data)
        assert not serializer.is_valid()
        assert 'delivery_date' in serializer.errors
    
    def test_validate_first_attempt_date(self):
        """Test validation of first attempt date."""
        order = OrderFactory.create()
        customer = order.customer
        
        # First attempt date before ship date (should fail)
        ship_date = datetime.now().date()
        first_attempt_date = ship_date - timedelta(days=1)
        
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_date': ship_date,
            'first_attempt_date': first_attempt_date
        }
        
        serializer = USShippingSerializer(data=data)
        assert not serializer.is_valid()
        assert 'first_attempt_date' in serializer.errors
    
    def test_validate_success(self):
        """Test successful validation of all fields."""
        order = OrderFactory.create()
        customer = order.customer
        
        ship_date = datetime.now().date()
        first_attempt_date = ship_date + timedelta(days=1)
        delivery_date = ship_date + timedelta(days=2)
        
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'US Test Name',
            'ship_to_address_1': '456 Test Ave',
            'ship_to_city': 'Test City',
            'ship_to_state': 'CA',
            'ship_to_zip': '90210',
            'tracking_number': 'US-TRACK-1234567890',
            'ship_date': ship_date,
            'first_attempt_date': first_attempt_date,
            'delivery_date': delivery_date,
            'service_name': 'Express'
        }
        
        serializer = USShippingSerializer(data=data)
        assert serializer.is_valid()
    
    def test_create(self):
        """Test creating a US shipping record from serializer."""
        order = OrderFactory.create()
        customer = order.customer
        
        ship_date = datetime.now().date()
        first_attempt_date = ship_date + timedelta(days=1)
        delivery_date = ship_date + timedelta(days=2)
        
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'US Test Name',
            'ship_to_address_1': '456 Test Ave',
            'ship_to_city': 'Test City',
            'ship_to_state': 'CA',
            'ship_to_zip': '90210',
            'tracking_number': 'US-TRACK-1234567890',
            'ship_date': ship_date,
            'first_attempt_date': first_attempt_date,
            'delivery_date': delivery_date,
            'service_name': 'Express'
        }
        
        serializer = USShippingSerializer(data=data)
        assert serializer.is_valid()
        shipping = serializer.save()
        
        assert shipping.transaction_id == order.id
        assert shipping.customer_id == customer.id
        assert shipping.ship_to_name == 'US Test Name'
        assert shipping.tracking_number == 'US-TRACK-1234567890'
        assert shipping.ship_date == ship_date
        assert shipping.first_attempt_date == first_attempt_date
        assert shipping.delivery_date == delivery_date
        assert shipping.service_name == 'Express'