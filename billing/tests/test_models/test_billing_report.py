import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, timedelta

from customers.models import Customer
from orders.models import Order
from billing.models import BillingReport, BillingReportDetail

# Use the pytest-django marker to enable database access
pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture
def user():
    """Create a test user for billing tests."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass'
    )

@pytest.fixture
def test_customer():
    """Create a test customer for billing tests."""
    # Use a random suffix to ensure unique email
    import uuid
    random_suffix = str(uuid.uuid4())[:8]
    return Customer.objects.create(
        company_name='Test Company',
        legal_business_name='Test Company LLC',
        email=f'contact_{random_suffix}@example.com',
        phone='123-456-7890'
    )

@pytest.fixture
def test_dates():
    """Return test dates for billing reports."""
    today = timezone.now().date()
    return {
        'today': today,
        'start_date': today - timedelta(days=30),
        'end_date': today - timedelta(days=1)
    }

@pytest.fixture
def report_data():
    """Sample report data for testing."""
    return {
        'orders': [
            {
                'order_id': 'ORD-001',
                'services': [
                    {
                        'service_id': 1,
                        'service_name': 'Shipping',
                        'amount': '10.50'
                    }
                ],
                'total_amount': '10.50'
            }
        ],
        'total_amount': '10.50'
    }
    
def test_create_billing_report(user, test_customer, test_dates, report_data):
    """Test creating a billing report"""
    report = BillingReport.objects.create(
        customer=test_customer,
        start_date=test_dates['start_date'],
        end_date=test_dates['end_date'],
        total_amount=Decimal('10.50'),
        report_data=report_data,
        created_by=user,
        updated_by=user
    )
    
    assert report.customer == test_customer
    assert report.start_date == test_dates['start_date']
    assert report.end_date == test_dates['end_date']
    assert report.total_amount == Decimal('10.50')
    assert report.report_data == report_data
    assert report.created_by == user
    assert report.updated_by == user
    
    # Check auto-populated fields
    assert report.generated_at is not None
    assert report.created_at is not None
    assert report.updated_at is not None

def test_string_representation(test_customer, test_dates, report_data):
    """Test the string representation of a billing report"""
    report = BillingReport.objects.create(
        customer=test_customer,
        start_date=test_dates['start_date'],
        end_date=test_dates['end_date'],
        total_amount=Decimal('10.50'),
        report_data=report_data
    )
    
    expected_str = f"Report for {test_customer.company_name} ({test_dates['start_date']} to {test_dates['end_date']})"
    assert str(report) == expected_str

def test_start_date_after_end_date(test_customer, test_dates, report_data):
    """Test validation fails if start date is after end date"""
    report = BillingReport(
        customer=test_customer,
        start_date=test_dates['end_date'],
        end_date=test_dates['start_date'],
        total_amount=Decimal('10.50'),
        report_data=report_data
    )
    
    with pytest.raises(ValidationError):
        report.full_clean()

def test_future_start_date(test_customer, test_dates, report_data):
    """Test validation fails if start date is in the future"""
    future_date = test_dates['today'] + timedelta(days=1)
    
    report = BillingReport(
        customer=test_customer,
        start_date=future_date,
        end_date=future_date + timedelta(days=1),
        total_amount=Decimal('10.50'),
        report_data=report_data
    )
    
    with pytest.raises(ValidationError):
        report.full_clean()

def test_date_range_too_large(test_customer, test_dates, report_data, settings):
    """Test validation fails if date range is too large"""
    # Set a very large date range
    settings.MAX_REPORT_DATE_RANGE = 10
    report = BillingReport(
        customer=test_customer,
        start_date=test_dates['today'] - timedelta(days=20),
        end_date=test_dates['today'],
        total_amount=Decimal('10.50'),
        report_data=report_data
    )
    
    with pytest.raises(ValidationError):
        report.full_clean()

def test_negative_total_amount(test_customer, test_dates, report_data):
    """Test validation fails if total amount is negative"""
    report = BillingReport(
        customer=test_customer,
        start_date=test_dates['start_date'],
        end_date=test_dates['end_date'],
        total_amount=Decimal('-10.50'),
        report_data=report_data
    )
    
    with pytest.raises(ValidationError):
        report.full_clean()


@pytest.fixture
def test_order(test_customer):
    """Create a test order for billing tests."""
    return Order.objects.create(
        customer=test_customer,
        transaction_id='ORD-001',
        reference_number='REF-001',
        close_date=timezone.now()
    )

@pytest.fixture
def test_billing_report(test_customer, report_data):
    """Create a test billing report."""
    return BillingReport.objects.create(
        customer=test_customer,
        start_date=timezone.now().date() - timedelta(days=30),
        end_date=timezone.now().date() - timedelta(days=1),
        total_amount=Decimal('10.50'),
        report_data=report_data
    )

@pytest.fixture
def service_breakdown():
    """Sample service breakdown for testing."""
    return {
        'services': [
            {
                'service_id': 1,
                'service_name': 'Shipping',
                'amount': '10.50'
            }
        ]
    }

def test_create_billing_report_detail(test_billing_report, test_order, service_breakdown):
    """Test creating a billing report detail"""
    detail = BillingReportDetail.objects.create(
        report=test_billing_report,
        order=test_order,
        service_breakdown=service_breakdown,
        total_amount=Decimal('10.50')
    )
    
    assert detail.report == test_billing_report
    assert detail.order == test_order
    assert detail.service_breakdown == service_breakdown
    assert detail.total_amount == Decimal('10.50')

def test_billing_detail_string_representation(test_billing_report, test_order, service_breakdown):
    """Test the string representation of a billing report detail"""
    detail = BillingReportDetail.objects.create(
        report=test_billing_report,
        order=test_order,
        service_breakdown=service_breakdown,
        total_amount=Decimal('10.50')
    )
    
    expected_str = f"Detail for {test_billing_report} - Order {test_order.transaction_id}"
    assert str(detail) == expected_str

def test_billing_detail_negative_total_amount(test_billing_report, test_order, service_breakdown):
    """Test validation fails if total amount is negative"""
    detail = BillingReportDetail(
        report=test_billing_report,
        order=test_order,
        service_breakdown=service_breakdown,
        total_amount=Decimal('-10.50')
    )
    
    with pytest.raises(ValidationError):
        detail.full_clean()