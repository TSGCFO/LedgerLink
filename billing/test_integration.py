"""
Integration tests for the billing app.

These tests verify the integration between the billing app's components:
- Billing Calculator 
- Services
- API Views
- Database Models

They also test integration with other modules like:
- Customer Services
- Orders
- Rules
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import json
from datetime import datetime, timedelta
import io

from billing.models import BillingReport, BillingReportDetail
from billing.services import BillingReportService
from billing.billing_calculator import BillingCalculator, ServiceCost, OrderCost
from billing.utils import ReportCache
from customers.models import Customer
from services.models import Service
from customer_services.models import CustomerService
from orders.models import Order
from rules.models import RuleGroup, Rule, AdvancedRule


class BillingCalculatorIntegrationTest(TestCase):
    """Test integration of BillingCalculator with models and database."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create a customer
        cls.customer = Customer.objects.create(
            company_name="Integration Test Company",
            legal_business_name="Integration Test Company LLC",
            email="integration@example.com",
            phone="555-1234",
            address="123 Integration St",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="US"
        )

        # Create services
        cls.service1 = Service.objects.create(
            service_name="Standard Shipping",
            description="Regular shipping service",
            charge_type="single"
        )
        
        cls.service2 = Service.objects.create(
            service_name="Pick and Pack",
            description="Pick and pack service",
            charge_type="quantity"
        )
        
        # Create customer services
        cls.cs1 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service1,
            unit_price=Decimal('15.00')
        )
        
        cls.cs2 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service2,
            unit_price=Decimal('5.00')
        )
        
        # Create rule group for customer service 1
        cls.rule_group = RuleGroup.objects.create(
            customer_service=cls.cs1,
            logic_operator='AND'
        )
        
        # Create a rule
        cls.rule = Rule.objects.create(
            rule_group=cls.rule_group,
            field="total_item_qty",
            operator="gt",
            value="0"
        )
        
        # Create orders
        today = timezone.now().date()
        cls.order1 = Order.objects.create(
            customer=cls.customer,
            transaction_id="ORD-001",
            transaction_date=today,
            close_date=today,
            ship_to_name="John Doe",
            ship_to_company="Test Co",
            ship_to_address="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_country="US",
            total_item_qty=5,
            line_items=2,
            weight_lb=10.0,
            sku_quantity=json.dumps([
                {"sku": "SKU-001", "quantity": 3},
                {"sku": "SKU-002", "quantity": 2}
            ])
        )
        
        cls.order2 = Order.objects.create(
            customer=cls.customer,
            transaction_id="ORD-002",
            transaction_date=today - timedelta(days=1),
            close_date=today - timedelta(days=1),
            ship_to_name="Jane Smith",
            ship_to_company="Another Co",
            ship_to_address="456 Test Ave",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_country="US",
            total_item_qty=3,
            line_items=1,
            weight_lb=5.0,
            sku_quantity=json.dumps([
                {"sku": "SKU-001", "quantity": 3}
            ])
        )
        
        # Create an order outside the test date range
        cls.order3 = Order.objects.create(
            customer=cls.customer,
            transaction_id="ORD-003",
            transaction_date=today - timedelta(days=30),
            close_date=today - timedelta(days=30),
            ship_to_name="Bob Johnson",
            ship_to_company="Old Co",
            ship_to_address="789 Past St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_country="US",
            total_item_qty=2,
            line_items=1,
            weight_lb=3.0,
            sku_quantity=json.dumps([
                {"sku": "SKU-003", "quantity": 2}
            ])
        )
        
        # Create a user for testing API views
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_billing_calculator_integration(self):
        """Test that BillingCalculator correctly integrates with database models."""
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        calculator = BillingCalculator(self.customer.id, start_date, end_date)
        report = calculator.generate_report()
        
        # Verify report structure
        self.assertEqual(report.customer_id, self.customer.id)
        self.assertEqual(report.start_date, start_date)
        self.assertEqual(report.end_date, end_date)
        
        # Verify service costs
        self.assertEqual(len(report.order_costs), 2)  # Should include only order1 and order2
        
        # First order costs
        order1_cost = next((oc for oc in report.order_costs if oc.order_id == "ORD-001"), None)
        self.assertIsNotNone(order1_cost)
        self.assertEqual(len(order1_cost.service_costs), 2)  # Both services apply
        
        # Verify service costs for order1
        service1_cost = next((sc for sc in order1_cost.service_costs if sc.service_id == self.service1.id), None)
        self.assertIsNotNone(service1_cost)
        self.assertEqual(service1_cost.amount, Decimal('15.00'))  # Base price for single charge type
        
        service2_cost = next((sc for sc in order1_cost.service_costs if sc.service_id == self.service2.id), None)
        self.assertIsNotNone(service2_cost)
        self.assertEqual(service2_cost.amount, Decimal('25.00'))  # 5 items * $5.00 per item
        
        # Check order total
        self.assertEqual(order1_cost.total_amount, Decimal('40.00'))  # 15.00 + 25.00
        
        # Second order costs
        order2_cost = next((oc for oc in report.order_costs if oc.order_id == "ORD-002"), None)
        self.assertIsNotNone(order2_cost)
        self.assertEqual(len(order2_cost.service_costs), 2)  # Both services apply
        
        # Verify service costs for order2
        service1_cost = next((sc for sc in order2_cost.service_costs if sc.service_id == self.service1.id), None)
        self.assertIsNotNone(service1_cost)
        self.assertEqual(service1_cost.amount, Decimal('15.00'))  # Base price for single charge type
        
        service2_cost = next((sc for sc in order2_cost.service_costs if sc.service_id == self.service2.id), None)
        self.assertIsNotNone(service2_cost)
        self.assertEqual(service2_cost.amount, Decimal('15.00'))  # 3 items * $5.00 per item
        
        # Check order total
        self.assertEqual(order2_cost.total_amount, Decimal('30.00'))  # 15.00 + 15.00
        
        # Check overall total
        self.assertEqual(report.total_amount, Decimal('70.00'))  # 40.00 + 30.00
        
        # Check service totals
        self.assertEqual(report.service_totals[self.service1.id], Decimal('30.00'))  # 15.00 * 2 orders
        self.assertEqual(report.service_totals[self.service2.id], Decimal('40.00'))  # 25.00 + 15.00

    def test_billing_calculator_rule_integration(self):
        """Test integration of billing calculator with rules."""
        # Modify rule to only apply to orders with weight > 7.0
        self.rule.field = "weight_lb"
        self.rule.operator = "gt"
        self.rule.value = "7.0"
        self.rule.save()
        
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        calculator = BillingCalculator(self.customer.id, start_date, end_date)
        report = calculator.generate_report()
        
        # Order1 has weight 10.0 (> 7.0), so both services should apply
        order1_cost = next((oc for oc in report.order_costs if oc.order_id == "ORD-001"), None)
        self.assertIsNotNone(order1_cost)
        self.assertEqual(len(order1_cost.service_costs), 2)
        
        # Order2 has weight 5.0 (< 7.0), so only service2 should apply
        order2_cost = next((oc for oc in report.order_costs if oc.order_id == "ORD-002"), None)
        self.assertIsNotNone(order2_cost)
        self.assertEqual(len(order2_cost.service_costs), 1)
        self.assertEqual(order2_cost.service_costs[0].service_id, self.service2.id)
        
        # Check overall total (15.00 + 25.00 + 15.00 = 55.00)
        self.assertEqual(report.total_amount, Decimal('55.00'))

    def test_billing_calculator_advanced_rules(self):
        """Test integration with advanced rules, specifically case-based tiers."""
        # Create case-based tier service
        tier_service = Service.objects.create(
            service_name="Case Based Tier",
            description="Service with case-based pricing",
            charge_type="case_based_tier"
        )
        
        # Create customer service
        cs3 = CustomerService.objects.create(
            customer=self.customer,
            service=tier_service,
            unit_price=Decimal('10.00')
        )
        
        # Create advanced rule with tier config
        advanced_rule = AdvancedRule.objects.create(
            customer_service=cs3,
            name="Case Based Tier Rule",
            conditions={},
            calculations={},
            tier_config={
                "excluded_skus": [],
                "ranges": [
                    {"min": 1, "max": 5, "multiplier": 1.0},  # 1-5 cases: base price
                    {"min": 6, "max": 10, "multiplier": 0.9},  # 6-10 cases: 10% discount
                    {"min": 11, "max": 9999, "multiplier": 0.8}  # 11+ cases: 20% discount
                ]
            }
        )
        
        # Update order1 to have cases
        self.order1.sku_quantity = json.dumps([
            {"sku": "CASE-001", "quantity": 7}  # 7 cases (tier 2)
        ])
        self.order1.save()
        
        # Update order2 to have cases
        self.order2.sku_quantity = json.dumps([
            {"sku": "CASE-002", "quantity": 3}  # 3 cases (tier 1)
        ])
        self.order2.save()
        
        # Run calculator
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        calculator = BillingCalculator(self.customer.id, start_date, end_date)
        report = calculator.generate_report()
        
        # Order1 should have tier 2 pricing (7 cases, 10% discount)
        order1_cost = next((oc for oc in report.order_costs if oc.order_id == "ORD-001"), None)
        tier_service_cost = next((sc for sc in order1_cost.service_costs if sc.service_id == tier_service.id), None)
        self.assertIsNotNone(tier_service_cost)
        
        # $10.00 * 0.9 = $9.00
        self.assertEqual(tier_service_cost.amount, Decimal('9.00'))
        
        # Order2 should have tier 1 pricing (3 cases, no discount)
        order2_cost = next((oc for oc in report.order_costs if oc.order_id == "ORD-002"), None)
        tier_service_cost = next((sc for sc in order2_cost.service_costs if sc.service_id == tier_service.id), None)
        self.assertIsNotNone(tier_service_cost)
        
        # $10.00 * 1.0 = $10.00
        self.assertEqual(tier_service_cost.amount, Decimal('10.00'))


class BillingServiceIntegrationTest(TestCase):
    """Test integration of BillingReportService with database and BillingCalculator."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create a customer
        cls.customer = Customer.objects.create(
            company_name="Service Test Company",
            legal_business_name="Service Test Company LLC",
            email="service_test@example.com"
        )
        
        # Create a service
        cls.service = Service.objects.create(
            service_name="Test Service",
            description="Service for testing",
            charge_type="single"
        )
        
        # Create customer service
        cls.cs = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('25.00')
        )
        
        # Create an order
        today = timezone.now().date()
        cls.order = Order.objects.create(
            customer=cls.customer,
            transaction_id="SRV-001",
            transaction_date=today,
            close_date=today,
            ship_to_name="Service Test",
            ship_to_address="123 Service St",
            total_item_qty=1
        )
        
        # Create a user
        cls.user = User.objects.create_user(
            username='serviceuser',
            email='service@example.com',
            password='password'
        )

    def test_service_generate_report(self):
        """Test that BillingReportService correctly generates reports."""
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        # Create service with user
        service = BillingReportService(user=self.user)
        
        # Generate report
        result = service.generate_report(
            customer_id=self.customer.id,
            start_date=start_date,
            end_date=end_date,
            output_format='preview'
        )
        
        # Verify result
        self.assertIn('orders', result)
        self.assertEqual(len(result['orders']), 1)
        self.assertEqual(result['orders'][0]['order_id'], 'SRV-001')
        self.assertEqual(float(result['total_amount']), 25.0)
        
        # Check that report was saved to database
        self.assertEqual(BillingReport.objects.count(), 1)
        report = BillingReport.objects.first()
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.total_amount, Decimal('25.00'))
        self.assertEqual(report.created_by, self.user)

    def test_service_cache_integration(self):
        """Test integration with the report cache."""
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        # Clear cache
        ReportCache._cache = {}
        
        # Create service
        service = BillingReportService()
        
        # Generate report (should cache result)
        result1 = service.generate_report(
            customer_id=self.customer.id,
            start_date=start_date,
            end_date=end_date,
            output_format='preview'
        )
        
        # Verify result
        self.assertIn('orders', result1)
        
        # Get from cache (should be same object)
        cached_result = ReportCache.get_cached_report(
            self.customer.id, start_date, end_date, 'preview'
        )
        self.assertIsNotNone(cached_result)
        
        # Generate again (should use cache)
        result2 = service.generate_report(
            customer_id=self.customer.id,
            start_date=start_date,
            end_date=end_date,
            output_format='preview'
        )
        
        # Both results should be equal but not the same object
        self.assertEqual(result1, result2)


class BillingViewsIntegrationTest(TestCase):
    """Test integration of billing views with services and models."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create a customer
        cls.customer = Customer.objects.create(
            company_name="API Test Company",
            legal_business_name="API Test Company LLC",
            email="api_test@example.com"
        )
        
        # Create a service
        cls.service = Service.objects.create(
            service_name="API Test Service",
            description="Service for API testing",
            charge_type="single"
        )
        
        # Create customer service
        cls.cs = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('15.00')
        )
        
        # Create an order
        today = timezone.now().date()
        cls.order = Order.objects.create(
            customer=cls.customer,
            transaction_id="API-001",
            transaction_date=today,
            close_date=today,
            ship_to_name="API Test",
            ship_to_address="123 API St",
            total_item_qty=1
        )
        
        # Create a user
        cls.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='password'
        )
        
        # Create client
        cls.client = Client()
        
        # Create date range
        cls.start_date = (timezone.now().date() - timedelta(days=7)).isoformat()
        cls.end_date = timezone.now().date().isoformat()

    def test_generate_report_api_integration(self):
        """Test the GenerateReportAPIView integration."""
        # Login
        self.client.login(username='apiuser', password='password')
        
        # URL for generating report
        url = reverse('billing:generate_report')
        
        # Create request data
        data = {
            'customer': self.customer.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'output_format': 'preview'
        }
        
        # Make request
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = json.loads(response.content)
        
        # Verify structure
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        self.assertEqual(response_data['data']['customer_name'], 'API Test Company')
        self.assertEqual(response_data['data']['start_date'], self.start_date)
        self.assertEqual(response_data['data']['end_date'], self.end_date)
        
        # Verify preview data
        self.assertIn('preview_data', response_data['data'])
        preview_data = response_data['data']['preview_data']
        self.assertIn('orders', preview_data)
        self.assertEqual(len(preview_data['orders']), 1)
        
        # Check order data
        order_data = preview_data['orders'][0]
        self.assertEqual(order_data['order_id'], 'API-001')
        self.assertEqual(len(order_data['services']), 1)
        self.assertEqual(float(order_data['total_amount']), 15.0)
        
        # Verify service data
        service_data = order_data['services'][0]
        self.assertEqual(service_data['service_id'], self.service.id)
        self.assertEqual(service_data['service_name'], 'API Test Service')
        self.assertEqual(float(service_data['amount']), 15.0)

    def test_billing_report_list_api_integration(self):
        """Test the BillingReportListView integration."""
        # Create a billing report
        report = BillingReport.objects.create(
            customer=self.customer,
            start_date=timezone.now().date() - timedelta(days=7),
            end_date=timezone.now().date(),
            total_amount=Decimal('15.00'),
            report_data={'test': 'data'},
            created_by=self.user,
            updated_by=self.user
        )
        
        # Login
        self.client.login(username='apiuser', password='password')
        
        # URL for listing reports
        url = reverse('billing:report_list')
        
        # Make request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        response_data = json.loads(response.content)
        
        # Verify structure
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        self.assertEqual(len(response_data['data']), 1)
        
        # Verify report data
        report_data = response_data['data'][0]
        self.assertEqual(report_data['id'], str(report.id))
        self.assertEqual(report_data['customer'], self.customer.id)
        self.assertEqual(report_data['customer_name'], 'API Test Company')
        self.assertEqual(float(report_data['total_amount']), 15.0)

    def test_output_format_integration(self):
        """Test integration of different output formats."""
        # Login
        self.client.login(username='apiuser', password='password')
        
        # URL for generating report
        url = reverse('billing:generate_report')
        
        # Test formats (can't fully test binary outputs but can check response types)
        formats = ['preview', 'excel', 'pdf', 'csv']
        
        for output_format in formats:
            # Create request data
            data = {
                'customer': self.customer.id,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'output_format': output_format
            }
            
            # Make request
            response = self.client.post(
                url,
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            
            # Check content type
            if output_format == 'preview':
                self.assertEqual(response['Content-Type'], 'application/json')
            elif output_format == 'excel':
                self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            elif output_format == 'pdf':
                self.assertEqual(response['Content-Type'], 'application/pdf')
            elif output_format == 'csv':
                self.assertEqual(response['Content-Type'], 'text/csv')


class BillingEndToEndTest(TestCase):
    """End-to-end test of the entire billing process."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create a customer
        cls.customer = Customer.objects.create(
            company_name="E2E Test Company",
            legal_business_name="E2E Test Company LLC",
            email="e2e@example.com",
            phone="555-E2E-TEST",
            address="123 E2E St",
            city="E2E City",
            state="E2",
            zip_code="12345",
            country="US"
        )
        
        # Create services
        cls.service1 = Service.objects.create(
            service_name="Standard E2E Service",
            description="Regular service for E2E testing",
            charge_type="single"
        )
        
        cls.service2 = Service.objects.create(
            service_name="Quantity E2E Service",
            description="Quantity-based service for E2E testing",
            charge_type="quantity"
        )
        
        # Create customer services
        cls.cs1 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service1,
            unit_price=Decimal('20.00')
        )
        
        cls.cs2 = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service2,
            unit_price=Decimal('2.50')
        )
        
        # Create orders
        today = timezone.now().date()
        for i in range(5):  # Create 5 orders
            Order.objects.create(
                customer=cls.customer,
                transaction_id=f"E2E-00{i+1}",
                transaction_date=today - timedelta(days=i),
                close_date=today - timedelta(days=i),
                ship_to_name=f"E2E Test {i+1}",
                ship_to_address=f"{i+1}23 E2E St",
                ship_to_city="E2E City",
                ship_to_state="E2",
                ship_to_country="US",
                total_item_qty=5 + i,  # Different quantities
                line_items=1 + (i % 3),
                weight_lb=10.0 + i,
                sku_quantity=json.dumps([
                    {"sku": f"E2E-SKU-00{j+1}", "quantity": 2 + j} 
                    for j in range(i+1)
                ])
            )
        
        # Create a user
        cls.user = User.objects.create_user(
            username='e2euser',
            email='e2e@example.com',
            password='e2epassword'
        )
        
        # Create client
        cls.client = Client()
        cls.client.login(username='e2euser', password='e2epassword')

    def test_end_to_end_billing_process(self):
        """Test the entire billing process from calculation to report generation."""
        # Step 1: Generate a report using the service
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
        
        service = BillingReportService(user=self.user)
        preview_result = service.generate_report(
            customer_id=self.customer.id,
            start_date=start_date,
            end_date=end_date,
            output_format='preview'
        )
        
        # Verify preview data
        self.assertIn('orders', preview_result)
        self.assertEqual(len(preview_result['orders']), 5)  # All 5 orders
        
        # Check that report was saved to database
        self.assertEqual(BillingReport.objects.count(), 1)
        
        # Step 2: Generate a report using the API
        url = reverse('billing:generate_report')
        
        data = {
            'customer': self.customer.id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'output_format': 'preview'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Step 3: List reports using the API
        list_url = reverse('billing:report_list')
        response = self.client.get(f"{list_url}?customer={self.customer.id}")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        # Should have 2 reports now (one from service, one from API)
        self.assertEqual(len(response_data['data']), 2)
        
        # Calculate total - every order has service1 (20.00) and service2 (2.50 * qty)
        # Order 1: 20.00 + (2.50 * 5) = 20.00 + 12.50 = 32.50
        # Order 2: 20.00 + (2.50 * 6) = 20.00 + 15.00 = 35.00
        # Order 3: 20.00 + (2.50 * 7) = 20.00 + 17.50 = 37.50
        # Order 4: 20.00 + (2.50 * 8) = 20.00 + 20.00 = 40.00
        # Order 5: 20.00 + (2.50 * 9) = 20.00 + 22.50 = 42.50
        # Total: 32.50 + 35.00 + 37.50 + 40.00 + 42.50 = 187.50
        expected_total = Decimal('187.50')
        
        # Verify the total amount in the reports
        for report_data in response_data['data']:
            self.assertEqual(Decimal(report_data['total_amount']), expected_total)
            
        # Step 4: Generate CSV report and verify
        data['output_format'] = 'csv'
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="billing_report.csv"'))
        
        # Basic content check - can't fully parse CSV output here
        csv_content = response.content.decode('utf-8')
        self.assertTrue(csv_content.startswith("Order ID,Service ID,Service Name,Amount"))
        self.assertIn("E2E-001", csv_content)
        self.assertIn("Standard E2E Service", csv_content)
        self.assertIn("Quantity E2E Service", csv_content)