import json
from decimal import Decimal
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from Billing_V2.models import BillingReport, OrderCost, ServiceCost
from customers.models import Customer
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from Billing_V2.utils.calculator import BillingCalculator
from rules.models import Rule, RuleGroup

"""
Integration tests for Billing_V2 that test the interaction between:
- BillingCalculator
- Rule evaluation
- API endpoints
- Database models
"""

@override_settings(
    SKIP_MATERIALIZED_VIEWS=True,  # Skip materialized views in tests
    # Use in-memory SQLite database for tests
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)
class BillingV2IntegrationTest(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.client = APIClient()
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Integration Test Company",
            contact_name="John Tester",
            email="john@test.com",
            phone="555-1234",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="US",
            is_active=True
        )
        
        # Create test services
        self.service_1 = Service.objects.create(
            name="Standard Shipping",
            description="Standard shipping service",
            cost_type="per_order",
            base_cost=Decimal("25.00")
        )
        
        self.service_2 = Service.objects.create(
            name="Special Handling",
            description="Special handling fee",
            cost_type="per_quantity",
            base_cost=Decimal("5.00")
        )
        
        # Create customer services
        self.customer_service_1 = CustomerService.objects.create(
            customer=self.customer,
            service=self.service_1,
            is_active=True
        )
        
        self.customer_service_2 = CustomerService.objects.create(
            customer=self.customer,
            service=self.service_2,
            is_active=True
        )
        
        # Create test orders
        self.order_1 = Order.objects.create(
            customer=self.customer,
            order_number="ORD-001",
            transaction_date=timezone.now().date() - timedelta(days=5),
            status="Completed",
            ship_to_name="John Smith",
            ship_to_address="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            ship_to_country="US",
            total_items=3,
            total_amount=Decimal("150.00")
        )
        
        self.order_2 = Order.objects.create(
            customer=self.customer,
            order_number="ORD-002",
            transaction_date=timezone.now().date() - timedelta(days=2),
            status="Completed",
            ship_to_name="Jane Smith",
            ship_to_address="456 Test Ave",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            ship_to_country="US",
            total_items=5,
            total_amount=Decimal("250.00")
        )
        
        # Create rule group
        self.rule_group = RuleGroup.objects.create(
            name="Standard Shipping Rules",
            description="Rules for standard shipping service",
            is_active=True
        )
        
        # Create rule for order value over $100
        self.rule = Rule.objects.create(
            name="Order Value > $100",
            description="Applies when order value exceeds $100",
            rule_group=self.rule_group,
            field="total_amount",
            operator="gt",
            value="100.00",
            is_active=True
        )
        
        # Associate rule group with customer service
        self.customer_service_1.rule_group = self.rule_group
        self.customer_service_1.save()
    
    def test_generate_billing_report_api(self):
        """Test the generate billing report API endpoint"""
        url = reverse('billing_v2:generate-report')
        
        data = {
            'customer_id': self.customer.id,
            'start_date': (timezone.now().date() - timedelta(days=10)).isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'output_format': 'json'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
        # Verify report was created in database
        report_id = response.data['data']['id']
        report = BillingReport.objects.get(id=report_id)
        
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.output_format, 'json')
        
        # Verify order costs were created
        self.assertEqual(report.order_costs.count(), 2)
        
        # Verify service costs were applied
        for order_cost in report.order_costs.all():
            self.assertEqual(order_cost.service_costs.count(), 1)  # Standard shipping should apply
            
            # Each order should have standard shipping cost
            service_cost = order_cost.service_costs.first()
            self.assertEqual(service_cost.service.name, "Standard Shipping")
            self.assertEqual(service_cost.amount, Decimal("25.00"))
    
    def test_calculator_rule_evaluation_integration(self):
        """Test the integration between calculator and rule evaluation"""
        # Initialize calculator
        calculator = BillingCalculator(
            customer=self.customer,
            start_date=(timezone.now().date() - timedelta(days=10)),
            end_date=timezone.now().date()
        )
        
        # Generate a report
        report = calculator.generate_report()
        
        # Check report contains correct number of orders
        self.assertEqual(len(report.order_costs), 2)
        
        # Check that rule evaluation worked correctly
        # Both orders should have standard shipping (order value > $100)
        for order_cost in report.order_costs:
            service_costs = [sc for sc in order_cost.service_costs 
                             if sc.service.name == "Standard Shipping"]
            self.assertEqual(len(service_costs), 1)
            self.assertEqual(service_costs[0].amount, Decimal("25.00"))
    
    def test_billing_report_to_json(self):
        """Test the JSON conversion of a billing report"""
        calculator = BillingCalculator(
            customer=self.customer,
            start_date=(timezone.now().date() - timedelta(days=10)),
            end_date=timezone.now().date()
        )
        
        # Generate and save a report
        report = calculator.generate_report()
        report.save()
        
        # Convert to JSON
        json_data = report.to_json()
        parsed_data = json.loads(json_data)
        
        # Validate JSON structure
        self.assertEqual(parsed_data['customer_id'], self.customer.id)
        self.assertEqual(parsed_data['customer_name'], self.customer.company_name)
        self.assertEqual(len(parsed_data['order_costs']), 2)
        
        # Validate order costs
        for order_cost in parsed_data['order_costs']:
            self.assertIn('order_id', order_cost)
            self.assertIn('order_number', order_cost)
            self.assertIn('transaction_date', order_cost)
            self.assertIn('service_costs', order_cost)
            
            # Each order should have standard shipping service cost
            shipping_services = [sc for sc in order_cost['service_costs'] 
                                if sc['service_name'] == "Standard Shipping"]
            self.assertEqual(len(shipping_services), 1)
            self.assertEqual(Decimal(str(shipping_services[0]['amount'])), Decimal("25.00"))
    
    def test_api_report_list_and_detail(self):
        """Test the report list and detail API endpoints"""
        # First create a report
        calculator = BillingCalculator(
            customer=self.customer,
            start_date=(timezone.now().date() - timedelta(days=10)),
            end_date=timezone.now().date()
        )
        
        report = calculator.generate_report()
        report.save()
        
        # Test list endpoint
        list_url = reverse('billing_v2:report-list')
        list_response = self.client.get(list_url)
        
        self.assertEqual(list_response.status_code, 200)
        self.assertTrue(list_response.data['success'])
        self.assertEqual(len(list_response.data['data']), 1)
        
        # Test detail endpoint
        detail_url = reverse('billing_v2:report-detail', args=[report.id])
        detail_response = self.client.get(detail_url)
        
        self.assertEqual(detail_response.status_code, 200)
        self.assertTrue(detail_response.data['success'])
        self.assertEqual(detail_response.data['data']['id'], str(report.id))
        self.assertEqual(detail_response.data['data']['customer_name'], self.customer.company_name)
    
    def test_customer_summary_endpoint(self):
        """Test the customer summary API endpoint"""
        # Create multiple reports for the customer
        start_date = timezone.now().date() - timedelta(days=30)
        
        for i in range(3):
            calculator = BillingCalculator(
                customer=self.customer,
                start_date=start_date + timedelta(days=i*10),
                end_date=start_date + timedelta(days=(i+1)*10 - 1)
            )
            
            report = calculator.generate_report()
            report.save()
        
        # Test customer summary endpoint
        url = reverse('billing_v2:customer-summary')
        response = self.client.get(f"{url}?customer_id={self.customer.id}")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
        summary = response.data['data'][0]
        self.assertEqual(summary['customer_id'], self.customer.id)
        self.assertEqual(summary['customer_name'], self.customer.company_name)
        self.assertEqual(summary['reports_count'], 3)
        self.assertGreater(Decimal(str(summary['total_billed'])), Decimal("0"))