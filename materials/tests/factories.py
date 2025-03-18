import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from materials.models import Material, BoxPrice


class MaterialFactory(DjangoModelFactory):
    """Factory for creating Material model instances for testing."""
    
    class Meta:
        model = Material
    
    name = factory.Sequence(lambda n: f'Test Material {n}')
    description = factory.Faker('paragraph', nb_sentences=3)
    unit_price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True, min_value=Decimal('0.01'), max_value=Decimal('999.99'))


class BoxPriceFactory(DjangoModelFactory):
    """Factory for creating BoxPrice model instances for testing."""
    
    class Meta:
        model = BoxPrice
    
    box_type = factory.Sequence(lambda n: f'Box Type {n}')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True, min_value=Decimal('0.01'), max_value=Decimal('999.99'))
    length = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=Decimal('1.00'), max_value=Decimal('99.99'))
    width = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=Decimal('1.00'), max_value=Decimal('99.99'))
    height = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=Decimal('1.00'), max_value=Decimal('99.99'))