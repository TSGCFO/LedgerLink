"""
Factory definitions that produce realistic test data.

This module provides factories for creating test data that closely 
resembles production data patterns. These factories are designed to be 
used across all test suites for consistent and realistic test data.
"""

import factory
import json
import random
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

# Import models
from customers.models import Customer
from orders.models import Order
from products.models import Product
from services.models import Service
from customer_services.models import CustomerService
from billing.models import BillingReport, BillingReportDetail
from materials.models import Material, BoxPrice
from shipping.models import USShipping, CADShipping
from rules.models import RuleGroup, Rule, AdvancedRule
from inserts.models import Insert

# User Factory
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances with realistic data."""
    
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = False
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        password = extracted or 'password123'
        self.set_password(password)
        if create:
            self.save()

class AdminUserFactory(UserFactory):
    """Factory for creating admin User instances."""
    username = factory.Sequence(lambda n: f'admin{n}')
    is_staff = True
    is_superuser = True

# Customer Factory
class CustomerFactory(factory.django.DjangoModelFactory):
    """Factory for creating Customer instances with realistic data."""
    
    class Meta:
        model = Customer
        django_get_or_create = ('email',)
    
    company_name = factory.Sequence(lambda n: f"Company {n}")
    legal_business_name = factory.LazyAttribute(
        lambda o: f"{o.company_name} LLC"
    )
    email = factory.Sequence(lambda n: f"contact{n}@company{n}.com")
    phone = factory.Sequence(lambda n: f"555-{n:03d}-{random.randint(1000, 9999)}")
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip = factory.Faker('zipcode')
    country = 'US'
    business_type = factory.Iterator(['Retail', 'Manufacturing', 'Distribution', 'Service'])
    is_active = True

class RetailCustomerFactory(CustomerFactory):
    """Factory for creating Retail customers."""
    business_type = 'Retail'

class ManufacturingCustomerFactory(CustomerFactory):
    """Factory for creating Manufacturing customers."""
    business_type = 'Manufacturing'

class DistributionCustomerFactory(CustomerFactory):
    """Factory for creating Distribution customers."""
    business_type = 'Distribution'

class ServiceCustomerFactory(CustomerFactory):
    """Factory for creating Service customers."""
    business_type = 'Service'

# Order Factory
class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for creating Order instances with numeric transaction IDs."""
    
    class Meta:
        model = Order
        django_get_or_create = ('transaction_id',)
    
    # Required fields
    transaction_id = factory.Sequence(lambda n: 100000 + n)
    customer = factory.SubFactory(CustomerFactory)
    reference_number = factory.Sequence(lambda n: f"REF-{n:06d}")
    
    # Order status and priority
    status = 'draft'
    priority = 'medium'
    close_date = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=30))
    
    # Shipping information
    ship_to_name = factory.Faker('name')
    ship_to_company = factory.Faker('company')
    ship_to_address = factory.Faker('street_address')
    ship_to_city = factory.Faker('city')
    ship_to_state = factory.Faker('state_abbr')
    ship_to_zip = factory.Faker('zipcode')
    ship_to_country = 'US'
    
    # Order details
    weight_lb = factory.LazyFunction(lambda: round(random.uniform(1, 100), 2))
    line_items = factory.LazyFunction(lambda: random.randint(1, 10))
    total_item_qty = factory.LazyFunction(lambda: random.randint(1, 100))
    volume_cuft = factory.LazyFunction(lambda: round(random.uniform(1, 50), 2))
    packages = factory.LazyFunction(lambda: random.randint(1, 10))
    notes = factory.Faker('paragraph')
    carrier = factory.Iterator(['FedEx', 'UPS', 'USPS', 'DHL'])
    
    # Generate realistic SKU quantities
    @factory.lazy_attribute
    def sku_quantity(self):
        """Generate realistic SKU quantities based on production patterns."""
        num_skus = random.randint(1, 5)
        skus = {}
        
        # Use realistic SKU patterns: PREFIX-NNNN format
        prefixes = ['SKU', 'PROD', 'ITEM', 'INV']
        
        for i in range(num_skus):
            prefix = random.choice(prefixes)
            sku_id = f"{prefix}-{random.randint(1000, 9999)}"
            quantity = random.randint(1, 20)
            skus[sku_id] = quantity
            
        return skus

class SubmittedOrderFactory(OrderFactory):
    """Factory for creating submitted orders."""
    status = 'submitted'
    
    @factory.post_generation
    def submission_date(self, create, extracted, **kwargs):
        """Set submission date after order creation."""
        self.submission_date = extracted or timezone.now()
        if create:
            self.save()

class ShippedOrderFactory(SubmittedOrderFactory):
    """Factory for creating shipped orders."""
    status = 'shipped'
    
    @factory.post_generation
    def ship_date(self, create, extracted, **kwargs):
        """Set ship date after order creation."""
        self.ship_date = extracted or timezone.now()
        if create:
            self.save()

class DeliveredOrderFactory(ShippedOrderFactory):
    """Factory for creating delivered orders."""
    status = 'delivered'
    
    @factory.post_generation
    def delivery_date(self, create, extracted, **kwargs):
        """Set delivery date after order creation."""
        self.delivery_date = extracted or timezone.now()
        if create:
            self.save()

class CancelledOrderFactory(OrderFactory):
    """Factory for creating cancelled orders."""
    status = 'cancelled'
    
    @factory.post_generation
    def cancellation_date(self, create, extracted, **kwargs):
        """Set cancellation date after order creation."""
        self.cancellation_date = extracted or timezone.now()
        if create:
            self.save()

class HighPriorityOrderFactory(OrderFactory):
    """Factory for creating high priority orders."""
    priority = 'high'

class LowPriorityOrderFactory(OrderFactory):
    """Factory for creating low priority orders."""
    priority = 'low'

class LargeOrderFactory(OrderFactory):
    """Factory for creating orders with many SKUs for performance testing."""
    line_items = factory.LazyFunction(lambda: random.randint(20, 50))
    total_item_qty = factory.LazyFunction(lambda: random.randint(100, 500))
    
    @factory.lazy_attribute
    def sku_quantity(self):
        """Generate a large number of SKUs for performance testing."""
        num_skus = random.randint(20, 50)
        skus = {}
        
        prefixes = ['SKU', 'PROD', 'ITEM', 'INV']
        
        for i in range(num_skus):
            prefix = random.choice(prefixes)
            sku_id = f"{prefix}-{random.randint(1000, 9999)}"
            quantity = random.randint(1, 100)
            skus[sku_id] = quantity
            
        return skus

class OrderWithComplexDataFactory(OrderFactory):
    """Factory for creating orders with complex nested data structures."""
    
    @factory.lazy_attribute
    def sku_quantity(self):
        """Generate complex nested SKU data structure."""
        num_skus = random.randint(3, 8)
        skus = {}
        
        for i in range(num_skus):
            sku_id = f"SKU-{random.randint(1000, 9999)}"
            skus[sku_id] = {
                'quantity': random.randint(1, 50),
                'cases': random.randint(0, 5),
                'picks': random.randint(0, 9),
                'price': round(random.uniform(5, 500), 2),
                'weight': round(random.uniform(0.1, 10), 2),
                'dimensions': {
                    'length': round(random.uniform(1, 30), 1),
                    'width': round(random.uniform(1, 20), 1),
                    'height': round(random.uniform(1, 15), 1)
                }
            }
            
        return skus

# Product Factory
class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for creating Product instances."""
    
    class Meta:
        model = Product
        django_get_or_create = ('sku', 'customer')
    
    sku = factory.Sequence(lambda n: f"PROD-{n:04d}")
    customer = factory.SubFactory(CustomerFactory)
    name = factory.Sequence(lambda n: f"Product {n}")
    description = factory.Faker('sentence')
    
    # Labeling units
    unit_1 = 'EA'
    unit_2 = 'CS'
    unit_3 = 'PL'
    
    # Labeling quantities
    quantity_1 = 1
    quantity_2 = factory.LazyFunction(lambda: random.randint(5, 20))
    quantity_3 = factory.LazyFunction(lambda: random.randint(40, 100))

# Service Factory
class ServiceFactory(factory.django.DjangoModelFactory):
    """Factory for creating Service instances."""
    
    class Meta:
        model = Service
        django_get_or_create = ('service_name',)
    
    service_name = factory.Sequence(lambda n: f"Service {n}")
    description = factory.Faker('sentence')
    charge_type = factory.Iterator(['fixed', 'per_unit', 'tiered', 'case_based_tier'])

class FixedChargeServiceFactory(ServiceFactory):
    """Factory for creating fixed charge services."""
    charge_type = 'fixed'

class PerUnitServiceFactory(ServiceFactory):
    """Factory for creating per-unit services."""
    charge_type = 'per_unit'

class TieredServiceFactory(ServiceFactory):
    """Factory for creating tiered services."""
    charge_type = 'tiered'

class CaseTierServiceFactory(ServiceFactory):
    """Factory for creating case-based tier services."""
    charge_type = 'case_based_tier'

# CustomerService Factory
class CustomerServiceFactory(factory.django.DjangoModelFactory):
    """Factory for creating CustomerService instances."""
    
    class Meta:
        model = CustomerService
        django_get_or_create = ('customer', 'service')
    
    customer = factory.SubFactory(CustomerFactory)
    service = factory.SubFactory(ServiceFactory)
    unit_price = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 1000), 2))))
    is_active = True
    
    @factory.post_generation
    def skus(self, create, extracted, **kwargs):
        """Add SKUs to the CustomerService."""
        if not create:
            return
            
        if extracted:
            for sku in extracted:
                self.skus.add(sku)
        else:
            # Create some default SKUs
            num_skus = random.randint(1, 5)
            for _ in range(num_skus):
                product = ProductFactory(customer=self.customer)
                self.skus.add(product)

# Rules Factories
class RuleGroupFactory(factory.django.DjangoModelFactory):
    """Factory for creating RuleGroup instances."""
    
    class Meta:
        model = RuleGroup
    
    name = factory.Sequence(lambda n: f"Rule Group {n}")
    customer_service = factory.SubFactory(CustomerServiceFactory)
    logic_operator = factory.Iterator(['AND', 'OR'])
    
    @factory.post_generation
    def rules(self, create, extracted, **kwargs):
        """Add rules to the rule group after creation."""
        if not create:
            return
            
        if extracted:
            for rule in extracted:
                rule.rule_group = self
                rule.save()
        else:
            # Create some default rules
            num_rules = random.randint(1, 3)
            for i in range(num_rules):
                rule = RuleFactory(rule_group=self)

class RuleFactory(factory.django.DjangoModelFactory):
    """Factory for creating basic Rule instances."""
    
    class Meta:
        model = Rule
    
    rule_group = factory.SubFactory(RuleGroupFactory)
    field = factory.Iterator([
        'weight', 'line_items', 'total_item_qty', 'volume', 
        'packages', 'sku_count', 'is_rush'
    ])
    operator = factory.Iterator(['eq', 'ne', 'gt', 'lt', 'gte', 'lte'])
    value = factory.LazyFunction(lambda: random.randint(1, 100))
    adjustment_amount = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(1, 100), 2)))
    )
    adjustment_type = factory.Iterator(['fixed', 'percentage'])

class AdvancedRuleFactory(factory.django.DjangoModelFactory):
    """Factory for creating AdvancedRule instances with complex conditions and calculations."""
    
    class Meta:
        model = AdvancedRule
    
    rule_group = factory.SubFactory(RuleGroupFactory)
    name = factory.Sequence(lambda n: f"Advanced Rule {n}")
    
    @factory.lazy_attribute
    def conditions(self):
        """Generate realistic conditions for advanced rules."""
        # Simple condition
        if random.random() < 0.3:
            return {
                "field": random.choice(["weight", "line_items", "total_item_qty"]),
                "operator": random.choice(["eq", "gt", "lt"]),
                "value": random.randint(1, 100)
            }
        
        # OR condition
        elif random.random() < 0.6:
            return {
                "operator": "OR",
                "conditions": [
                    {
                        "field": "weight",
                        "operator": "gt",
                        "value": random.randint(20, 50)
                    },
                    {
                        "field": "line_items",
                        "operator": "gte",
                        "value": random.randint(5, 15)
                    }
                ]
            }
        
        # AND condition
        else:
            return {
                "operator": "AND",
                "conditions": [
                    {
                        "field": "total_item_qty",
                        "operator": "gte",
                        "value": random.randint(10, 50)
                    },
                    {
                        "field": "packages",
                        "operator": "lt",
                        "value": random.randint(5, 15)
                    }
                ]
            }
    
    @factory.lazy_attribute
    def calculations(self):
        """Generate realistic calculations for advanced rules."""
        calc_type = random.choice(["fixed", "per_unit", "formula"])
        
        if calc_type == "fixed":
            return {
                "type": "fixed",
                "amount": round(random.uniform(10, 200), 2)
            }
        elif calc_type == "per_unit":
            return {
                "type": "per_unit",
                "unit": random.choice(["item", "package", "line"]),
                "rate": round(random.uniform(0.5, 10), 2)
            }
        else:
            return {
                "type": "formula",
                "formula": f"{round(random.uniform(0.5, 5), 2)} * [total_item_qty] + {round(random.uniform(5, 20), 2)}"
            }
    
    @factory.lazy_attribute
    def tier_config(self):
        """Generate realistic tier configuration for case-based rules."""
        num_tiers = random.randint(2, 4)
        tiers = []
        
        min_val = 0
        for i in range(num_tiers):
            max_val = min_val + random.randint(5, 20)
            
            # Last tier has no max
            if i == num_tiers - 1:
                tiers.append({
                    "min": min_val,
                    "value": round(random.uniform(5, 50), 2)
                })
            else:
                tiers.append({
                    "min": min_val,
                    "max": max_val,
                    "value": round(random.uniform(5, 50), 2)
                })
                min_val = max_val
        
        return {
            "field": random.choice(["cases", "picks", "total_item_qty"]),
            "tiers": tiers
        }

# Billing Factories
class BillingReportFactory(factory.django.DjangoModelFactory):
    """Factory for creating BillingReport instances."""
    
    class Meta:
        model = BillingReport
    
    customer = factory.SubFactory(CustomerFactory)
    start_date = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: timezone.now().date())
    total_amount = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(100, 5000), 2)))
    )
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda o: o.created_by)
    
    @factory.lazy_attribute
    def report_data(self):
        """Generate realistic report data with numeric transaction IDs."""
        num_orders = random.randint(1, 5)
        orders = []
        
        for i in range(num_orders):
            # Use numeric order_id
            order_id = 100000 + i
            
            num_services = random.randint(1, 3)
            services = []
            
            service_total = Decimal('0.00')
            
            for j in range(num_services):
                service_amount = Decimal(str(round(random.uniform(10, 500), 2)))
                services.append({
                    'service_id': j + 1,
                    'service_name': f'Service {j + 1}',
                    'amount': str(service_amount)
                })
                service_total += service_amount
            
            orders.append({
                'order_id': order_id,
                'services': services,
                'total_amount': str(service_total)
            })
        
        return {
            'orders': orders,
            'total_amount': str(sum(Decimal(order['total_amount']) for order in orders)),
            'service_totals': {
                '1': {'name': 'Service 1', 'amount': str(Decimal('100.00'))},
                '2': {'name': 'Service 2', 'amount': str(Decimal('200.00'))},
                '3': {'name': 'Service 3', 'amount': str(Decimal('300.00'))}
            }
        }

class BillingReportDetailFactory(factory.django.DjangoModelFactory):
    """Factory for creating BillingReportDetail instances."""
    
    class Meta:
        model = BillingReportDetail
    
    report = factory.SubFactory(BillingReportFactory)
    order = factory.SubFactory(OrderFactory)
    
    @factory.lazy_attribute
    def service_breakdown(self):
        """Generate realistic service breakdown."""
        services = []
        total = Decimal('0.00')
        
        for i in range(1, 4):
            amount = Decimal(str(round(random.uniform(10, 200), 2)))
            services.append({
                'service_id': i,
                'service_name': f'Service {i}',
                'amount': str(amount)
            })
            total += amount
        
        return {'services': services}
    
    total_amount = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(10, 1000), 2)))
    )

# Material Factories
class MaterialFactory(factory.django.DjangoModelFactory):
    """Factory for creating Material instances."""
    
    class Meta:
        model = Material
    
    name = factory.Sequence(lambda n: f"Material {n}")
    description = factory.Faker('sentence')
    
    @factory.lazy_attribute
    def properties(self):
        """Generate realistic material properties."""
        return {
            'color': random.choice(['White', 'Brown', 'Black', 'Blue', 'Green']),
            'thickness': round(random.uniform(0.1, 5.0), 2),
            'weight_per_sqft': round(random.uniform(0.05, 2.0), 3),
            'recyclable': random.choice([True, False])
        }

class BoxPriceFactory(factory.django.DjangoModelFactory):
    """Factory for creating BoxPrice instances."""
    
    class Meta:
        model = BoxPrice
    
    material = factory.SubFactory(MaterialFactory)
    size = factory.Iterator(['S', 'M', 'L', 'XL', 'XXL'])
    price = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(1, 50), 2)))
    )
    
    @factory.lazy_attribute
    def dimensions(self):
        """Generate realistic box dimensions based on size."""
        sizes = {
            'S': (8, 6, 4),
            'M': (12, 10, 6),
            'L': (18, 14, 8),
            'XL': (24, 18, 12),
            'XXL': (30, 24, 18)
        }
        
        base_dimensions = sizes.get(self.size, (10, 8, 6))
        variation = random.uniform(0.9, 1.1)
        
        return {
            'length': round(base_dimensions[0] * variation, 1),
            'width': round(base_dimensions[1] * variation, 1),
            'height': round(base_dimensions[2] * variation, 1)
        }

# Shipping Factories
class USShippingFactory(factory.django.DjangoModelFactory):
    """Factory for creating USShipping instances."""
    
    class Meta:
        model = USShipping
    
    order = factory.SubFactory(OrderFactory)
    carrier = factory.Iterator(['USPS', 'UPS', 'FedEx', 'DHL'])
    tracking_number = factory.Sequence(
        lambda n: f"{random.choice(['US', 'UP', 'FX', 'DH'])}{n:010d}"
    )
    service_level = factory.Iterator(['Ground', '2-Day', 'Next Day', 'Economy'])
    
    @factory.lazy_attribute
    def shipping_cost(self):
        """Generate realistic shipping cost based on service level."""
        base_costs = {
            'Ground': (5, 20),
            '2-Day': (15, 50),
            'Next Day': (25, 100),
            'Economy': (3, 15)
        }
        
        base_range = base_costs.get(self.service_level, (5, 30))
        return Decimal(str(round(random.uniform(base_range[0], base_range[1]), 2)))

class CADShippingFactory(factory.django.DjangoModelFactory):
    """Factory for creating CADShipping instances."""
    
    class Meta:
        model = CADShipping
    
    order = factory.SubFactory(OrderFactory)
    carrier = factory.Iterator(['Canada Post', 'Purolator', 'UPS Canada', 'DHL Canada'])
    tracking_number = factory.Sequence(
        lambda n: f"{random.choice(['CP', 'PU', 'UC', 'DC'])}{n:010d}"
    )
    service_level = factory.Iterator(['Standard', 'Expedited', 'Priority', 'Economy'])
    customs_reference = factory.Sequence(lambda n: f"CUS-{n:08d}")
    
    @factory.lazy_attribute
    def shipping_cost(self):
        """Generate realistic shipping cost based on service level."""
        base_costs = {
            'Standard': (10, 30),
            'Expedited': (20, 60),
            'Priority': (30, 120),
            'Economy': (8, 25)
        }
        
        base_range = base_costs.get(self.service_level, (10, 40))
        return Decimal(str(round(random.uniform(base_range[0], base_range[1]), 2)))
    
    @factory.lazy_attribute
    def duties_and_taxes(self):
        """Generate realistic duties and taxes (usually a percentage of shipping cost)."""
        return self.shipping_cost * Decimal(str(round(random.uniform(0.1, 0.3), 2)))

# Insert Factory
class InsertFactory(factory.django.DjangoModelFactory):
    """Factory for creating Insert instances."""
    
    class Meta:
        model = Insert
    
    name = factory.Sequence(lambda n: f"Insert {n}")
    description = factory.Faker('sentence')
    material = factory.SubFactory(MaterialFactory)
    
    @factory.lazy_attribute
    def dimensions(self):
        """Generate realistic insert dimensions."""
        return {
            'length': round(random.uniform(1, 20), 1),
            'width': round(random.uniform(1, 15), 1),
            'thickness': round(random.uniform(0.1, 2), 2)
        }
    
    unit_cost = factory.LazyFunction(
        lambda: Decimal(str(round(random.uniform(0.5, 10), 2)))
    )

# Sample Data Factories
class RealisticCustomerFactory(CustomerFactory):
    """
    Factory creating customers with realistic company names based on real-world patterns.
    """
    # Using realistic company names with suffixes (but avoid actual company names)
    @factory.lazy_attribute
    def company_name(self):
        prefixes = ['Global', 'Advanced', 'Premier', 'Superior', 'Precision', 'Elite', 
                    'Star', 'Metro', 'Dynamic', 'Modern']
        suffixes = ['Solutions', 'Logistics', 'Distribution', 'Supply', 'Industries', 
                    'Products', 'Manufacturing', 'Services', 'Enterprises', 'Group']
        middle = ['Tech', 'Med', 'Food', 'Retail', 'Auto', 'Home', 'Sport', 'Office',
                  'Fashion', 'Furniture']
        
        name_pattern = random.choice([
            f"{random.choice(prefixes)} {random.choice(middle)} {random.choice(suffixes)}",
            f"{random.choice(prefixes)} {random.choice(suffixes)}",
            f"{random.choice(middle)} {random.choice(suffixes)}",
            f"{random.choice(prefixes)} {random.choice(middle)}"
        ])
        
        return name_pattern

class RealisticOrderFactory(OrderFactory):
    """
    Factory creating orders with realistic patterns based on production data.
    """
    @factory.lazy_attribute
    def sku_quantity(self):
        """Generate SKU quantities that match patterns seen in production."""
        num_skus = random.randint(1, 8)
        skus = {}
        
        # More realistic SKU patterns from production
        # 1. Format patterns: ABC-1234, A123, 123A, ABCD12345
        format_patterns = [
            lambda: f"{random.choice(['SKU', 'PRD', 'ITM', 'INV'])}-{random.randint(1000, 9999)}",
            lambda: f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100, 999)}",
            lambda: f"{random.randint(100, 999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
            lambda: f"{random.choice(['SKU', 'PRD', 'ITM'])}{random.randint(10000, 99999)}"
        ]
        
        # 2. Quantity patterns: Often clustered (many of one, few of others)
        for i in range(num_skus):
            sku_id = random.choice(format_patterns)()
            
            # Primary SKU often has higher quantity
            if i == 0:
                quantity = random.randint(10, 50)
            else:
                # Secondary SKUs often follow power law distribution
                quantity = random.choices(
                    [random.randint(1, 3), random.randint(4, 10), random.randint(11, 30)],
                    weights=[0.6, 0.3, 0.1]
                )[0]
            
            skus[sku_id] = quantity
            
        return skus

# Factory Traits
class WithNotesTrait(factory.Trait):
    """Trait to add detailed notes to objects."""
    
    @factory.lazy_attribute
    def notes(self):
        """Generate detailed notes."""
        return "\n".join([
            factory.Faker('sentence').generate({}),
            factory.Faker('sentence').generate({}),
            factory.Faker('sentence').generate({})
        ])

class WithTrackingHistoryTrait(factory.Trait):
    """Trait to add tracking history to objects."""
    
    @factory.lazy_attribute
    def tracking_history(self):
        """Generate tracking history events."""
        num_events = random.randint(3, 8)
        events = []
        
        base_date = timezone.now() - timedelta(days=random.randint(5, 30))
        
        for i in range(num_events):
            event_date = base_date + timedelta(hours=random.randint(1, 48))
            events.append({
                'timestamp': event_date.isoformat(),
                'status': random.choice(['Created', 'Updated', 'Processed', 'Shipped', 'Delivered']),
                'location': factory.Faker('city').generate({}),
                'user': factory.Faker('user_name').generate({}),
                'notes': factory.Faker('sentence').generate({}) if random.random() > 0.5 else None
            })
            base_date = event_date
            
        # Sort events by timestamp
        events.sort(key=lambda x: x['timestamp'])
        return events

# Helper Functions
def create_order_with_services(customer=None, service_count=None):
    """
    Create an order with associated services for a customer.
    
    Args:
        customer: Customer instance (creates new one if None)
        service_count: Number of services to create (random 1-3 if None)
    
    Returns:
        tuple: (order, customer_services, associated_rules)
    """
    # Create or use customer
    customer = customer or CustomerFactory()
    
    # Create order
    order = OrderFactory(customer=customer)
    
    # Create services
    service_count = service_count or random.randint(1, 3)
    customer_services = []
    rules = []
    
    for i in range(service_count):
        # Create service
        service = ServiceFactory()
        
        # Create customer service
        cs = CustomerServiceFactory(customer=customer, service=service)
        customer_services.append(cs)
        
        # Create rule group with rules
        rule_group = RuleGroupFactory(customer_service=cs)
        
        # Add basic and advanced rules
        basic_rule = RuleFactory(rule_group=rule_group)
        advanced_rule = AdvancedRuleFactory(rule_group=rule_group)
        
        rules.extend([basic_rule, advanced_rule])
    
    return order, customer_services, rules

def create_billing_scenario(orders_count=None):
    """
    Create a complete billing scenario with customer, orders, services, and billing report.
    
    Args:
        orders_count: Number of orders to create (random 1-5 if None)
    
    Returns:
        tuple: (customer, orders, billing_report, billing_details)
    """
    # Create customer
    customer = RealisticCustomerFactory()
    
    # Create orders
    orders_count = orders_count or random.randint(1, 5)
    orders = []
    services = []
    
    for _ in range(orders_count):
        order, customer_services, _ = create_order_with_services(customer=customer)
        orders.append(order)
        services.extend(customer_services)
    
    # Create billing report
    report = BillingReportFactory(customer=customer)
    
    # Create billing details
    details = []
    for order in orders:
        detail = BillingReportDetailFactory(report=report, order=order)
        details.append(detail)
    
    return customer, orders, report, details