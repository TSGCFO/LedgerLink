import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from billing.models import BillingReport, BillingReportDetail
from customers.models import Customer
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from rules.models import Rule, RuleGroup

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True

class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer
    
    company_name = factory.Sequence(lambda n: f'Customer {n}')
    contact_name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order
    
    transaction_id = factory.Sequence(lambda n: f'ORD-{n:04d}')
    customer = factory.SubFactory(CustomerFactory)
    order_date = factory.LazyFunction(lambda: timezone.now().date())
    close_date = factory.LazyFunction(lambda: timezone.now().date())
    reference_number = factory.Sequence(lambda n: f'REF-{n:04d}')
    weight_lb = factory.Faker('pyfloat', min_value=1, max_value=100)
    total_item_qty = factory.Faker('pyint', min_value=1, max_value=50)
    sku_quantity = factory.LazyAttribute(
        lambda o: [
            {"sku": f"SKU-{i}", "quantity": i*2} 
            for i in range(1, o.total_item_qty % 5 + 2)
        ]
    )
    
    @factory.post_generation
    def convert_sku_quantity(self, create, extracted, **kwargs):
        """Convert SKU quantity to JSON string format"""
        import json
        if create and self.sku_quantity:
            if isinstance(self.sku_quantity, list):
                self.sku_quantity = json.dumps(self.sku_quantity)

class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service
    
    service_name = factory.Sequence(lambda n: f'Service {n}')
    service_code = factory.Sequence(lambda n: f'SRV-{n:03d}')
    description = factory.Faker('sentence')
    charge_type = factory.Iterator(['single', 'quantity', 'case_based_tier'])
    active = True

class CustomerServiceFactory(DjangoModelFactory):
    class Meta:
        model = CustomerService
    
    customer = factory.SubFactory(CustomerFactory)
    service = factory.SubFactory(ServiceFactory)
    unit_price = factory.Faker('pydecimal', min_value=1, max_value=100, right_digits=2)
    effective_date = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=30))
    end_date = None  # No end date by default
    
    @factory.post_generation
    def add_skus(self, create, extracted, **kwargs):
        """Add SKUs to the customer service"""
        if not create:
            return
        
        if extracted:
            # Add specific SKUs if provided
            for sku in extracted:
                self.skus.add(sku)
        elif kwargs.get('add_random_skus', False):
            # Add random SKUs
            from products.models import Product
            skus_count = kwargs.get('skus_count', 3)
            products = Product.objects.filter(customer=self.customer)[:skus_count]
            for product in products:
                self.skus.add(product.sku)

class RuleFactory(DjangoModelFactory):
    class Meta:
        model = Rule
    
    name = factory.Sequence(lambda n: f'Rule {n}')
    description = factory.Faker('sentence')
    field = factory.Iterator(['weight_lb', 'total_item_qty', 'ship_to_country', 'sku_quantity'])
    operator = factory.Iterator(['eq', 'gt', 'lt', 'ne', 'in', 'contains'])
    value = factory.LazyAttribute(
        lambda o: '10' if o.field in ['weight_lb', 'total_item_qty'] 
               else 'US' if o.field == 'ship_to_country' 
               else 'SKU-1'
    )
    
    @factory.post_generation
    def set_rule_group(self, create, extracted, **kwargs):
        """Associate with a rule group"""
        if not create:
            return
            
        if extracted:
            extracted.rules.add(self)

class RuleGroupFactory(DjangoModelFactory):
    class Meta:
        model = RuleGroup
    
    name = factory.Sequence(lambda n: f'Rule Group {n}')
    description = factory.Faker('sentence')
    logic_operator = factory.Iterator(['AND', 'OR', 'NOT', 'XOR', 'NAND', 'NOR'])
    customer_service = factory.SubFactory(CustomerServiceFactory)
    
    @factory.post_generation
    def add_rules(self, create, extracted, **kwargs):
        """Add rules to the rule group"""
        if not create:
            return
        
        if extracted:
            # Add specific rules
            for rule in extracted:
                self.rules.add(rule)
        else:
            # Create some rules
            rules_count = kwargs.get('rules_count', 2)
            for _ in range(rules_count):
                RuleFactory(set_rule_group=self)

class BillingReportFactory(DjangoModelFactory):
    class Meta:
        model = BillingReport
    
    customer = factory.SubFactory(CustomerFactory)
    start_date = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: timezone.now().date())
    generated_at = factory.LazyFunction(timezone.now)
    total_amount = factory.Faker('pydecimal', min_value=100, max_value=5000, right_digits=2)
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)
    
    @factory.LazyAttribute
    def report_data(self):
        """Generate mock report data"""
        service_costs = [
            {
                'service_id': i,
                'service_name': f'Service {i}',
                'amount': str(Decimal(f'{i * 10}.00'))
            } 
            for i in range(1, 4)
        ]
        
        order_count = 5
        orders = []
        total_amount = Decimal('0')
        
        for i in range(1, order_count + 1):
            order_total = Decimal('0')
            order_services = []
            
            for service in service_costs:
                # Create a copy to avoid modifying the original
                service_copy = service.copy()
                amount = Decimal(service_copy['amount'])
                order_total += amount
                order_services.append(service_copy)
            
            orders.append({
                'order_id': f'ORD-{i:04d}',
                'services': order_services,
                'total_amount': str(order_total)
            })
            total_amount += order_total
        
        return {
            'customer_id': self.customer.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'orders': orders,
            'total_amount': str(total_amount)
        }
    
    @factory.post_generation
    def create_details(self, create, extracted, **kwargs):
        """Create billing report details"""
        if not create:
            return
        
        if kwargs.get('create_details', True):
            order_count = len(self.report_data.get('orders', []))
            for i in range(order_count):
                BillingReportDetailFactory(
                    report=self,
                    order=OrderFactory(customer=self.customer)
                )

class BillingReportDetailFactory(DjangoModelFactory):
    class Meta:
        model = BillingReportDetail
    
    report = factory.SubFactory(BillingReportFactory, create_details=False)
    order = factory.SubFactory(OrderFactory)
    total_amount = factory.Faker('pydecimal', min_value=10, max_value=500, right_digits=2)
    
    @factory.LazyAttribute
    def service_breakdown(self):
        """Generate mock service breakdown data"""
        service_count = 3
        breakdown = {}
        total = Decimal('0')
        
        for i in range(1, service_count + 1):
            amount = Decimal(f'{i * 10}.00')
            breakdown[f'service_{i}'] = {
                'service_id': i,
                'service_name': f'Service {i}',
                'amount': str(amount)
            }
            total += amount
        
        # Ensure total matches the total_amount field
        self.total_amount = total
        
        return breakdown