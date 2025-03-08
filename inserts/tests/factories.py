import factory
from factory.django import DjangoModelFactory
from inserts.models import Insert
from customers.tests.factories import CustomerFactory


class InsertFactory(DjangoModelFactory):
    """Factory for creating Insert model instances for testing."""
    
    class Meta:
        model = Insert
    
    sku = factory.Sequence(lambda n: f'TEST-INSERT-{n}')
    insert_name = factory.Sequence(lambda n: f'Test Insert {n}')
    insert_quantity = factory.Faker('random_int', min=1, max=100)
    customer = factory.SubFactory(CustomerFactory)