import factory
from customers.models import Customer
from faker import Faker

fake = Faker()


class CustomerFactory(factory.django.DjangoModelFactory):
    """Factory for generating test Customer instances."""
    
    class Meta:
        model = Customer
    
    company_name = factory.LazyFunction(lambda: fake.company())
    legal_business_name = factory.LazyFunction(lambda: fake.company() + " LLC")
    email = factory.LazyFunction(lambda: fake.email())
    phone = factory.LazyFunction(lambda: fake.phone_number()[:20])
    address = factory.LazyFunction(lambda: fake.street_address())
    city = factory.LazyFunction(lambda: fake.city())
    state = factory.LazyFunction(lambda: fake.state_abbr())
    zip = factory.LazyFunction(lambda: fake.zipcode())
    country = factory.LazyAttribute(lambda o: 'US')
    business_type = factory.LazyFunction(lambda: fake.random_element(elements=("Retail", "Wholesale", "Manufacturing", "Service")))
    is_active = True