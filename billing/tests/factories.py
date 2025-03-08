# billing/tests/factories.py

import factory
import random
from datetime import datetime, timedelta
from factory.django import DjangoModelFactory
from decimal import Decimal
from billing.models import BillingReport, BillingReportDetail
from customers.tests.factories import CustomerFactory
from orders.tests.factories import OrderFactory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances for testing.
    """
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = False
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        self.set_password(extracted or 'password123')

class BillingReportFactory(DjangoModelFactory):
    """
    Factory for creating BillingReport instances for testing.
    """
    class Meta:
        model = BillingReport
    
    customer = factory.SubFactory(CustomerFactory)
    start_date = factory.LazyFunction(lambda: datetime.now().date() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: datetime.now().date())
    generated_at = factory.LazyFunction(datetime.now)
    total_amount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(100, 5000), 2))))
    
    @factory.lazy_attribute
    def report_data(self):
        """Generate realistic report data."""
        num_orders = random.randint(1, 5)
        orders = []
        
        order_total = Decimal('0.00')
        
        for i in range(num_orders):
            num_services = random.randint(1, 3)
            services = []
            
            service_total = Decimal('0.00')
            
            for j in range(num_services):
                service_amount = Decimal(str(round(random.uniform(10, 500), 2)))
                services.append({
                    'service_id': j + 1,
                    'service_name': f'Test Service {j + 1}',
                    'amount': str(service_amount)
                })
                service_total += service_amount
            
            orders.append({
                'order_id': i + 1,
                'services': services,
                'total_amount': str(service_total)
            })
            
            order_total += service_total
        
        return {
            'orders': orders,
            'total_amount': str(order_total),
            'service_totals': {
                'Test Service 1': str(Decimal(str(round(random.uniform(50, 1000), 2)))),
                'Test Service 2': str(Decimal(str(round(random.uniform(50, 1000), 2)))),
                'Test Service 3': str(Decimal(str(round(random.uniform(50, 1000), 2))))
            }
        }
    
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

class BillingReportDetailFactory(DjangoModelFactory):
    """
    Factory for creating BillingReportDetail instances for testing.
    """
    class Meta:
        model = BillingReportDetail
    
    report = factory.SubFactory(BillingReportFactory)
    order = factory.SubFactory(OrderFactory)
    
    @factory.lazy_attribute
    def service_breakdown(self):
        """Generate realistic service breakdown."""
        num_services = random.randint(1, 3)
        services = []
        
        service_total = Decimal('0.00')
        
        for i in range(num_services):
            service_amount = Decimal(str(round(random.uniform(10, 500), 2)))
            services.append({
                'service_id': i + 1,
                'service_name': f'Test Service {i + 1}',
                'amount': str(service_amount)
            })
            service_total += service_amount
        
        return {'services': services}
    
    total_amount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(100, 1000), 2))))