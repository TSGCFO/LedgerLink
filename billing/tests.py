from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from billing.services.billing_calculator import BillingCalculator
from customers.models import Customer
from orders.models import Order
from customer_services.models import CustomerService
from services.models import Service
from rules.models import RuleGroup, Rule


class BillingCalculatorTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.customer = Customer.objects.create(company_name="Test Company")
        self.service = Service.objects.create(service_name="Test Service")
        self.customer_service = CustomerService.objects.create(
            customer=self.customer, service=self.service, unit_price=Decimal("10.00")
        )

        # Create a rule that applies to all orders
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service, logic_operator="AND"
        )
        self.rule = Rule.objects.create(
            rule_group=self.rule_group,
            field="total_item_qty",
            operator="gt",
            value="0",
            adjustment_amount=Decimal("5.00"),
        )

        # Create test orders
        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=30)

        self.order1 = Order.objects.create(
            customer=self.customer,
            transaction_id=1,
            close_date=self.start_date + timedelta(days=1),
            total_item_qty=5,
        )
        self.order2 = Order.objects.create(
            customer=self.customer,
            transaction_id=2,
            close_date=self.start_date + timedelta(days=2),
            total_item_qty=10,
        )

    def test_calculate_billing(self):
        calculator = BillingCalculator(self.customer, self.start_date, self.end_date)
        result = calculator.calculate_billing()

        # Check overall structure
        self.assertEqual(result["customer"], self.customer.company_name)
        self.assertEqual(result["start_date"], self.start_date)
        self.assertEqual(result["end_date"], self.end_date)

        # Check total bill
        expected_total = Decimal("160.00")  # (5 * 10 + 5) + (10 * 10 + 5)
        self.assertEqual(result["total_bill"], expected_total)

        # Check individual order details
        self.assertEqual(len(result["billing_details"]), 2)

        # Check first order
        order1_details = result["billing_details"][0]
        self.assertEqual(order1_details["order"]["transaction_id"], 1)
        self.assertEqual(order1_details["total"], Decimal("55.00"))

        # Check second order
        order2_details = result["billing_details"][1]
        self.assertEqual(order2_details["order"]["transaction_id"], 2)
        self.assertEqual(order2_details["total"], Decimal("105.00"))

    def test_generate_invoice_data(self):
        calculator = BillingCalculator(self.customer, self.start_date, self.end_date)
        invoice_data = calculator.generate_invoice_data()

        self.assertEqual(invoice_data["customer_name"], self.customer.company_name)
        self.assertEqual(invoice_data["total_amount"], Decimal("160.00"))
        self.assertEqual(len(invoice_data["line_items"]), 2)

        # Check line items
        self.assertEqual(invoice_data["line_items"][0]["quantity"], 5)
        self.assertEqual(invoice_data["line_items"][0]["total"], Decimal("55.00"))
        self.assertEqual(invoice_data["line_items"][1]["quantity"], 10)
        self.assertEqual(invoice_data["line_items"][1]["total"], Decimal("105.00"))
