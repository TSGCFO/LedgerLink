# shipping/tests/factories.py

import factory
import random
from datetime import datetime, timedelta
from factory.django import DjangoModelFactory
from decimal import Decimal
from shipping.models import CADShipping, USShipping
from orders.tests.factories import OrderFactory
from customers.tests.factories import CustomerFactory

class CADShippingFactory(DjangoModelFactory):
    """
    Factory for creating CADShipping instances for testing.
    """
    class Meta:
        model = CADShipping
    
    transaction = factory.SubFactory(OrderFactory)
    customer = factory.SelfAttribute('transaction.customer')
    service_code_description = factory.Faker('word')
    ship_to_name = factory.Faker('name')
    ship_to_address_1 = factory.Faker('street_address')
    ship_to_address_2 = factory.Faker('secondary_address')
    shiptoaddress3 = factory.Faker('secondary_address')
    ship_to_city = factory.Faker('city')
    ship_to_state = factory.Faker('state_abbr')
    ship_to_country = factory.Faker('country_code')
    ship_to_postal_code = factory.Faker('postcode')
    tracking_number = factory.Sequence(lambda n: f'TRACK-{n:010d}')
    pre_tax_shipping_charge = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 100), 2))))
    tax1type = 'GST'
    tax1amount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(1, 10), 2))))
    tax2type = 'PST'
    tax2amount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(1, 5), 2))))
    tax3type = None
    tax3amount = None
    fuel_surcharge = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(1, 5), 2))))
    reference = factory.Faker('word')
    weight = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(1, 10), 2))))
    gross_weight = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(1, 15), 2))))
    box_length = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5, 30), 2))))
    box_width = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5, 20), 2))))
    box_height = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5, 10), 2))))
    box_name = factory.Sequence(lambda n: f'Box {n}')
    ship_date = factory.LazyFunction(lambda: datetime.now() - timedelta(days=random.randint(1, 30)))
    carrier = factory.Iterator(['FedEx', 'UPS', 'DHL', 'Canada Post'])
    raw_ship_date = factory.LazyAttribute(lambda o: o.ship_date.strftime('%Y-%m-%d'))

class USShippingFactory(DjangoModelFactory):
    """
    Factory for creating USShipping instances for testing.
    """
    class Meta:
        model = USShipping
    
    transaction = factory.SubFactory(OrderFactory)
    customer = factory.SelfAttribute('transaction.customer')
    ship_date = factory.LazyFunction(lambda: datetime.now().date() - timedelta(days=random.randint(1, 30)))
    ship_to_name = factory.Faker('name')
    ship_to_address_1 = factory.Faker('street_address')
    ship_to_address_2 = factory.Faker('secondary_address')
    ship_to_city = factory.Faker('city')
    ship_to_state = factory.Faker('state_abbr')
    ship_to_zip = factory.Faker('zipcode')
    ship_to_country_code = 'US'
    tracking_number = factory.Sequence(lambda n: f'US-TRACK-{n:010d}')
    service_name = factory.Iterator(['Ground', 'Express', '2-Day', 'Next Day'])
    weight_lbs = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(1, 50), 2))))
    length_in = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5, 30), 2))))
    width_in = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5, 20), 2))))
    height_in = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5, 10), 2))))
    base_chg = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 100), 2))))
    carrier_peak_charge = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(0, 10), 2))))
    wizmo_peak_charge = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(0, 5), 2))))
    accessorial_charges = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(0, 15), 2))))
    rate = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 50), 2))))
    hst = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(0, 10), 2))))
    gst = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(0, 5), 2))))
    current_status = factory.Iterator(['In Transit', 'Delivered', 'Exception'])
    delivery_status = factory.Iterator(['Completed', 'Pending', 'Failed'])
    first_attempt_date = factory.LazyAttribute(lambda o: o.ship_date + timedelta(days=random.randint(1, 3)))
    delivery_date = factory.LazyAttribute(lambda o: o.first_attempt_date + timedelta(days=random.randint(0, 3)))
    days_to_first_deliver = factory.LazyAttribute(lambda o: (o.first_attempt_date - o.ship_date).days)