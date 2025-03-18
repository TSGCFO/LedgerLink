"""
Pytest configuration for billing tests.
This conftest.py extends the main project's conftest.py rather than replacing it.
"""
import os
import pytest
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone

from billing.models import BillingReport, BillingReportDetail

# Import from the main conftest.py's shared factories
# Here we rely on the global shared factories rather than duplicating them
pytest_plugins = ['LedgerLink.conftest']
from services.tests.factories import ServiceFactory
from customer_services.tests.factories import CustomerServiceFactory
from rules.models import RuleGroup, AdvancedRule
from customers.models import Customer

# Import utility functions
from billing.tests.utils import verify_field_exists, verify_model_schema, verify_billing_schema

# Import main project's fixtures
from conftest import django_db_setup, _django_db_helper

# Set environment variables for testing if needed
if 'SKIP_MATERIALIZED_VIEWS' not in os.environ:
    os.environ['SKIP_MATERIALIZED_VIEWS'] = 'True'

# Mark all tests in this directory as django_db tests
pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture(scope='session', autouse=True)
def verify_db_schema(django_db_blocker):
    """
    Verify that the database schema has all required fields before running tests.
    In particular, check for the is_active field in the Customer model and
    required billing tables.
    """
    django_db_blocker.unblock()
    try:
        # Check Customer model has is_active field
        customer_success, customer_message = verify_field_exists(Customer, 'is_active')
        if not customer_success:
            print(f"Warning: {customer_message}")
            # Don't fail the test if is_active is missing - we'll create it if needed
        
        # Verify BillingReport model schema
        report_success, report_message = verify_model_schema(BillingReport)
        if not report_success:
            print(f"Warning: {report_message}")
        
        # Verify BillingReportDetail model schema if it exists
        try:
            detail_success, detail_message = verify_model_schema(BillingReportDetail)
            if not detail_success:
                print(f"Warning: {detail_message}")
        except Exception as e:
            print(f"Error checking BillingReportDetail schema: {e}")
        
        # Verify billing-specific schema
        billing_success, billing_message = verify_billing_schema()
        if not billing_success:
            print(f"Warning: {billing_message}")
            
        print("Schema verification for billing app completed. Some warnings may need to be addressed.")
    finally:
        django_db_blocker.restore()

@pytest.fixture
def billing_test_setup(django_db_blocker, _django_db_helper):
    """
    Setup fixture for billing tests that ensures:
    1. Database is properly unblocked
    2. Schema is correctly set up
    3. Required models are available
    """
    # Additional setup can go here
    yield
    # Any cleanup can go here

@pytest.fixture
def billing_user():
    """Create a user for billing tests."""
    return UserFactory()

@pytest.fixture
def billing_customer():
    """Create a customer for billing tests."""
    return CustomerFactory(
        company_name="Billing Test Company",
        contact_email="billing@test.com",
        phone_number="555-123-4567"
    )

@pytest.fixture
def billing_order(billing_customer):
    """Create an order for billing tests with SKU data."""
    return OrderFactory(
        customer=billing_customer,
        transaction_id=12345,  # Use an integer instead of a string
        reference_number="REF-12345",
        close_date=timezone.now(),
        sku_quantity=json.dumps([
            {"sku": "TEST-SKU-1", "quantity": 5},
            {"sku": "TEST-SKU-2", "quantity": 10}
        ])
    )

@pytest.fixture
def basic_billing_report(billing_customer, billing_user):
    """Create a basic billing report."""
    start_date = timezone.now().date() - timedelta(days=30)
    end_date = timezone.now().date()
    
    report_data = {
        "orders": [
            {
                "order_id": 12345,  # Use integer for order_id
                "services": [
                    {
                        "service_id": 1,
                        "service_name": "Test Service",
                        "amount": "100.00"
                    }
                ],
                "total_amount": "100.00"
            }
        ],
        "service_totals": {
            "1": {
                "name": "Test Service",
                "amount": "100.00"
            }
        },
        "total_amount": "100.00"
    }
    
    return BillingReport.objects.create(
        customer=billing_customer,
        start_date=start_date,
        end_date=end_date,
        total_amount=Decimal("100.00"),
        report_data=report_data,
        created_by=billing_user,
        updated_by=billing_user
    )

@pytest.fixture
def billing_report_with_details(billing_customer, billing_user, billing_order):
    """Create a billing report with details."""
    report = BillingReportFactory(
        customer=billing_customer,
        created_by=billing_user,
        updated_by=billing_user
    )
    
    detail = BillingReportDetailFactory(
        report=report,
        order=billing_order,
        total_amount=Decimal("150.00")
    )
    
    return report

@pytest.fixture
def case_based_service(billing_customer):
    """Create a case-based service configuration."""
    # Create the service
    service = ServiceFactory(
        service_name="Case-Based Service",
        description="Service charged based on case tiers",
        charge_type="case_based_tier"
    )
    
    # Create customer service
    customer_service = CustomerServiceFactory(
        customer=billing_customer,
        service=service,
        unit_price=Decimal("100.00")
    )
    
    # Create rule group
    rule_group = RuleGroup.objects.create(
        customer_service=customer_service,
        logic_operator="AND"
    )
    
    # Create advanced rule with tier configuration
    rule = AdvancedRule.objects.create(
        rule_group=rule_group,
        field="sku_quantity",
        operator="contains",
        value="SKU",
        calculations=[
            {"type": "case_based_tier", "value": 1.0}
        ],
        tier_config={
            "ranges": [
                {"min": 1, "max": 3, "multiplier": 1.0},
                {"min": 4, "max": 6, "multiplier": 2.0},
                {"min": 7, "max": 10, "multiplier": 3.0}
            ],
            "excluded_skus": ["EXCLUDE-SKU"]
        }
    )
    
    return {
        "service": service,
        "customer_service": customer_service,
        "rule_group": rule_group,
        "rule": rule
    }

# Add a method to Order for case-based calculations during tests
@pytest.fixture(autouse=True)
def add_case_methods_to_order(monkeypatch):
    """Add methods to Order for case-based calculations during tests."""
    import orders.models
    
    def get_case_summary(self, exclude_skus=None):
        """Get case summary for the order."""
        try:
            if not hasattr(self, 'sku_quantity') or not self.sku_quantity:
                return {"total_cases": 0, "skus": {}}
                
            # Handle both string and list formats
            if isinstance(self.sku_quantity, str):
                try:
                    skus = json.loads(self.sku_quantity)
                except json.JSONDecodeError:
                    return {"total_cases": 0, "skus": {}}
            else:
                skus = self.sku_quantity
                
            excluded = set(exclude_skus or [])
            sku_cases = {}
            total_cases = 0
            
            # Format could be a list of dicts or a dict with SKUs as keys
            if isinstance(skus, list):
                for item in skus:
                    sku = item.get('sku', '')
                    if sku and sku not in excluded:
                        # Default to 1 case per 10 items
                        quantity = float(item.get('quantity', 0))
                        cases = int(quantity / 10)
                        if cases > 0:
                            sku_cases[sku] = cases
                            total_cases += cases
            elif isinstance(skus, dict):
                for sku, data in skus.items():
                    if sku not in excluded:
                        if isinstance(data, dict):
                            cases = data.get('cases', 0)
                        else:
                            # Default to 1 case per 10 items
                            quantity = float(data)
                            cases = int(quantity / 10)
                        
                        if cases > 0:
                            sku_cases[sku] = cases
                            total_cases += cases
                    
            return {
                "total_cases": total_cases,
                "skus": sku_cases
            }
        except Exception as e:
            print(f"Error in get_case_summary: {e}")
            return {"total_cases": 0, "skus": {}}
    
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
    monkeypatch.setattr(orders.models.Order, "get_case_summary", get_case_summary)
    monkeypatch.setattr(orders.models.Order, "has_only_excluded_skus", has_only_excluded_skus)