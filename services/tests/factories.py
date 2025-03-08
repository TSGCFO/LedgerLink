# services/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from services.models import Service
import random

class ServiceFactory(DjangoModelFactory):
    """
    Factory for creating Service instances for testing.
    """
    class Meta:
        model = Service
        django_get_or_create = ('service_name',)
    
    service_name = factory.Sequence(lambda n: f'Test Service {n}')
    description = factory.Faker('paragraph', nb_sentences=3)
    charge_type = factory.LazyFunction(lambda: random.choice(['single', 'quantity']))
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override _create to handle the custom validation in the model."""
        # Force lowercase for service_name if needed for validation
        if 'service_name' in kwargs:
            kwargs['service_name'] = kwargs['service_name'].strip()
        return super()._create(model_class, *args, **kwargs)