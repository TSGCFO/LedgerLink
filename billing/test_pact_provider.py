"""
Pact provider tests for the billing API.

These tests verify that the billing API fulfills the contract
expected by the frontend application. The contract is defined
by the consumer (frontend) in the billing.pact.test.js file.
"""

import json
import logging
import os
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from billing.models import BillingReport
from billing.services import BillingReportService
from customers.models import Customer
from services.models import Service
from customer_services.models import CustomerService
from orders.models import Order

# Try to import pact libraries, but don't fail if not available
try:
    from pact import Verifier
    HAS_PACT = True
except (ImportError, ModuleNotFoundError):
    HAS_PACT = False

logger = logging.getLogger(__name__)

# Paths and configuration for PACT
PACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'pact')
PACT_FILE = os.path.join(PACT_DIR, 'pacts', 'react-app-billing-api.json')
PACT_BROKER_URL = os.environ.get('PACT_BROKER_URL', 'http://localhost:9292')
PROVIDER_NAME = 'billing-api'
PROVIDER_URL = os.environ.get('PROVIDER_URL', 'http://localhost:8000')


@pytest.mark.skipif(not HAS_PACT, reason="Pact library not available")
@pytest.mark.pact
class TestBillingPactProvider:
    """Test the billing API as a PACT provider."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class."""
        # Set up API client
        cls.client = APIClient()
        # Create and authenticate a user
        cls.user = User.objects.create_user(
            username='pactuser',
            email='pact@example.com',
            password='pactpassword',
            is_staff=True
        )
        cls.client.force_authenticate(user=cls.user)
        
    def setup_method(self, method):
        """Set up for each test method."""
        # Create test data
        self.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Company LLC",
            email="test@example.com"
        )
        
        # Create services
        self.service = Service.objects.create(
            service_name="Test Service",
            description="Service for testing",
            charge_type="single"
        )
        
        # Create customer service
        self.cs = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('25.00')
        )
        
        # Create orders
        today = datetime.now().date()
        self.order = Order.objects.create(
            customer=self.customer,
            transaction_id="TEST-001",
            transaction_date=today,
            close_date=today,
            ship_to_name="Test Person",
            ship_to_address="123 Test St",
            total_item_qty=1
        )
        
        # Create a billing report
        self.report = BillingReport.objects.create(
            customer=self.customer,
            start_date=today - timedelta(days=30),
            end_date=today,
            total_amount=Decimal('25.00'),
            report_data={
                'customer_id': self.customer.id,
                'start_date': (today - timedelta(days=30)).isoformat(),
                'end_date': today.isoformat(),
                'orders': [
                    {
                        'order_id': "TEST-001",
                        'services': [
                            {
                                'service_id': self.service.id,
                                'service_name': "Test Service",
                                'amount': "25.00"
                            }
                        ],
                        'total_amount': "25.00"
                    }
                ],
                'service_totals': {
                    str(self.service.id): {
                        'name': "Test Service",
                        'amount': "25.00"
                    }
                },
                'total_amount': "25.00"
            },
            created_by=self.user,
            updated_by=self.user
        )
        
    def teardown_method(self, method):
        """Clean up after each test method."""
        # Clean up all test data
        BillingReport.objects.all().delete()
        Order.objects.all().delete()
        CustomerService.objects.all().delete()
        Service.objects.all().delete()
        Customer.objects.all().delete()
    
    def test_get_billing_reports_list(self):
        """Test GET request to billing reports list endpoint."""
        # Create additional reports
        today = datetime.now().date()
        for i in range(2):
            BillingReport.objects.create(
                customer=self.customer,
                start_date=today - timedelta(days=15),
                end_date=today,
                total_amount=Decimal('15.00'),
                report_data={'test': f'data-{i}'},
                created_by=self.user,
                updated_by=self.user
            )
        
        # Make the request
        url = reverse('billing:report_list')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] is True
        
        # The response data should include all reports
        assert len(response_data['data']) == 3  # Original report + 2 new ones
        
        # Verify the report data
        for report in response_data['data']:
            assert 'id' in report
            assert 'customer' in report
            assert 'customer_name' in report
            assert 'start_date' in report
            assert 'end_date' in report
            assert 'total_amount' in report
            assert 'generated_at' in report
    
    def test_get_billing_reports_with_filter(self):
        """Test GET request to billing reports list endpoint with filters."""
        # Create a different customer with reports
        customer2 = Customer.objects.create(
            company_name="Another Company",
            email="another@example.com"
        )
        
        # Create additional reports for different customers
        today = datetime.now().date()
        for customer in [self.customer, customer2]:
            BillingReport.objects.create(
                customer=customer,
                start_date=today - timedelta(days=15),
                end_date=today,
                total_amount=Decimal('15.00'),
                report_data={'test': 'data'},
                created_by=self.user,
                updated_by=self.user
            )
        
        # Make the request with customer filter
        url = f"{reverse('billing:report_list')}?customer={self.customer.id}"
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] is True
        
        # Should only include reports for the requested customer
        assert len(response_data['data']) == 2  # Original report + 1 new one
        for report in response_data['data']:
            assert report['customer'] == self.customer.id
        
        # Make the request with date filter
        yesterday = (today - timedelta(days=1)).isoformat()
        url = f"{reverse('billing:report_list')}?start_date={yesterday}"
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] is True
        
        # All reports have start dates older than yesterday, so none should match
        assert len(response_data['data']) == 0
    
    def test_get_billing_report_by_id(self):
        """Test GET request to specific billing report endpoint."""
        # Make the request
        url = reverse('billing:report_detail', kwargs={'pk': self.report.id})
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['id'] == str(self.report.id)
        assert response_data['customer'] == self.customer.id
        assert response_data['customer_name'] == self.customer.company_name
        assert Decimal(response_data['total_amount']) == self.report.total_amount
    
    def test_generate_billing_report(self):
        """Test POST request to generate a billing report."""
        # Prepare the request data
        today = datetime.now().date()
        data = {
            'customer': self.customer.id,
            'start_date': (today - timedelta(days=30)).isoformat(),
            'end_date': today.isoformat(),
            'output_format': 'preview'
        }
        
        # Make the request
        url = reverse('billing:generate_report')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Verify the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] is True
        assert 'data' in response_data
        
        # Check report data structure
        report_data = response_data['data']
        assert report_data['customer_name'] == self.customer.company_name
        assert report_data['start_date'] == data['start_date']
        assert report_data['end_date'] == data['end_date']
        
        # Check preview data
        assert 'preview_data' in report_data
        preview_data = report_data['preview_data']
        assert 'orders' in preview_data
        assert 'service_totals' in preview_data
        assert 'total_amount' in preview_data
    
    def test_delete_billing_report(self):
        """Test DELETE request to delete a billing report."""
        # Make the request
        url = reverse('billing:report_detail', kwargs={'pk': self.report.id})
        response = self.client.delete(url)
        
        # Verify the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['success'] is True
        assert 'message' in response_data
        
        # Verify the report was deleted
        assert not BillingReport.objects.filter(id=self.report.id).exists()
    
    def test_generate_billing_report_formats(self):
        """Test POST request to generate reports in different formats."""
        # Prepare the request data
        today = datetime.now().date()
        data = {
            'customer': self.customer.id,
            'start_date': (today - timedelta(days=30)).isoformat(),
            'end_date': today.isoformat()
        }
        
        # Test different formats
        formats = ['preview', 'excel', 'pdf', 'csv']
        for output_format in formats:
            # Update the format
            data['output_format'] = output_format
            
            # Make the request
            url = reverse('billing:generate_report')
            response = self.client.post(
                url,
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Verify the response status code
            assert response.status_code == 200
            
            # For preview format, verify JSON structure
            if output_format == 'preview':
                response_data = json.loads(response.content)
                assert response_data['success'] is True
                assert 'data' in response_data
                assert 'preview_data' in response_data['data']
            # For other formats, verify content type
            elif output_format == 'excel':
                assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif output_format == 'pdf':
                assert response['Content-Type'] == 'application/pdf'
            elif output_format == 'csv':
                assert response['Content-Type'] == 'text/csv'
    
    def test_validation_errors(self):
        """Test validation error handling in generate report endpoint."""
        # Test case 1: Missing required field (customer)
        data1 = {
            'start_date': '2025-01-01',
            'end_date': '2025-02-01'
        }
        
        # Make the request
        url = reverse('billing:generate_report')
        response = self.client.post(
            url,
            data=json.dumps(data1),
            content_type='application/json'
        )
        
        # Verify the response
        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert response_data['success'] is False
        assert 'error' in response_data
        
        # Test case 2: Invalid date range (start after end)
        data2 = {
            'customer': self.customer.id,
            'start_date': '2025-02-01',
            'end_date': '2025-01-01'
        }
        
        # Make the request
        response = self.client.post(
            url,
            data=json.dumps(data2),
            content_type='application/json'
        )
        
        # Verify the response
        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert response_data['success'] is False
        assert 'error' in response_data
        
        # Test case 3: Invalid output format
        data3 = {
            'customer': self.customer.id,
            'start_date': '2025-01-01',
            'end_date': '2025-02-01',
            'output_format': 'invalid'
        }
        
        # Make the request
        response = self.client.post(
            url,
            data=json.dumps(data3),
            content_type='application/json'
        )
        
        # Verify the response
        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert response_data['success'] is False
        assert 'error' in response_data
    
    @pytest.mark.skip(reason="Full PACT verification requires a running service")
    def test_verify_billing_pacts(self):
        """Verify all PACT contracts for the billing API."""
        # This test requires a running API service
        if not os.path.exists(PACT_FILE):
            pytest.skip(f"PACT file not found: {PACT_FILE}")
        
        # Use the Pact verifier to validate all contracts
        verifier = Verifier(
            provider="billing-api",
            provider_base_url=PROVIDER_URL
        )
        
        # Define provider states and set up the required state
        provider_states = {
            "billing reports exist": self.setup_billing_reports,
            "a specific billing report exists": self.setup_specific_report,
            "can generate a billing report": self.setup_for_report_generation
        }
        
        # Verify the PACT
        output, _ = verifier.verify_pacts(
            PACT_FILE,
            provider_states=provider_states,
            provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states"
        )
        
        assert output == 0, "PACT verification failed"
    
    def setup_billing_reports(self):
        """Set up the 'billing reports exist' provider state."""
        # Create a test customer
        customer = Customer.objects.create(
            company_name="PACT Test Company",
            email="pact@example.com"
        )
        
        # Create reports
        today = datetime.now().date()
        reports = []
        for i in range(2):
            reports.append(BillingReport.objects.create(
                customer=customer,
                start_date=today - timedelta(days=30),
                end_date=today,
                total_amount=Decimal('100.00') + Decimal(str(i * 50)),
                report_data={'pact_test': f'data-{i}'},
                created_by=self.user,
                updated_by=self.user
            ))
        
        return {'customer': customer, 'reports': reports}
    
    def setup_specific_report(self):
        """Set up the 'a specific billing report exists' provider state."""
        # Create a test customer
        customer = Customer.objects.create(
            company_name="PACT Test Company",
            email="pact@example.com"
        )
        
        # Create a specific report
        today = datetime.now().date()
        report = BillingReport.objects.create(
            customer=customer,
            start_date=today - timedelta(days=30),
            end_date=today,
            total_amount=Decimal('1500.50'),
            report_data={
                'pact_test': 'specific_report',
                'customer_id': customer.id,
                'start_date': (today - timedelta(days=30)).isoformat(),
                'end_date': today.isoformat(),
                'total_amount': '1500.50'
            },
            created_by=self.user,
            updated_by=self.user
        )
        
        return {'customer': customer, 'report': report}
    
    def setup_for_report_generation(self):
        """Set up the 'can generate a billing report' provider state."""
        # Create a test customer
        customer = Customer.objects.create(
            company_name="PACT Report Generation",
            email="pact_report@example.com"
        )
        
        # Create a service
        service = Service.objects.create(
            service_name="PACT Test Service",
            description="Service for PACT testing",
            charge_type="single"
        )
        
        # Create a customer service
        cs = CustomerService.objects.create(
            customer=customer,
            service=service,
            unit_price=Decimal('25.00')
        )
        
        # Create an order
        today = datetime.now().date()
        order = Order.objects.create(
            customer=customer,
            transaction_id="PACT-ORDER",
            transaction_date=today - timedelta(days=1),
            close_date=today - timedelta(days=1),
            ship_to_name="PACT Test",
            ship_to_address="123 PACT St",
            total_item_qty=1
        )
        
        return {
            'customer': customer,
            'service': service,
            'customer_service': cs,
            'order': order
        }