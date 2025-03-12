"""
Minimal test for billing app functionality.
This test is designed to run with minimal database setup to verify basic app functionality.
"""
import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from django.db import connection

from customers.models import Customer
from billing.models import BillingReport, BillingReportDetail

# Import factories
from tests.factories import (
    UserFactory, AdminUserFactory, 
    CustomerFactory, 
    BillingReportFactory, BillingReportDetailFactory,
    create_billing_scenario
)

User = get_user_model()

# Function to verify or create required tables directly
def setup_minimal_tables():
    """Verify or create the minimal required tables for tests."""
    with connection.cursor() as cursor:
        # Check and create auth_user table if needed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("auth_user",))
        if not cursor.fetchone()[0]:
            print("Creating auth_user table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    password VARCHAR(128) NOT NULL,
                    email VARCHAR(254) NOT NULL,
                    first_name VARCHAR(150) NOT NULL,
                    last_name VARCHAR(150) NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    is_staff BOOLEAN NOT NULL,
                    is_superuser BOOLEAN NOT NULL,
                    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
                    last_login TIMESTAMP WITH TIME ZONE NULL
                )
            """)
        
        # Check and create customers_customer table if needed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("customers_customer",))
        if not cursor.fetchone()[0]:
            print("Creating customers_customer table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers_customer (
                    id SERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    legal_business_name VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    address VARCHAR(255),
                    city VARCHAR(100),
                    state VARCHAR(50),
                    zip VARCHAR(20),
                    country VARCHAR(50) DEFAULT 'US',
                    business_type VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
        
        # Check and create billing_billingreport table if needed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("billing_billingreport",))
        if not cursor.fetchone()[0]:
            print("Creating billing_billingreport table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS billing_billingreport (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers_customer(id),
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    report_data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    created_by_id INTEGER NULL,
                    updated_by_id INTEGER NULL,
                    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
        
        # Check and create billing_billingreportdetail table if needed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("billing_billingreportdetail",))
        if not cursor.fetchone()[0]:
            print("Creating billing_billingreportdetail table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS billing_billingreportdetail (
                    id SERIAL PRIMARY KEY,
                    report_id INTEGER REFERENCES billing_billingreport(id),
                    order_id INTEGER NOT NULL,
                    service_breakdown JSONB NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL
                )
            """)


class MinimalBillingTest(TestCase):
    """
    Minimal test case for billing functionality.
    Uses Django's TestCase for reliable database setup.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for the whole test case."""
        # Ensure tables exist
        setup_minimal_tables()
        super().setUpClass()
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name='Test Company',
            legal_business_name='Test Company LLC',
            email='contact@test.com',
            phone='123-456-7890'
        )
    
    def test_create_billing_report(self):
        """Test that we can create a basic billing report."""
        # Create a simple report
        report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            total_amount=Decimal('100.00'),
            report_data={},
            created_by=self.user,
            updated_by=self.user
        )
        
        # Verify it was created
        self.assertEqual(BillingReport.objects.count(), 1)
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.total_amount, Decimal('100.00'))
        self.assertEqual(report.created_by, self.user)


# For pytest compatibility
@pytest.mark.django_db
def test_create_billing_report_pytest(django_db_setup):
    """Test creating a billing report using pytest."""
    # Ensure tables exist
    setup_minimal_tables()
    
    # Create test user
    user = User.objects.create_user(
        username='testuser_pytest',
        email='pytest@example.com',
        password='password123'
    )
    
    # Create test customer
    customer = Customer.objects.create(
        company_name='Pytest Company',
        legal_business_name='Pytest Company LLC',
        email='contact@pytest.com',
        phone='123-456-7890'
    )
    
    # Create a simple report
    report = BillingReport.objects.create(
        customer=customer,
        start_date=timezone.now().date(),
        end_date=timezone.now().date(),
        total_amount=Decimal('100.00'),
        report_data={},
        created_by=user,
        updated_by=user
    )
    
    # Verify it was created
    assert BillingReport.objects.count() >= 1
    assert report.customer == customer
    assert report.total_amount == Decimal('100.00')
    assert report.created_by == user


class BillingFactoryTest(TestCase):
    """
    Test case using the factory classes to test billing functionality.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for the whole test case."""
        # Ensure tables exist
        setup_minimal_tables()
        super().setUpClass()
    
    def test_create_billing_report_with_factory(self):
        """Test creating a billing report using the factory."""
        # Create a user using the factory
        user = UserFactory()
        
        # Create a customer using the factory
        customer = CustomerFactory()
        
        # Create a billing report using the factory
        report = BillingReportFactory(
            customer=customer,
            created_by=user,
            updated_by=user,
            total_amount=Decimal('500.00')
        )
        
        # Verify it was created correctly
        self.assertEqual(report.customer, customer)
        self.assertEqual(report.created_by, user)
        self.assertEqual(report.updated_by, user)
        self.assertEqual(report.total_amount, Decimal('500.00'))
        
        # Verify report_data structure
        self.assertIn('orders', report.report_data)
        self.assertIn('total_amount', report.report_data)
        self.assertIn('service_totals', report.report_data)
    
    def test_create_billing_scenario(self):
        """Test creating a complete billing scenario with the helper function."""
        # Create a billing scenario with 3 orders
        customer, orders, report, details = create_billing_scenario(orders_count=3)
        
        # Verify the scenario was created correctly
        self.assertEqual(len(orders), 3)
        self.assertEqual(len(details), 3)
        
        # Verify relationships
        for order in orders:
            self.assertEqual(order.customer, customer)
        
        self.assertEqual(report.customer, customer)
        
        for detail in details:
            self.assertEqual(detail.report, report)
            self.assertIn(detail.order, orders)
            
            # Verify service breakdown structure
            self.assertIn('services', detail.service_breakdown)
            self.assertTrue(len(detail.service_breakdown['services']) > 0)


# For pytest compatibility
@pytest.mark.django_db
def test_billing_factory_pytest(django_db_setup):
    """Test the billing factory using pytest."""
    # Ensure tables exist
    setup_minimal_tables()
    
    # Create a billing report using the factory
    report = BillingReportFactory()
    
    # Verify it was created correctly
    assert report.id is not None
    assert report.customer is not None
    assert report.total_amount > 0
    
    # Create a billing report detail
    detail = BillingReportDetailFactory(report=report)
    
    # Verify it was created correctly
    assert detail.id is not None
    assert detail.report == report
    assert detail.order is not None
    assert detail.total_amount > 0