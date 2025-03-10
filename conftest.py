import pytest
import os
import sys
import json
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.db import connections, connection
from django.utils import timezone
import factory

# Only import testcontainers if not in Docker environment
try:
    from testcontainers.postgres import PostgresContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False


def is_sqlite_in_memory_db():
    """Check if we are using an in-memory database."""
    database_name = settings.DATABASES['default']['NAME']
    return (database_name == ':memory:' or 
            'mode=memory' in database_name or 
            database_name.startswith('file:memorydb'))


def is_postgresql_db():
    """Check if we are using a PostgreSQL database."""
    return settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'


def should_use_testcontainers():
    """Check if we should use TestContainers for database setup."""
    # Don't use TestContainers if we're in Docker or if it's not available
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true'
    use_testcontainers = (
        is_postgresql_db() and 
        os.environ.get('USE_TESTCONTAINERS', 'True').lower() == 'true' and
        not in_docker and
        TESTCONTAINERS_AVAILABLE
    )
    return use_testcontainers


@pytest.fixture(scope='session')
def postgres_container():
    """
    Fixture that provides a PostgreSQL container.
    The container is started when this fixture is first requested
    and stopped at the end of the test session.
    """
    if not should_use_testcontainers():
        # Skip TestContainers if not needed
        print("TestContainers not used - using existing database connection.")
        yield None
        return
    
    # TestContainers implementation
    try:
        # Define container configuration - match version in docker-compose.test.yml
        postgres_container = PostgresContainer(
            image="postgres:15",
            username="postgres",
            password="postgres",
            dbname="ledgerlink_test",
            port=5432
        )
        
        # Start the container
        print("Starting PostgreSQL container with TestContainers...")
        postgres_container.start()
        
        # Save the connection information for the Django fixture
        os.environ['TC_DB_NAME'] = postgres_container.dbname
        os.environ['TC_DB_USER'] = postgres_container.username
        os.environ['TC_DB_PASSWORD'] = postgres_container.password
        os.environ['TC_DB_HOST'] = postgres_container.get_container_host_ip()
        os.environ['TC_DB_PORT'] = str(postgres_container.get_exposed_port(5432))
        
        print(f"TestContainers PostgreSQL running at: {os.environ['TC_DB_HOST']}:{os.environ['TC_DB_PORT']}")
        
        # Make container available to tests
        yield postgres_container
        
        # Stop container when tests are done
        print("Stopping PostgreSQL container...")
        postgres_container.stop()
        print("PostgreSQL container stopped.")
    except Exception as e:
        print(f"Error setting up TestContainers: {e}")
        yield None


@pytest.fixture(scope='session')
def django_db_setup(request, postgres_container):
    """
    This fixture completely replaces the default django_db_setup fixture 
    provided by pytest-django.
    
    It sets up the database using create_model() to directly create tables 
    without running migrations. For PostgreSQL, it also creates materialized views
    and other PostgreSQL-specific objects.
    """
    from django.db import connection, connections
    from django.apps import apps
    
    # Check if we're in Docker
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == 'true'
    
    # If in Docker, use the existing database configuration
    if in_docker:
        print("Using Docker database configuration")
        # Nothing to do - settings are already configured by docker-compose
        pass
    # If using TestContainers, configure Django to use the container's connection details
    elif should_use_testcontainers() and postgres_container:
        print("Using TestContainers database configuration")
        # Update Django's database configuration
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['TC_DB_NAME'],
            'USER': os.environ['TC_DB_USER'],
            'PASSWORD': os.environ['TC_DB_PASSWORD'],
            'HOST': os.environ['TC_DB_HOST'],
            'PORT': os.environ['TC_DB_PORT'],
            'ATOMIC_REQUESTS': True,
        }
        
        # Close any existing connections and reconnect with new settings
        for conn in connections.all():
            conn.close()
    
    # When not in Docker, we need to set up the database schema
    if not in_docker:
        # Apply migrations using Django's migration executor
        from django.core.management import call_command
        from django.db.migrations.executor import MigrationExecutor
        
        print("Applying migrations for test database...")
        try:
            # First method: Using migration executor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                print(f"Applying {len(plan)} pending migrations...")
                executor.migrate(executor.loader.graph.leaf_nodes())
                print("Migrations applied successfully")
            else:
                print("No migrations to apply")
            
            # Force pre-created ContentType creation
            from django.contrib.contenttypes.models import ContentType
            ContentType.objects.clear_cache()
            
            # Verify database schema matches models
            print("Verifying database schema...")
            try:
                from django.db import models
                from customers.models import Customer
                
                # Verify critical fields exist
                with connection.cursor() as cursor:
                    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'customers_customer'")
                    columns = [row[0] for row in cursor.fetchall()]
                    
                    # Check for is_active field
                    if 'is_active' not in columns:
                        print("WARNING: 'is_active' field not found in customers_customer table!")
                        print(f"Available columns: {', '.join(columns)}")
                        print("Using second method: call_command to apply migrations...")
                        call_command('migrate', interactive=False, verbosity=1)
            except Exception as e:
                print(f"Schema verification error: {e}")
                print("Using second method: call_command to apply migrations...")
                call_command('migrate', interactive=False, verbosity=1)
        except Exception as e:
            print(f"Migration application error: {e}")
            print("Using fallback method: call_command to apply migrations...")
            call_command('migrate', interactive=False, verbosity=1)
        
        # If using PostgreSQL, create materialized views and other PostgreSQL-specific objects
        create_materialized_views = os.environ.get('SKIP_MATERIALIZED_VIEWS') != 'True'
        if is_postgresql_db() and create_materialized_views:
            print("PostgreSQL detected - creating materialized views and other PostgreSQL-specific objects")
            try:
                # Execute SQL from test_postgresql_objects.sql
                sql_file_path = os.path.join(settings.BASE_DIR, 'tests', 'test_postgresql_objects.sql')
                if os.path.exists(sql_file_path):
                    with open(sql_file_path, 'r') as f:
                        sql = f.read()
                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                    print("Successfully created PostgreSQL-specific objects")
                else:
                    print(f"WARNING: Could not find {sql_file_path}")
            except Exception as e:
                print(f"Failed to create PostgreSQL-specific objects: {e}")
        elif is_postgresql_db():
            print("Skipping materialized view creation for tests (SKIP_MATERIALIZED_VIEWS=True)")


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def admin_user():
    User = get_user_model()
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword'
    )
    return user


@pytest.fixture
def authenticated_client(client, admin_user):
    client.force_login(admin_user)
    return client

# Shared Factory classes for consistent test data across all apps

class CustomerFactory(factory.django.DjangoModelFactory):
    """Factory for creating Customer instances with unique emails"""
    
    class Meta:
        model = 'customers.Customer'
    
    company_name = factory.Sequence(lambda n: f"Test Company {n}")
    legal_business_name = factory.Sequence(lambda n: f"Test Company {n} LLC")
    email = factory.Sequence(lambda n: f"test{n}@example.com")
    phone = factory.Sequence(lambda n: f"555-123-{n:04d}")
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip = factory.Faker('zipcode')
    country = 'US'
    business_type = factory.Iterator(['Retail', 'Manufacturing', 'Distribution', 'Service'])
    is_active = True

class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for creating Order instances with numeric transaction IDs"""
    
    class Meta:
        model = 'orders.Order'
    
    # Required fields
    transaction_id = factory.Sequence(lambda n: 100000 + n)  # Use a simple integer sequence
    customer = factory.SubFactory(CustomerFactory)
    reference_number = factory.Sequence(lambda n: f"ORD-{n:06d}")
    
    # Optional fields with defaults
    status = 'draft'
    priority = 'medium'
    close_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    
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
    total_item_qty = factory.LazyFunction(lambda: random.randint(1, 100))
    volume_cuft = factory.LazyFunction(lambda: round(random.uniform(1, 50), 2))
    packages = factory.LazyFunction(lambda: random.randint(1, 10))
    notes = factory.Faker('paragraph')
    carrier = factory.Iterator(['FedEx', 'UPS', 'USPS', 'DHL'])
    
    # Generate random SKU quantities
    @factory.lazy_attribute
    def sku_quantity(self):
        num_skus = random.randint(1, 5)
        skus = {f"SKU-{i:04d}": random.randint(1, 20) for i in range(num_skus)}
        return skus
    
    # Set line_items based on sku_quantity
    @factory.lazy_attribute
    def line_items(self):
        return len(self.sku_quantity) if self.sku_quantity else 0

class ServiceFactory(factory.django.DjangoModelFactory):
    """Factory for creating Service instances"""
    
    class Meta:
        model = 'services.Service'
    
    service_name = factory.Sequence(lambda n: f"Test Service {n}")
    description = factory.Faker('sentence')
    charge_type = factory.Iterator(['fixed', 'per_unit', 'tiered', 'case_based_tier'])
    
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances"""
    
    class Meta:
        model = get_user_model()
    
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

class CustomerServiceFactory(factory.django.DjangoModelFactory):
    """Factory for creating CustomerService instances"""
    
    class Meta:
        model = 'customer_services.CustomerService'
    
    customer = factory.SubFactory(CustomerFactory)
    service = factory.SubFactory(ServiceFactory)
    unit_price = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 1000), 2))))
    is_active = True

class BillingReportFactory(factory.django.DjangoModelFactory):
    """Factory for creating BillingReport instances"""
    
    class Meta:
        model = 'billing.BillingReport'
    
    customer = factory.SubFactory(CustomerFactory)
    start_date = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=30))
    end_date = factory.LazyFunction(lambda: timezone.now().date())
    total_amount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(100, 5000), 2))))
    
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
                    'service_name': f'Test Service {j + 1}',
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
                '1': {'name': 'Test Service 1', 'amount': str(Decimal('100.00'))},
                '2': {'name': 'Test Service 2', 'amount': str(Decimal('200.00'))},
                '3': {'name': 'Test Service 3', 'amount': str(Decimal('300.00'))}
            }
        }
    
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

class BillingReportDetailFactory(factory.django.DjangoModelFactory):
    """Factory for creating BillingReportDetail instances"""
    
    class Meta:
        model = 'billing.BillingReportDetail'
    
    report = factory.SubFactory(BillingReportFactory)
    order = factory.SubFactory(OrderFactory)
    
    @factory.lazy_attribute
    def service_breakdown(self):
        services = []
        total = Decimal('0.00')
        
        for i in range(1, 4):
            amount = Decimal(str(round(random.uniform(10, 200), 2)))
            services.append({
                'service_id': i,
                'service_name': f'Test Service {i}',
                'amount': str(amount)
            })
            total += amount
        
        return {'services': services}
    
    total_amount = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 1000), 2))))


@pytest.fixture
def test_customer():
    """Create a test customer with unique email."""
    # Use a random suffix to ensure unique email
    random_suffix = str(uuid.uuid4())[:8]
    return CustomerFactory(email=f'customer_{random_suffix}@example.com')

@pytest.fixture
def test_service():
    """Create a test service."""
    return ServiceFactory()

@pytest.fixture
def test_order(test_customer):
    """Create a test order with numeric transaction ID."""
    return OrderFactory(customer=test_customer)

@pytest.fixture
def test_customer_service(test_customer, test_service):
    """Create a test customer service relationship."""
    return CustomerServiceFactory(customer=test_customer, service=test_service)

@pytest.fixture
def test_billing_report(test_customer, admin_user):
    """Create a test billing report."""
    return BillingReportFactory(
        customer=test_customer,
        created_by=admin_user,
        updated_by=admin_user
    )

@pytest.fixture
def test_billing_report_detail(test_billing_report, test_order):
    """Create a test billing report detail."""
    return BillingReportDetailFactory(
        report=test_billing_report,
        order=test_order
    )

# Define helper methods for order models
@pytest.fixture(autouse=False)
def add_case_methods_to_order(monkeypatch):
    """
    Add methods to Order for case-based calculations during tests.
    Not auto-applied to avoid conflicting with existing methods.
    """
    # Only import Order here to avoid circular imports
    from orders.models import Order
    
    def get_case_summary(self, exclude_skus=None):
        """Get case summary for the order."""
        try:
            if not hasattr(self, 'sku_quantity') or not self.sku_quantity:
                return {"total_cases": 0, "total_picks": 0, "sku_breakdown": []}
                
            # Handle both string and dict formats
            if isinstance(self.sku_quantity, str):
                try:
                    skus = json.loads(self.sku_quantity)
                except json.JSONDecodeError:
                    return {"total_cases": 0, "total_picks": 0, "sku_breakdown": []}
            else:
                skus = self.sku_quantity
                
            excluded = set(exclude_skus or [])
            sku_cases = {}
            total_cases = 0
            total_picks = 0
            
            # Format could be a list of dicts or a dict with SKUs as keys
            if isinstance(skus, list):
                for item in skus:
                    sku = item.get('sku', '')
                    if sku and sku not in excluded:
                        # Default to 1 case per 10 items
                        quantity = float(item.get('quantity', 0))
                        cases = int(quantity / 10)
                        picks = quantity % 10
                        
                        if cases > 0 or picks > 0:
                            sku_cases[sku] = {'cases': cases, 'picks': picks}
                            total_cases += cases
                            total_picks += picks
            elif isinstance(skus, dict):
                for sku, data in skus.items():
                    if sku not in excluded:
                        if isinstance(data, dict):
                            cases = data.get('cases', 0)
                            picks = data.get('picks', 0)
                        else:
                            # Default to 1 case per 10 items
                            quantity = float(data)
                            cases = int(quantity / 10)
                            picks = quantity % 10
                        
                        if cases > 0 or picks > 0:
                            sku_cases[sku] = {'cases': cases, 'picks': picks}
                            total_cases += cases
                            total_picks += picks
                    
            return {
                "total_cases": total_cases,
                "total_picks": total_picks,
                "sku_breakdown": [
                    {
                        "sku_name": sku,
                        "cases": data['cases'],
                        "picks": data['picks'],
                        "case_size": 10,
                        "case_unit": "each"
                    } 
                    for sku, data in sku_cases.items()
                ]
            }
        except Exception as e:
            print(f"Error in get_case_summary: {e}")
            return {"total_cases": 0, "total_picks": 0, "sku_breakdown": []}
    
    def get_total_cases(self, exclude_skus=None):
        """Get total cases across all SKUs"""
        summary = self.get_case_summary(exclude_skus)
        return summary.get("total_cases", 0)
    
    def get_total_picks(self, exclude_skus=None):
        """Get total picks across all SKUs"""
        summary = self.get_case_summary(exclude_skus)
        return summary.get("total_picks", 0)
    
    def has_only_excluded_skus(self, exclude_skus):
        """Check if order has only excluded SKUs."""
        if not exclude_skus:
            return False
            
        try:
            if not hasattr(self, 'sku_quantity') or not self.sku_quantity:
                return False
                
            # Handle both string and list formats
            if isinstance(self.sku_quantity, str):
                try:
                    skus = json.loads(self.sku_quantity)
                except json.JSONDecodeError:
                    return False
            else:
                skus = self.sku_quantity
                
            excluded = set(exclude_skus)
            
            # Format could be a list of dicts or a dict with SKUs as keys
            if isinstance(skus, list):
                return all(item.get('sku', '') in excluded for item in skus)
            elif isinstance(skus, dict):
                return all(sku in excluded for sku in skus.keys())
                
            return False
        except Exception as e:
            print(f"Error in has_only_excluded_skus: {e}")
            return False
    
    # Add methods to Order model
    monkeypatch.setattr(Order, "get_case_summary", get_case_summary)
    monkeypatch.setattr(Order, "get_total_cases", get_total_cases)
    monkeypatch.setattr(Order, "get_total_picks", get_total_picks)
    monkeypatch.setattr(Order, "has_only_excluded_skus", has_only_excluded_skus)

@pytest.fixture(scope='function')
def _django_db_helper(request, django_db_setup, django_db_blocker):
    """
    This fixture is used by pytest-django to provide database access for tests.
    Specifically for TestContainers, this ensures database is properly set up.
    """
    django_db_blocker.unblock()
    try:
        yield
    finally:
        django_db_blocker.restore()