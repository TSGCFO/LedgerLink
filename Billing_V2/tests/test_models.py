import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from customers.models import Customer
from orders.models import Order
from ..models import BillingReport, OrderCost, ServiceCost


class BillingReportModelTest(TestCase):
    """Tests for the BillingReport model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create a test billing report
        self.report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now(),
            service_totals={
                "1": {"service_name": "Test Service", "amount": 100.00}
            },
            total_amount=100.00
        )
        
    def test_billing_report_creation(self):
        """Test creating a BillingReport"""
        self.assertEqual(self.report.customer, self.customer)
        self.assertEqual(float(self.report.total_amount), 100.00)
        self.assertEqual(
            self.report.service_totals, 
            {"1": {"service_name": "Test Service", "amount": 100.00}}
        )
        
    def test_billing_report_string_representation(self):
        """Test the string representation of BillingReport"""
        expected_string = f"Billing Report #{self.report.id} - Test Company"
        self.assertEqual(str(self.report), expected_string)
        
    def test_to_dict_method(self):
        """Test the to_dict method of BillingReport"""
        report_dict = self.report.to_dict()
        
        self.assertEqual(report_dict['customer_id'], self.customer.id)
        self.assertEqual(report_dict['customer_name'], "Test Company")
        self.assertEqual(report_dict['total_amount'], 100.0)
        self.assertEqual(
            report_dict['service_totals'], 
            {"1": {"service_name": "Test Service", "amount": 100.00}}
        )
        
    def test_to_json_method(self):
        """Test the to_json method of BillingReport"""
        report_json = self.report.to_json()
        report_dict = json.loads(report_json)
        
        self.assertEqual(report_dict['customer_id'], self.customer.id)
        self.assertEqual(report_dict['customer_name'], "Test Company")
        self.assertEqual(report_dict['total_amount'], 100.0)


class OrderCostModelTest(TestCase):
    """Tests for the OrderCost model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create a test order
        self.order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF12345",
            status="shipped",
            priority="medium"
        )
        
        # Create a test billing report
        self.report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now()
        )
        
        # Create a test order cost
        self.order_cost = OrderCost.objects.create(
            order=self.order,
            billing_report=self.report,
            total_amount=50.00
        )
        
    def test_order_cost_creation(self):
        """Test creating an OrderCost"""
        self.assertEqual(self.order_cost.order, self.order)
        self.assertEqual(self.order_cost.billing_report, self.report)
        self.assertEqual(float(self.order_cost.total_amount), 50.00)
        
    def test_order_cost_string_representation(self):
        """Test the string representation of OrderCost"""
        expected_string = f"Order Cost #{self.order_cost.id} - Order #{self.order.transaction_id}"
        self.assertEqual(str(self.order_cost), expected_string)
        
    def test_to_dict_method(self):
        """Test the to_dict method of OrderCost"""
        order_cost_dict = self.order_cost.to_dict()
        
        self.assertEqual(order_cost_dict['order_id'], self.order.transaction_id)
        self.assertEqual(order_cost_dict['reference_number'], "REF12345")
        self.assertEqual(order_cost_dict['total_amount'], 50.0)
        self.assertEqual(len(order_cost_dict['service_costs']), 0)
        
    def test_add_service_cost(self):
        """Test adding a service cost to an order cost"""
        # Create a service cost
        service_cost = ServiceCost.objects.create(
            order_cost=self.order_cost,
            service_id=1,
            service_name="Test Service",
            amount=25.00
        )
        
        # Initial total amount
        initial_total = self.order_cost.total_amount
        
        # Add the service cost
        self.order_cost.add_service_cost(service_cost)
        
        # Verify total amount is updated
        self.assertEqual(float(self.order_cost.total_amount), float(initial_total) + 25.00)
        
        # Get updated object from database
        updated_order_cost = OrderCost.objects.get(id=self.order_cost.id)
        
        # Verify that service cost is associated with order cost
        self.assertEqual(updated_order_cost.service_costs.count(), 1)
        self.assertEqual(updated_order_cost.service_costs.first(), service_cost)


class ServiceCostModelTest(TestCase):
    """Tests for the ServiceCost model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create a test order
        self.order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF12345",
            status="shipped",
            priority="medium"
        )
        
        # Create a test billing report
        self.report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now()
        )
        
        # Create a test order cost
        self.order_cost = OrderCost.objects.create(
            order=self.order,
            billing_report=self.report
        )
        
        # Create a test service cost
        self.service_cost = ServiceCost.objects.create(
            order_cost=self.order_cost,
            service_id=1,
            service_name="Test Service",
            amount=25.00
        )
        
    def test_service_cost_creation(self):
        """Test creating a ServiceCost"""
        self.assertEqual(self.service_cost.order_cost, self.order_cost)
        self.assertEqual(self.service_cost.service_id, 1)
        self.assertEqual(self.service_cost.service_name, "Test Service")
        self.assertEqual(float(self.service_cost.amount), 25.00)
        
    def test_service_cost_string_representation(self):
        """Test the string representation of ServiceCost"""
        expected_string = "Test Service - $25.00"
        self.assertEqual(str(self.service_cost), expected_string)
        
    def test_to_dict_method(self):
        """Test the to_dict method of ServiceCost"""
        service_cost_dict = self.service_cost.to_dict()
        
        self.assertEqual(service_cost_dict['service_id'], 1)
        self.assertEqual(service_cost_dict['service_name'], "Test Service")
        self.assertEqual(service_cost_dict['amount'], 25.0)