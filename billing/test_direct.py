"""
Direct test for billing app that combines Django TestCase with pytest features.
This provides more reliable database setup than pure pytest.
"""
import pytest
import json
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import connection

from billing.minimal_test import setup_minimal_tables
from billing.models import BillingReport, BillingReportDetail
from customers.models import Customer

User = get_user_model()


def setup_direct_test_tables():
    """Set up tables needed for direct testing, including orders table mock."""
    with connection.cursor() as cursor:
        # Ensure basic tables exist
        setup_minimal_tables()
        
        # Check and create orders_order table if needed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("orders_order",))
        if not cursor.fetchone()[0]:
            print("Creating simplified orders_order table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders_order (
                    transaction_id INTEGER PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers_customer(id),
                    reference_number VARCHAR(100),
                    ship_to_name VARCHAR(255),
                    ship_to_address VARCHAR(255),
                    ship_to_city VARCHAR(255),
                    ship_to_state VARCHAR(50),
                    ship_to_zip VARCHAR(50),
                    sku_quantity JSONB,
                    total_item_qty INTEGER
                )
            """)
        
        # Check and create billing_billingreportdetail table if needed
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ("billing_billingreportdetail",))
        if not cursor.fetchone()[0]:
            print("Creating billing_billingreportdetail table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS billing_billingreportdetail (
                    id SERIAL PRIMARY KEY,
                    report_id INTEGER REFERENCES billing_billingreport(id) ON DELETE CASCADE,
                    order_id INTEGER,
                    service_breakdown JSONB NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL
                )
            """)


@pytest.mark.django_db
class BillingDirectTest(TestCase):
    """
    Test billing functionality using Django's TestCase for
    reliable database setup combined with pytest markers.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for the whole test case."""
        # Ensure tables exist
        setup_direct_test_tables()
        super().setUpClass()
    
    def setUp(self):
        """Set up test environment."""
        # Create a test user
        self.user = User.objects.create_user(
            username='billing_tester',
            email='billing@test.com',
            password='testpass123'
        )
        
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name='Billing Test Company',
            legal_business_name='Billing Test Company LLC',
            email='billing@example.com',
            phone='123-456-7890'
        )
        
        # Create a mock order directly in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders_order (
                    transaction_id, customer_id, reference_number, 
                    ship_to_name, ship_to_address, ship_to_city, 
                    ship_to_state, ship_to_zip, sku_quantity, total_item_qty
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                12345, self.customer.id, 'REF-12345',
                'Test Recipient', '123 Test St', 'Test City',
                'TS', '12345', json.dumps({
                    'TEST-SKU-1': 5,
                    'TEST-SKU-2': 10
                }), 15
            ])
        
        # Create a reference to the order
        class MockOrder:
            def __init__(self, transaction_id):
                self.transaction_id = transaction_id
        
        self.order = MockOrder(12345)
    
    def test_create_billing_report(self):
        """Test that a billing report can be created."""
        # Create test data
        start_date = timezone.now().date()
        end_date = start_date
        
        # Create billing report
        report = BillingReport.objects.create(
            customer=self.customer,
            start_date=start_date,
            end_date=end_date,
            total_amount=Decimal('150.00'),
            report_data={
                'orders': [
                    {
                        'order_id': self.order.transaction_id,
                        'services': [
                            {
                                'service_id': 1,
                                'service_name': 'Test Service',
                                'amount': '150.00'
                            }
                        ],
                        'total_amount': '150.00'
                    }
                ],
                'service_totals': {
                    '1': {
                        'name': 'Test Service',
                        'amount': '150.00'
                    }
                },
                'total_amount': '150.00'
            },
            created_by=self.user,
            updated_by=self.user
        )
        
        # Test that the report was created
        self.assertEqual(BillingReport.objects.count(), 1)
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.total_amount, Decimal('150.00'))
        self.assertEqual(report.created_by, self.user)
        
        # Test report data
        self.assertIn('orders', report.report_data)
        self.assertIn('service_totals', report.report_data)
        self.assertEqual(report.report_data['total_amount'], '150.00')
    
    def test_create_billing_report_detail(self):
        """Test that billing report details can be created."""
        # Create a billing report
        report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            total_amount=Decimal('150.00'),
            report_data={},
            created_by=self.user,
            updated_by=self.user
        )
        
        # Create a billing report detail
        detail = BillingReportDetail.objects.create(
            report=report,
            order_id=self.order.transaction_id,  # Use ID instead of object
            service_breakdown={
                '1': {
                    'name': 'Test Service',
                    'amount': '150.00'
                }
            },
            total_amount=Decimal('150.00')
        )
        
        # Test that the detail was created
        self.assertEqual(BillingReportDetail.objects.count(), 1)
        self.assertEqual(detail.report, report)
        self.assertEqual(detail.order_id, self.order.transaction_id)
        self.assertEqual(detail.total_amount, Decimal('150.00'))
        self.assertIn('1', detail.service_breakdown)