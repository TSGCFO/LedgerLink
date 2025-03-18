# customer_services/tests/factories.py

import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from customer_services.models import CustomerService
from customers.tests.factories import CustomerFactory
from services.tests.factories import ServiceFactory
from products.tests.factories import ProductFactory

class CustomerServiceFactory(DjangoModelFactory):
    """
    Factory for creating CustomerService instances for testing.
    """
    class Meta:
        model = CustomerService
        django_get_or_create = ('customer', 'service')
    
    customer = factory.SubFactory(CustomerFactory)
    service = factory.SubFactory(ServiceFactory)
    unit_price = factory.LazyFunction(lambda: Decimal('100.00'))
    
    @factory.post_generation
    def skus(self, create, extracted, **kwargs):
        """Add SKUs to the customer service after creation."""
        if not create or not extracted:
            return
            
        for sku in extracted:
            self.skus.add(sku)