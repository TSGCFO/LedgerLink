from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from billing.models import BillingReport, BillingReportDetail
from billing.services import BillingReportService
from billing.billing_calculator import BillingCalculator, generate_billing_report

from .factories import (
    CustomerFactory, OrderFactory, ServiceFactory,
    CustomerServiceFactory, RuleFactory, RuleGroupFactory,
    BillingReportFactory, UserFactory
)

User = get_user_model()


class BillingReportIntegrationTests(TestCase):
    """Integration tests for the billing report generation process."""
    
    def setUp(self):
        # Create test user
        self.user = UserFactory()
        
        # Create customer
        self.customer = CustomerFactory()
        
        # Create services
        self.service1 = ServiceFactory(
            service_name="Pick Cost",
            service_code="PICK",
            charge_type="quantity"
        )
        self.service2 = ServiceFactory(
            service_name="Case Pick",
            service_code="CASE",
            charge_type="quantity"
        )
        self.service3 = ServiceFactory(
            service_name="Shipping Fee",
            service_code="SHIP",
            charge_type="single"
        )
        
        # Create customer services
        self.cs1 = CustomerServiceFactory(
            customer=self.customer,
            service=self.service1,
            unit_price=Decimal('2.50')
        )
        self.cs2 = CustomerServiceFactory(
            customer=self.customer,
            service=self.service2,
            unit_price=Decimal('5.00')
        )
        self.cs3 = CustomerServiceFactory(
            customer=self.customer,
            service=self.service3,
            unit_price=Decimal('15.00')
        )
        
        # Create rule group for shipping
        self.rule_group = RuleGroupFactory(
            customer_service=self.cs3,
            logic_operator="OR",
            rules_count=0  # No rules to start with
        )
        
        # Create shipping rule based on weight
        self.rule1 = RuleFactory(
            field="weight_lb",
            operator="gt",
            value="10",
            set_rule_group=self.rule_group
        )
        
        # Create date range for report
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
        
        # Create orders
        self.order1 = OrderFactory(
            customer=self.customer,
            transaction_id="ORD-001",
            order_date=self.start_date + timedelta(days=5),
            close_date=self.start_date + timedelta(days=7),
            weight_lb=15.0,  # Greater than 10, so shipping applies
            total_item_qty=10,
            sku_quantity=json.dumps([
                {"sku": "SKU-A", "quantity": 5},
                {"sku": "SKU-B", "quantity": 5}
            ])
        )
        
        self.order2 = OrderFactory(
            customer=self.customer,
            transaction_id="ORD-002",
            order_date=self.start_date + timedelta(days=15),
            close_date=self.start_date + timedelta(days=16),
            weight_lb=5.0,  # Less than 10, so shipping doesn't apply
            total_item_qty=20,
            sku_quantity=json.dumps([
                {"sku": "SKU-C", "quantity": 10},
                {"sku": "SKU-D", "quantity": 10}
            ])
        )
        
        # Create report service
        self.report_service = BillingReportService(self.user)
    
    def test_end_to_end_report_generation(self):
        """Test the complete flow of generating a billing report."""
        # Generate a preview report
        report_data = self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Verify report structure
        self.assertIn('orders', report_data)
        self.assertIn('service_totals', report_data)
        self.assertIn('total_amount', report_data)
        self.assertIn('metadata', report_data)
        
        # Verify orders data
        self.assertEqual(len(report_data['orders']), 2)
        order_ids = [order['order_id'] for order in report_data['orders']]
        self.assertIn('ORD-001', order_ids)
        self.assertIn('ORD-002', order_ids)
        
        # Verify services for each order
        for order in report_data['orders']:
            if order['order_id'] == 'ORD-001':
                # Order 1 should have Pick Cost and Shipping (weight > 10)
                service_names = [s['service_name'] for s in order['services']]
                self.assertIn('Pick Cost', service_names)
                self.assertIn('Shipping Fee', service_names)
                
                # Calculate expected amounts
                pick_cost = Decimal('2.50') * Decimal('10')  # unit price * total items
                shipping = Decimal('15.00')  # flat fee
                expected_total = pick_cost + shipping
                
                self.assertEqual(Decimal(order['total_amount']), expected_total)
                
            elif order['order_id'] == 'ORD-002':
                # Order 2 should have only Pick Cost (weight < 10)
                service_names = [s['service_name'] for s in order['services']]
                self.assertIn('Pick Cost', service_names)
                self.assertNotIn('Shipping Fee', service_names)
                
                # Calculate expected amount
                pick_cost = Decimal('2.50') * Decimal('20')  # unit price * total items
                expected_total = pick_cost
                
                self.assertEqual(Decimal(order['total_amount']), expected_total)
        
        # Verify service totals
        self.assertIn(str(self.service1.id), report_data['service_totals'])  # Pick Cost
        self.assertIn(str(self.service3.id), report_data['service_totals'])  # Shipping
        
        # Calculate expected service totals
        pick_cost_total = Decimal('2.50') * (Decimal('10') + Decimal('20'))
        shipping_total = Decimal('15.00')
        
        # Check service total values
        self.assertEqual(
            report_data['service_totals'][str(self.service1.id)]['amount'],
            float(pick_cost_total)
        )
        self.assertEqual(
            report_data['service_totals'][str(self.service3.id)]['amount'],
            float(shipping_total)
        )
        
        # Verify total amount
        expected_grand_total = pick_cost_total + shipping_total
        self.assertEqual(Decimal(report_data['total_amount']), expected_grand_total)
    
    def test_service_rule_integration(self):
        """Test that service rules are correctly applied during billing calculation."""
        # Modify rule to exclude order1 (change weight threshold to > 20)
        self.rule1.value = '20'
        self.rule1.save()
        
        # Generate a preview report
        report_data = self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Check services for each order
        for order in report_data['orders']:
            # Neither order should have shipping now
            service_names = [s['service_name'] for s in order['services']]
            self.assertNotIn('Shipping Fee', service_names)
        
        # Verify shipping isn't in service totals
        self.assertNotIn(str(self.service3.id), report_data['service_totals'])
    
    def test_multiple_report_formats(self):
        """Test generating reports in different formats."""
        # Test preview format first
        preview_data = self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        self.assertIsInstance(preview_data, dict)
        
        # Test CSV format
        csv_data = self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='csv'
        )
        self.assertIsInstance(csv_data, str)
        self.assertIn('Order ID,Service ID,Service Name,Amount', csv_data)
        
        # Test Excel format
        excel_data = self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='excel'
        )
        self.assertIsInstance(excel_data, bytes)
        
        # Test PDF format
        pdf_data = self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='pdf'
        )
        self.assertIsInstance(pdf_data, bytes)
        self.assertTrue(pdf_data.startswith(b'%PDF'))
    
    def test_report_persistence(self):
        """Test that reports are persisted to the database."""
        # Generate a report
        self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Check the report was saved to the database
        reports = BillingReport.objects.filter(
            customer=self.customer,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self.assertEqual(reports.count(), 1)
        saved_report = reports.first()
        
        # Verify report data
        self.assertEqual(saved_report.customer, self.customer)
        self.assertEqual(saved_report.start_date, self.start_date)
        self.assertEqual(saved_report.end_date, self.end_date)
        self.assertIn('orders', saved_report.report_data)
        self.assertIn('total_amount', saved_report.report_data)
        
        # Verify audit fields
        self.assertEqual(saved_report.created_by, self.user)
        self.assertEqual(saved_report.updated_by, self.user)


class BillingCalculatorIntegrationTests(TestCase):
    """Integration tests for the BillingCalculator functionality."""
    
    def setUp(self):
        # Create customer
        self.customer = CustomerFactory()
        
        # Create services with different charge types
        self.single_service = ServiceFactory(
            service_name="Flat Fee",
            charge_type="single"
        )
        self.quantity_service = ServiceFactory(
            service_name="Per Item",
            charge_type="quantity"
        )
        self.case_service = ServiceFactory(
            service_name="Case Based",
            charge_type="case_based_tier"
        )
        
        # Create customer services
        self.cs_single = CustomerServiceFactory(
            customer=self.customer,
            service=self.single_service,
            unit_price=Decimal('10.00')
        )
        self.cs_quantity = CustomerServiceFactory(
            customer=self.customer,
            service=self.quantity_service,
            unit_price=Decimal('2.50')
        )
        self.cs_case = CustomerServiceFactory(
            customer=self.customer,
            service=self.case_service,
            unit_price=Decimal('5.00')
        )
        
        # Create date range
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
        
        # Create order
        self.order = OrderFactory(
            customer=self.customer,
            order_date=self.start_date + timedelta(days=1),
            close_date=self.start_date + timedelta(days=2),
            total_item_qty=10,
            sku_quantity=json.dumps([
                {"sku": "SKU-A", "quantity": 5},
                {"sku": "SKU-B", "quantity": 5}
            ])
        )
    
    def test_direct_calculator_usage(self):
        """Test using the BillingCalculator class directly."""
        # Create calculator
        calculator = BillingCalculator(
            self.customer.id,
            self.start_date,
            self.end_date
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Verify report structure
        self.assertEqual(report.customer_id, self.customer.id)
        self.assertEqual(report.start_date, self.start_date)
        self.assertEqual(report.end_date, self.end_date)
        
        # Verify order costs
        self.assertEqual(len(report.order_costs), 1)
        
        # Verify service costs
        order_cost = report.order_costs[0]
        service_ids = [sc.service_id for sc in order_cost.service_costs]
        self.assertIn(self.single_service.id, service_ids)
        self.assertIn(self.quantity_service.id, service_ids)
        
        # Calculate expected amounts
        single_amount = Decimal('10.00')  # flat fee
        quantity_amount = Decimal('2.50') * Decimal('10')  # unit price * items
        expected_total = single_amount + quantity_amount
        
        # Verify total amount
        self.assertEqual(report.total_amount, expected_total)
    
    def test_generate_billing_report_function(self):
        """Test using the generate_billing_report function."""
        # Call the function
        report_data = generate_billing_report(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Verify report data structure
        self.assertIn('customer_id', report_data)
        self.assertIn('start_date', report_data)
        self.assertIn('end_date', report_data)
        self.assertIn('orders', report_data)
        self.assertIn('total_amount', report_data)
        
        # Verify orders data
        self.assertEqual(len(report_data['orders']), 1)
        
        # Verify services
        order_data = report_data['orders'][0]
        service_ids = [s['service_id'] for s in order_data['services']]
        self.assertIn(self.single_service.id, service_ids)
        self.assertIn(self.quantity_service.id, service_ids)
        
        # Calculate expected amounts
        single_amount = Decimal('10.00')  # flat fee
        quantity_amount = Decimal('2.50') * Decimal('10')  # unit price * items
        expected_total = single_amount + quantity_amount
        
        # Verify total amount
        self.assertEqual(Decimal(report_data['total_amount']), expected_total)


class RuleEvaluationIntegrationTests(TestCase):
    """Integration tests for rule evaluation logic."""
    
    def setUp(self):
        # Create customer
        self.customer = CustomerFactory()
        
        # Create service
        self.service = ServiceFactory(
            service_name="Conditional Service",
            charge_type="single"
        )
        
        # Create customer service
        self.cs = CustomerServiceFactory(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('25.00')
        )
        
        # Create rule group with AND logic
        self.rule_group = RuleGroupFactory(
            customer_service=self.cs,
            logic_operator="AND",
            rules_count=0
        )
        
        # Create two rules that must both match
        self.rule1 = RuleFactory(
            field="weight_lb",
            operator="gt",
            value="10",
            set_rule_group=self.rule_group
        )
        
        self.rule2 = RuleFactory(
            field="ship_to_country",
            operator="eq",
            value="US",
            set_rule_group=self.rule_group
        )
        
        # Create date range
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
    
    def test_rule_logic_operators(self):
        """Test different rule logic operators."""
        # Create orders that match different combinations of rules
        
        # Order 1: Matches both rules (weight > 10, country = US)
        order1 = OrderFactory(
            customer=self.customer,
            order_date=self.start_date + timedelta(days=1),
            close_date=self.start_date + timedelta(days=2),
            weight_lb=15.0,
            ship_to_country="US"
        )
        
        # Order 2: Matches rule1 but not rule2 (weight > 10, country != US)
        order2 = OrderFactory(
            customer=self.customer,
            order_date=self.start_date + timedelta(days=3),
            close_date=self.start_date + timedelta(days=4),
            weight_lb=15.0,
            ship_to_country="CA"
        )
        
        # Order 3: Matches rule2 but not rule1 (weight <= 10, country = US)
        order3 = OrderFactory(
            customer=self.customer,
            order_date=self.start_date + timedelta(days=5),
            close_date=self.start_date + timedelta(days=6),
            weight_lb=5.0,
            ship_to_country="US"
        )
        
        # Logic operator: AND (both rules must match)
        self.rule_group.logic_operator = "AND"
        self.rule_group.save()
        
        # Generate report
        report_data = generate_billing_report(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Only order1 should have the service
        order_with_service = []
        for order in report_data['orders']:
            service_ids = [s['service_id'] for s in order['services']]
            if self.service.id in service_ids:
                order_with_service.append(order['order_id'])
        
        self.assertEqual(len(order_with_service), 1)
        self.assertEqual(order_with_service[0], order1.transaction_id)
        
        # Logic operator: OR (either rule must match)
        self.rule_group.logic_operator = "OR"
        self.rule_group.save()
        
        # Generate report
        report_data = generate_billing_report(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # All orders should have the service
        order_with_service = []
        for order in report_data['orders']:
            service_ids = [s['service_id'] for s in order['services']]
            if self.service.id in service_ids:
                order_with_service.append(order['order_id'])
        
        self.assertEqual(len(order_with_service), 3)
        self.assertIn(order1.transaction_id, order_with_service)
        self.assertIn(order2.transaction_id, order_with_service)
        self.assertIn(order3.transaction_id, order_with_service)