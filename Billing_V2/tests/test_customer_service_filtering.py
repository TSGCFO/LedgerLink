import json
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from customers.models import Customer
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from rules.models import RuleGroup
from ..utils.calculator import BillingCalculator
from ..models import BillingReport, OrderCost, ServiceCost


class CustomerServiceFilteringTest(TestCase):
    """Tests for customer service filtering in BillingCalculator"""
    
    def setUp(self):
        """Set up test data for customer service filtering tests"""
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com"
        )
        
        # Create multiple services with different charge types
        self.service1 = Service.objects.create(
            service_name="Single Service",
            charge_type="single"
        )
        
        self.service2 = Service.objects.create(
            service_name="Quantity Service",
            charge_type="quantity"
        )
        
        self.service3 = Service.objects.create(
            service_name="Case-based Service",
            charge_type="case_based_tier"
        )
        
        # Create customer services for the customer
        self.cs1 = CustomerService.objects.create(
            customer=self.customer,
            service=self.service1,
            unit_price=Decimal('100.00')
        )
        
        self.cs2 = CustomerService.objects.create(
            customer=self.customer,
            service=self.service2,
            unit_price=Decimal('10.00')
        )
        
        self.cs3 = CustomerService.objects.create(
            customer=self.customer,
            service=self.service3,
            unit_price=Decimal('50.00')
        )
        
        # Create test orders in the date range
        self.start_date = timezone.now().replace(day=1)
        self.end_date = timezone.now().replace(day=28)
        
        self.order1 = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF12345",
            status="shipped",
            priority="medium",
            close_date=self.start_date + timezone.timedelta(days=1),
            total_item_qty=5
        )
        
        self.order2 = Order.objects.create(
            transaction_id=67890,
            customer=self.customer,
            reference_number="REF67890",
            status="shipped",
            priority="medium",
            close_date=self.start_date + timezone.timedelta(days=2),
            total_item_qty=10
        )
    
    def test_generate_report_with_all_services(self):
        """Test generating report with all customer services (no filtering)"""
        # Create calculator without customer_service_ids (should include all services)
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the report contains all services
        service_ids_in_report = set(int(service_id) for service_id in report.service_totals.keys())
        expected_service_ids = {self.service1.id, self.service2.id, self.service3.id}
        
        self.assertEqual(service_ids_in_report, expected_service_ids)
        self.assertEqual(report.total_amount, Decimal('350.00'))  # 100 + 10*5 + 10*10 + 50
    
    def test_generate_report_with_filtered_services(self):
        """Test generating report with filtered customer services"""
        # Create calculator with specific customer_service_ids
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=[self.cs1.id, self.cs3.id]  # Only include single and case-based services
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the report contains only the specified services
        service_ids_in_report = set(int(service_id) for service_id in report.service_totals.keys())
        expected_service_ids = {self.service1.id, self.service3.id}
        
        self.assertEqual(service_ids_in_report, expected_service_ids)
        self.assertEqual(report.total_amount, Decimal('150.00'))  # 100 + 50
    
    def test_generate_report_with_single_service(self):
        """Test generating report with only one customer service"""
        # Create calculator with only one customer_service_id
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=[self.cs2.id]  # Only include quantity service
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the report contains only the specified service
        service_ids_in_report = set(int(service_id) for service_id in report.service_totals.keys())
        expected_service_ids = {self.service2.id}
        
        self.assertEqual(service_ids_in_report, expected_service_ids)
        self.assertEqual(report.total_amount, Decimal('150.00'))  # 10*5 + 10*10
    
    def test_generate_report_with_empty_service_list(self):
        """Test generating report with empty customer service list"""
        # Create calculator with empty customer_service_ids
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=[]  # Empty list should not include any services
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the report contains no services
        self.assertEqual(len(report.service_totals), 0)
        self.assertEqual(report.total_amount, Decimal('0.00'))
    
    def test_generate_report_with_nonexistent_service_ids(self):
        """Test generating report with nonexistent service IDs"""
        # Create calculator with nonexistent customer_service_ids
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=[9999, 10000]  # IDs that don't exist
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the report contains no services
        self.assertEqual(len(report.service_totals), 0)
        self.assertEqual(report.total_amount, Decimal('0.00'))
    
    def test_generate_report_with_mix_of_valid_and_invalid_service_ids(self):
        """Test generating report with mix of valid and invalid service IDs"""
        # Create calculator with mix of valid and invalid customer_service_ids
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=[self.cs1.id, 9999]  # One valid, one invalid
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the report contains only the valid service
        service_ids_in_report = set(int(service_id) for service_id in report.service_totals.keys())
        expected_service_ids = {self.service1.id}
        
        self.assertEqual(service_ids_in_report, expected_service_ids)
        self.assertEqual(report.total_amount, Decimal('100.00'))
    
    def test_metadata_in_report(self):
        """Test that the selected customer services are stored in report metadata"""
        # Create calculator with specific customer_service_ids
        service_ids = [self.cs1.id, self.cs3.id]
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=service_ids
        )
        
        # Generate the report
        report = calculator.generate_report()
        
        # Verify the metadata contains the selected service IDs
        self.assertIn('selected_services', report.metadata)
        self.assertEqual(report.metadata['selected_services'], service_ids)