# orders/tests/factories.py
import factory
import random
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from factory.django import DjangoModelFactory
from ..models import Order
from customers.tests.factories import CustomerFactory


@factory.django.mute_signals(post_save)
class OrderFactory(DjangoModelFactory):
    """Factory for creating Order instances for testing"""
    
    class Meta:
        model = Order
    
    # Required fields
    transaction_id = factory.Sequence(lambda n: 100000 + n)  # Use a simple sequence for testing
    customer = factory.SubFactory(CustomerFactory)
    reference_number = factory.Sequence(lambda n: f"ORD-{n:06d}")
    
    # Optional fields with defaults
    status = 'draft'
    priority = 'medium'
    close_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    
    # Shipping information
    ship_to_name = factory.Faker('name')
    ship_to_company = factory.Faker('company')
    ship_to_address = factory.Faker('street_address')
    ship_to_city = factory.Faker('city')
    ship_to_state = factory.Faker('state_abbr')
    ship_to_zip = factory.Faker('zipcode')
    ship_to_country = 'US'
    
    # Order details
    weight_lb = factory.LazyFunction(lambda: round(random.uniform(1, 100), 2))
    total_item_qty = factory.LazyFunction(lambda: random.randint(1, 100))
    volume_cuft = factory.LazyFunction(lambda: round(random.uniform(1, 50), 2))
    packages = factory.LazyFunction(lambda: random.randint(1, 10))
    notes = factory.Faker('paragraph')
    carrier = factory.Iterator(['FedEx', 'UPS', 'USPS', 'DHL'])
    
    # Generate random SKU quantities
    @factory.lazy_attribute
    def sku_quantity(self):
        num_skus = random.randint(1, 5)
        skus = {f"SKU-{i:04d}": random.randint(1, 20) for i in range(num_skus)}
        return skus
    
    # Set line_items based on sku_quantity
    @factory.lazy_attribute
    def line_items(self):
        return len(self.sku_quantity) if self.sku_quantity else 0


class SubmittedOrderFactory(OrderFactory):
    """Factory for creating submitted Orders"""
    status = 'submitted'


class ShippedOrderFactory(OrderFactory):
    """Factory for creating shipped Orders"""
    status = 'shipped'


class DeliveredOrderFactory(OrderFactory):
    """Factory for creating delivered Orders"""
    status = 'delivered'


class CancelledOrderFactory(OrderFactory):
    """Factory for creating cancelled Orders"""
    status = 'cancelled'


class HighPriorityOrderFactory(OrderFactory):
    """Factory for creating high priority Orders"""
    priority = 'high'


class LowPriorityOrderFactory(OrderFactory):
    """Factory for creating low priority Orders"""
    priority = 'low'


class OrderWithoutShippingFactory(OrderFactory):
    """Factory for creating Orders without shipping information"""
    ship_to_name = None
    ship_to_company = None
    ship_to_address = None
    ship_to_city = None
    ship_to_state = None
    ship_to_zip = None
    ship_to_country = None


class LargeOrderFactory(OrderFactory):
    """Factory for creating large Orders with many SKUs"""
    
    @factory.lazy_attribute
    def sku_quantity(self):
        num_skus = random.randint(20, 50)  # Large number of SKUs
        skus = {f"SKU-{i:04d}": random.randint(1, 100) for i in range(num_skus)}
        return skus
    
    @factory.lazy_attribute
    def total_item_qty(self):
        return sum(self.sku_quantity.values()) if self.sku_quantity else 0
    
    @factory.lazy_attribute
    def line_items(self):
        return len(self.sku_quantity) if self.sku_quantity else 0
    
    packages = factory.LazyFunction(lambda: random.randint(10, 50))
    weight_lb = factory.LazyFunction(lambda: round(random.uniform(100, 1000), 2))
    volume_cuft = factory.LazyFunction(lambda: round(random.uniform(50, 500), 2))