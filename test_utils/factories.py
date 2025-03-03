"""
Factory classes for test data generation using factory_boy.
These factories create test data for various models in the LedgerLink project.
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpassword123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    date_joined = factory.LazyFunction(timezone.now)

class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = 'customers.Customer'
    
    company_name = factory.Faker('company')
    contact_name = factory.Faker('name')
    contact_email = factory.Faker('email')
    contact_phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    postal_code = factory.Faker('zipcode')
    country = factory.Faker('country_code')
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = 'products.Product'
    
    name = factory.Sequence(lambda n: f'Product {n}')
    sku = factory.Sequence(lambda n: f'SKU-{n:06d}')
    description = factory.Faker('paragraph')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    weight = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = 'orders.Order'
    
    customer = factory.SubFactory(CustomerFactory)
    order_number = factory.Sequence(lambda n: f'ORD-{n:06d}')
    order_date = factory.LazyFunction(timezone.now)
    status = 'pending'  # Default status
    shipping_address = factory.Faker('address')
    shipping_city = factory.Faker('city')
    shipping_state = factory.Faker('state_abbr')
    shipping_postal_code = factory.Faker('zipcode')
    shipping_country = factory.Faker('country_code')
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

class BasicRuleFactory(DjangoModelFactory):
    class Meta:
        model = 'rules.BasicRule'
    
    name = factory.Sequence(lambda n: f'Rule {n}')
    description = factory.Faker('sentence')
    field = 'product__sku'  # Example field
    operator = 'equal'  # Example operator
    value = factory.Sequence(lambda n: f'SKU-{n:06d}')
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

# Shipping factories
class CADShippingFactory(DjangoModelFactory):
    class Meta:
        model = 'shipping.CADShipping'
    
    transaction = factory.SubFactory(OrderFactory)
    customer = factory.SelfAttribute('transaction.customer')
    service_code_description = factory.Faker('text', max_nb_chars=20)
    ship_to_name = factory.Faker('name')
    ship_to_address_1 = factory.Faker('street_address')
    ship_to_address_2 = factory.Faker('secondary_address', allow_null=True)
    ship_to_city = factory.Faker('city')
    ship_to_state = factory.Faker('state_abbr')
    ship_to_country = 'CA'
    ship_to_postal_code = factory.Faker('postalcode')
    tracking_number = factory.Sequence(lambda n: f'CAD{n:010d}')
    pre_tax_shipping_charge = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    weight = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    carrier = factory.Faker('random_element', elements=['Canada Post', 'UPS', 'FedEx', 'Purolator'])
    ship_date = factory.LazyFunction(timezone.now)

class USShippingFactory(DjangoModelFactory):
    class Meta:
        model = 'shipping.USShipping'
    
    transaction = factory.SubFactory(OrderFactory)
    customer = factory.SelfAttribute('transaction.customer')
    ship_date = factory.LazyFunction(lambda: timezone.now().date())
    ship_to_name = factory.Faker('name')
    ship_to_address_1 = factory.Faker('street_address')
    ship_to_address_2 = factory.Faker('secondary_address', allow_null=True)
    ship_to_city = factory.Faker('city')
    ship_to_state = factory.Faker('state_abbr')
    ship_to_zip = factory.Faker('zipcode')
    ship_to_country_code = 'US'
    tracking_number = factory.Sequence(lambda n: f'US{n:010d}')
    service_name = factory.Faker('random_element', elements=['Ground', 'Express', '2-Day', 'Next Day'])
    weight_lbs = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    current_status = factory.Faker('random_element', elements=['pending', 'in_transit', 'delivered', 'exception'])
    delivery_status = factory.Faker('random_element', elements=['pending', 'attempted', 'delivered', 'failed'])

# Add more factories as needed for other models