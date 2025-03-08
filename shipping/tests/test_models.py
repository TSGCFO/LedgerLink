# shipping/tests/test_models.py

import pytest
from datetime import datetime, timedelta
from django.db import IntegrityError
from shipping.models import CADShipping, USShipping
from orders.models import Order
from .factories import CADShippingFactory, USShippingFactory
from orders.tests.factories import OrderFactory

pytestmark = pytest.mark.django_db

class TestCADShippingModel:
    """
    Test cases for the CADShipping model.
    """
    
    def test_create_cad_shipping(self):
        """Test creating a CAD shipping record."""
        shipping = CADShippingFactory.create()
        assert shipping.pk is not None
        assert CADShipping.objects.count() == 1
        assert CADShipping.objects.first().tracking_number == shipping.tracking_number
    
    def test_cad_shipping_str_method(self):
        """Test the string representation of a CAD shipping record."""
        order = OrderFactory.create(order_number="ORD-12345")
        shipping = CADShippingFactory.create(transaction=order)
        assert str(shipping) == f"CAD Shipping for Order {order.id}"
    
    def test_cad_shipping_transaction_unique(self):
        """Test that transaction (order) must be unique."""
        order = OrderFactory.create()
        CADShippingFactory.create(transaction=order)
        
        # Attempting to create another shipping record with the same order should fail
        with pytest.raises(IntegrityError):
            CADShippingFactory.create(transaction=order)
    
    def test_cad_shipping_transaction_cascade_delete(self):
        """Test that deleting an order cascades to the shipping record."""
        shipping = CADShippingFactory.create()
        transaction_id = shipping.transaction_id
        
        # Delete the order
        Order.objects.get(id=transaction_id).delete()
        
        # Verify shipping record is deleted
        assert not CADShipping.objects.filter(transaction_id=transaction_id).exists()
    
    def test_cad_shipping_customer_fields(self):
        """Test shipping record with customer details."""
        customer = shipping = CADShippingFactory.create()
        assert shipping.customer is not None
        assert shipping.customer == shipping.transaction.customer
    
    def test_cad_shipping_address_fields(self):
        """Test shipping record with address fields."""
        shipping = CADShippingFactory.create(
            ship_to_name="Test Name",
            ship_to_address_1="123 Test St",
            ship_to_address_2="Apt 4B",
            shiptoaddress3="Floor 2",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_country="CA",
            ship_to_postal_code="A1B 2C3"
        )
        
        # Retrieve from database to verify persistence
        shipping_db = CADShipping.objects.get(transaction_id=shipping.transaction_id)
        assert shipping_db.ship_to_name == "Test Name"
        assert shipping_db.ship_to_address_1 == "123 Test St"
        assert shipping_db.ship_to_address_2 == "Apt 4B"
        assert shipping_db.shiptoaddress3 == "Floor 2"
        assert shipping_db.ship_to_city == "Test City"
        assert shipping_db.ship_to_state == "TS"
        assert shipping_db.ship_to_country == "CA"
        assert shipping_db.ship_to_postal_code == "A1B 2C3"
    
    def test_cad_shipping_financial_fields(self):
        """Test shipping record with financial fields."""
        shipping = CADShippingFactory.create(
            pre_tax_shipping_charge=50.25,
            tax1type="GST",
            tax1amount=2.51,
            tax2type="PST",
            tax2amount=4.02,
            tax3type="HST",
            tax3amount=0.00,
            fuel_surcharge=3.75
        )
        
        # Retrieve from database to verify persistence
        shipping_db = CADShipping.objects.get(transaction_id=shipping.transaction_id)
        assert shipping_db.pre_tax_shipping_charge == 50.25
        assert shipping_db.tax1type == "GST"
        assert shipping_db.tax1amount == 2.51
        assert shipping_db.tax2type == "PST"
        assert shipping_db.tax2amount == 4.02
        assert shipping_db.tax3type == "HST"
        assert shipping_db.tax3amount == 0.00
        assert shipping_db.fuel_surcharge == 3.75


class TestUSShippingModel:
    """
    Test cases for the USShipping model.
    """
    
    def test_create_us_shipping(self):
        """Test creating a US shipping record."""
        shipping = USShippingFactory.create()
        assert shipping.pk is not None
        assert USShipping.objects.count() == 1
        assert USShipping.objects.first().tracking_number == shipping.tracking_number
    
    def test_us_shipping_str_method(self):
        """Test the string representation of a US shipping record."""
        order = OrderFactory.create(order_number="ORD-67890")
        shipping = USShippingFactory.create(transaction=order)
        assert str(shipping) == f"US Shipping for Order {order.id}"
    
    def test_us_shipping_transaction_unique(self):
        """Test that transaction (order) must be unique."""
        order = OrderFactory.create()
        USShippingFactory.create(transaction=order)
        
        # Attempting to create another shipping record with the same order should fail
        with pytest.raises(IntegrityError):
            USShippingFactory.create(transaction=order)
    
    def test_us_shipping_transaction_cascade_delete(self):
        """Test that deleting an order cascades to the shipping record."""
        shipping = USShippingFactory.create()
        transaction_id = shipping.transaction_id
        
        # Delete the order
        Order.objects.get(id=transaction_id).delete()
        
        # Verify shipping record is deleted
        assert not USShipping.objects.filter(transaction_id=transaction_id).exists()
    
    def test_us_shipping_address_fields(self):
        """Test shipping record with address fields."""
        shipping = USShippingFactory.create(
            ship_to_name="US Test Name",
            ship_to_address_1="456 Test Ave",
            ship_to_address_2="Suite 101",
            ship_to_city="Test City",
            ship_to_state="CA",
            ship_to_zip="90210",
            ship_to_country_code="US"
        )
        
        # Retrieve from database to verify persistence
        shipping_db = USShipping.objects.get(transaction_id=shipping.transaction_id)
        assert shipping_db.ship_to_name == "US Test Name"
        assert shipping_db.ship_to_address_1 == "456 Test Ave"
        assert shipping_db.ship_to_address_2 == "Suite 101"
        assert shipping_db.ship_to_city == "Test City"
        assert shipping_db.ship_to_state == "CA"
        assert shipping_db.ship_to_zip == "90210"
        assert shipping_db.ship_to_country_code == "US"
    
    def test_us_shipping_financial_fields(self):
        """Test shipping record with financial fields."""
        shipping = USShippingFactory.create(
            base_chg=45.50,
            carrier_peak_charge=5.25,
            wizmo_peak_charge=2.00,
            accessorial_charges=3.75,
            rate=40.00,
            hst=5.99,
            gst=2.50
        )
        
        # Retrieve from database to verify persistence
        shipping_db = USShipping.objects.get(transaction_id=shipping.transaction_id)
        assert shipping_db.base_chg == 45.50
        assert shipping_db.carrier_peak_charge == 5.25
        assert shipping_db.wizmo_peak_charge == 2.00
        assert shipping_db.accessorial_charges == 3.75
        assert shipping_db.rate == 40.00
        assert shipping_db.hst == 5.99
        assert shipping_db.gst == 2.50
    
    def test_us_shipping_status_fields(self):
        """Test shipping record with status fields."""
        shipping = USShippingFactory.create(
            current_status="In Transit",
            delivery_status="Pending"
        )
        
        # Retrieve from database to verify persistence
        shipping_db = USShipping.objects.get(transaction_id=shipping.transaction_id)
        assert shipping_db.current_status == "In Transit"
        assert shipping_db.delivery_status == "Pending"
    
    def test_us_shipping_date_fields(self):
        """Test shipping record with date fields."""
        ship_date = datetime.now().date() - timedelta(days=5)
        first_attempt_date = ship_date + timedelta(days=2)
        delivery_date = ship_date + timedelta(days=3)
        
        shipping = USShippingFactory.create(
            ship_date=ship_date,
            first_attempt_date=first_attempt_date,
            delivery_date=delivery_date,
            days_to_first_deliver=2
        )
        
        # Retrieve from database to verify persistence
        shipping_db = USShipping.objects.get(transaction_id=shipping.transaction_id)
        assert shipping_db.ship_date == ship_date
        assert shipping_db.first_attempt_date == first_attempt_date
        assert shipping_db.delivery_date == delivery_date
        assert shipping_db.days_to_first_deliver == 2