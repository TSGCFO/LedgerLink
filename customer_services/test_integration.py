from django.test import TestCase
from django.db import transaction
from decimal import Decimal

from customers.models import Customer
from services.models import Service
from .models import CustomerService
from rules.models import RuleGroup, Rule, AdvancedRule


class CustomerServiceIntegrationTest(TestCase):
    """
    Integration tests for CustomerService model with other modules.
    """
    @classmethod
    def setUpTestData(cls):
        # Create customers
        cls.customer = Customer.objects.create(
            company_name="Integration Test Company",
            legal_business_name="Integration Test Company LLC",
            email="integration@example.com",
            phone="555-9876",
            address="789 Integration St",
            city="Test City",
            state="TS",
            zip_code="98765",
            country="US"
        )
        
        # Create services
        cls.service = Service.objects.create(
            service_name="Integration Test Service",
            description="Service for integration testing",
            base_rate=Decimal('125.00'),
            charge_type="flat_rate"
        )
        
        # Create customer service
        cls.customer_service = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('120.00')
        )
    
    def test_rule_group_creation_with_customer_service(self):
        """Test creating a rule group for a customer service."""
        rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        self.assertEqual(rule_group.customer_service, self.customer_service)
        self.assertEqual(rule_group.logic_operator, 'AND')
    
    def test_basic_rule_creation_for_customer_service_rule_group(self):
        """Test creating a basic rule in a rule group for a customer service."""
        # Create rule group
        rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        # Create rule
        rule = Rule.objects.create(
            rule_group=rule_group,
            field='weight_lb',
            operator='gt',
            value='10',
            adjustment_amount='5.00'
        )
        
        self.assertEqual(rule.rule_group, rule_group)
        self.assertEqual(rule.field, 'weight_lb')
        self.assertEqual(rule.operator, 'gt')
        self.assertEqual(rule.value, '10')
        self.assertEqual(rule.adjustment_amount, '5.00')
    
    def test_advanced_rule_creation_for_customer_service_rule_group(self):
        """Test creating an advanced rule in a rule group for a customer service."""
        # Create rule group
        rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        # Create advanced rule
        advanced_rule = AdvancedRule.objects.create(
            rule_group=rule_group,
            conditions={
                'weight_lb': {'operator': 'gt', 'value': '20'},
                'quantity': {'operator': 'gt', 'value': '5'}
            },
            calculations=[
                {'type': 'flat_fee', 'value': 10.00},
                {'type': 'per_unit', 'value': 1.25, 'field': 'quantity'}
            ]
        )
        
        self.assertEqual(advanced_rule.rule_group, rule_group)
        self.assertEqual(advanced_rule.conditions['weight_lb']['operator'], 'gt')
        self.assertEqual(advanced_rule.conditions['weight_lb']['value'], '20')
        self.assertEqual(advanced_rule.calculations[0]['type'], 'flat_fee')
        self.assertEqual(advanced_rule.calculations[0]['value'], 10.00)
    
    def test_customer_service_deletion_cascades_to_rule_groups(self):
        """Test that deleting a customer service also deletes related rule groups."""
        # Create rule group
        rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        # Create rule
        rule = Rule.objects.create(
            rule_group=rule_group,
            field='weight_lb',
            operator='gt',
            value='10',
            adjustment_amount='5.00'
        )
        
        # Delete customer service
        rule_group_id = rule_group.id
        rule_id = rule.id
        self.customer_service.delete()
        
        # Verify rule group is deleted
        self.assertFalse(RuleGroup.objects.filter(id=rule_group_id).exists())
        
        # Verify rule is deleted
        self.assertFalse(Rule.objects.filter(id=rule_id).exists())
    
    def test_customer_service_unique_constraint(self):
        """Test that customer-service combination must be unique."""
        # Attempt to create duplicate customer service
        with transaction.atomic():
            with self.assertRaises(Exception):
                CustomerService.objects.create(
                    customer=self.customer,
                    service=self.service,
                    unit_price=Decimal('130.00')
                )


class CustomerServiceCascadeDeleteTest(TestCase):
    """
    Tests for cascade delete relationships with CustomerService model.
    """
    def setUp(self):
        # Create customers
        self.customer = Customer.objects.create(
            company_name="Cascade Test Company",
            legal_business_name="Cascade Test Company LLC",
            email="cascade@example.com",
            phone="555-4321",
            address="321 Cascade St",
            city="Test City",
            state="TS",
            zip_code="54321",
            country="US"
        )
        
        # Create services
        self.service = Service.objects.create(
            service_name="Cascade Test Service",
            description="Service for cascade testing",
            base_rate=Decimal('75.00'),
            charge_type="flat_rate"
        )
        
        # Create customer service
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('70.00')
        )
        
        # Create rule group
        self.rule_group = RuleGroup.objects.create(
            customer_service=self.customer_service,
            logic_operator='AND'
        )
        
        # Create rule
        self.rule = Rule.objects.create(
            rule_group=self.rule_group,
            field='weight_lb',
            operator='gt',
            value='15',
            adjustment_amount='7.50'
        )
    
    def test_customer_deletion_cascades_to_customer_service(self):
        """Test that deleting a customer also deletes related customer services."""
        customer_service_id = self.customer_service.id
        rule_group_id = self.rule_group.id
        rule_id = self.rule.id
        
        # Delete customer
        self.customer.delete()
        
        # Verify customer service is deleted
        self.assertFalse(CustomerService.objects.filter(id=customer_service_id).exists())
        
        # Verify rule group is deleted
        self.assertFalse(RuleGroup.objects.filter(id=rule_group_id).exists())
        
        # Verify rule is deleted
        self.assertFalse(Rule.objects.filter(id=rule_id).exists())
    
    def test_service_deletion_cascades_to_customer_service(self):
        """Test that deleting a service also deletes related customer services."""
        customer_service_id = self.customer_service.id
        rule_group_id = self.rule_group.id
        rule_id = self.rule.id
        
        # Delete service
        self.service.delete()
        
        # Verify customer service is deleted
        self.assertFalse(CustomerService.objects.filter(id=customer_service_id).exists())
        
        # Verify rule group is deleted
        self.assertFalse(RuleGroup.objects.filter(id=rule_group_id).exists())
        
        # Verify rule is deleted
        self.assertFalse(Rule.objects.filter(id=rule_id).exists())