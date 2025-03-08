import factory
from django.utils import timezone
from api.tests.factories import UserFactory
from products.models import Product
from customers.models import Customer


class CustomerFactory(factory.django.DjangoModelFactory):
    """Factory for creating Customer objects for tests."""
    class Meta:
        model = Customer

    company_name = factory.Sequence(lambda n: f"Company {n}")
    legal_business_name = factory.Sequence(lambda n: f"Legal Business Name {n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.company_name.lower().replace(' ', '')}@example.com")
    phone = factory.Faker('phone_number')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip = factory.Faker('zipcode')
    country = factory.Faker('country')
    business_type = factory.Iterator(['Retail', 'Manufacturing', 'Services', 'Wholesale'])
    is_active = True
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for creating Product objects for tests."""
    class Meta:
        model = Product

    sku = factory.Sequence(lambda n: f"SKU-{n:05d}")
    customer = factory.SubFactory(CustomerFactory)
    labeling_unit_1 = factory.Iterator(['BOX', 'CASE', 'PALLET', 'EACH'])
    labeling_quantity_1 = factory.Faker('pyint', min_value=1, max_value=100)
    labeling_unit_2 = factory.LazyAttribute(lambda o: None if factory.Faker('boolean')() else 'INNER')
    labeling_quantity_2 = factory.LazyAttribute(lambda o: None if o.labeling_unit_2 is None else factory.Faker('pyint', min_value=1, max_value=50)())
    labeling_unit_3 = factory.LazyAttribute(lambda o: None if factory.Faker('boolean')() else 'PACK')
    labeling_quantity_3 = factory.LazyAttribute(lambda o: None if o.labeling_unit_3 is None else factory.Faker('pyint', min_value=1, max_value=25)())
    labeling_unit_4 = factory.LazyAttribute(lambda o: None if factory.Faker('boolean')() else 'BUNDLE')
    labeling_quantity_4 = factory.LazyAttribute(lambda o: None if o.labeling_unit_4 is None else factory.Faker('pyint', min_value=1, max_value=10)())
    labeling_unit_5 = factory.LazyAttribute(lambda o: None if factory.Faker('boolean')() else 'PIECE')
    labeling_quantity_5 = factory.LazyAttribute(lambda o: None if o.labeling_unit_5 is None else factory.Faker('pyint', min_value=1, max_value=5)())
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)