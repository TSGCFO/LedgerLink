import os
import pytest
from django.conf import settings
from django.test import TestCase
from django.db import connection
from pytest_factoryboy import register

# Import your factory classes here
from customers.models import Customer
from orders.models import Order
from products.models import Product
from services.models import Service
from materials.models import Material, BoxPrice
from inserts.models import Insert
from customer_services.models import CustomerService
from shipping.models import CADShipping, USShipping
from rules.models import Rule, RuleGroup, AdvancedRule
from billing.models import BillingReport


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup):
    """
    Configure the test database with test-specific tables/views.
    We're extending the built-in pytest-django fixture.
    """
    with connection.cursor() as cursor:
        # Create OrderSKUView
        cursor.execute("""
        CREATE OR REPLACE VIEW orders_orderskuview AS
        SELECT o.id, 
               o.status,
               o.order_date, 
               o.priority,
               o.customer_id,
               jsonb_object_keys(o.sku_quantities) as sku_id,
               (o.sku_quantities->>jsonb_object_keys(o.sku_quantities))::integer as quantity
        FROM orders_order o
        """)
        
        # Create CustomerServiceView
        cursor.execute("""
        CREATE OR REPLACE VIEW customer_services_customerserviceview AS
        SELECT cs.id,
               cs.customer_id,
               cs.service_id,
               cs.custom_price,
               s.name as service_name,
               s.charge_type,
               c.company_name
        FROM customer_services_customerservice cs
        JOIN customers_customer c ON cs.customer_id = c.id
        JOIN services_service s ON cs.service_id = s.id
        """)


class MockOrderSKUView:
    """
    Test utility for mocking OrderSKUView database results
    """
    def __init__(self, id, status, order_date, priority, customer_id, sku_id, quantity):
        self.id = id
        self.status = status
        self.order_date = order_date
        self.priority = priority
        self.customer_id = customer_id
        self.sku_id = sku_id
        self.quantity = quantity


class MockCustomerServiceView:
    """
    Test utility for mocking CustomerServiceView database results
    """
    def __init__(self, id, customer_id, service_id, custom_price, service_name, charge_type, company_name):
        self.id = id
        self.customer_id = customer_id
        self.service_id = service_id
        self.custom_price = custom_price
        self.service_name = service_name
        self.charge_type = charge_type
        self.company_name = company_name


# Register factories if using factory_boy
# register(UserFactory)
# register(CustomerFactory)
# etc.