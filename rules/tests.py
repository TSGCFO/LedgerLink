from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Rule, RuleGroup
from .forms import RuleForm
from customer_services.models import CustomerService
from customers.models import Customer
from orders.models import Order, OrderSKUView

class RuleTests(TestCase):
    def setUp(self):
        # Create test customer and customer service
        self.customer = Customer.objects.create(
            company_name="Test Company"
        )
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service_name="Test Service"
        )
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )

    def test_sku_name_rule(self):
        # Test SKU name rule creation and validation
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_name',
            operator='eq',
            value='TEST-SKU'
        )
        self.assertEqual(rule.field, 'sku_name')
        self.assertEqual(rule.value, 'TEST-SKU')

        # Test invalid operator for SKU name
        with self.assertRaises(ValidationError):
            rule.operator = 'gt'
            rule.clean()

    def test_sku_count_rule(self):
        # Test SKU count rule creation and validation
        rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_count',
            operator='gt',
            value='5'
        )
        self.assertEqual(rule.field, 'sku_count')
        self.assertEqual(rule.value, '5')

        # Test string value for SKU count
        with self.assertRaises(ValidationError):
            rule.value = 'invalid'
            rule.clean()

    def test_rule_form_sku_name(self):
        # Test form validation for SKU name
        form_data = {
            'rule_group': self.rule_group.id,
            'field': 'sku_name',
            'operator': 'contains',
            'value': 'TEST'
        }
        form = RuleForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid operator for SKU name
        form_data['operator'] = 'gt'
        form = RuleForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_rule_form_sku_count(self):
        # Test form validation for SKU count
        form_data = {
            'rule_group': self.rule_group.id,
            'field': 'sku_count',
            'operator': 'gt',
            'value': '5'
        }
        form = RuleForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid value for SKU count
        form_data['value'] = 'invalid'
        form = RuleForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_rule_evaluation(self):
        # Create test order with SKU view data
        order = Order.objects.create(
            transaction_id=1,
            customer=self.customer,
            reference_number='TEST-ORDER'
        )
        order_sku = OrderSKUView.objects.create(
            transaction_id=1,
            customer=self.customer,
            reference_number='TEST-ORDER',
            sku_name='TEST-SKU',
            sku_count=10
        )

        # Test SKU name rule evaluation
        name_rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_name',
            operator='eq',
            value='TEST-SKU'
        )
        self.assertTrue(name_rule.evaluate(order_sku))

        # Test SKU count rule evaluation
        count_rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='sku_count',
            operator='gt',
            value='5'
        )
        self.assertTrue(count_rule.evaluate(order_sku))
