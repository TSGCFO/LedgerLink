from django.test import TestCase
from django.db import transaction
from decimal import Decimal

from .models import Service
from customers.models import Customer
from customer_services.models import CustomerService
from rules.models import RuleGroup


class ServiceIntegrationTest(TestCase):
    """
    Integration tests for Service model with other modules.
    """
    @classmethod
    def setUpTestData(cls):
        # Create a service
        cls.service = Service.objects.create(
            service_name="Integration Test Service",
            description="Service for integration testing",
            charge_type="quantity"
        )
        
        # Create a customer
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
    
    def test_create_customer_service_with_service(self):
        """Test creating a customer service with a service."""
        customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('150.00')
        )
        
        self.assertEqual(customer_service.customer, self.customer)
        self.assertEqual(customer_service.service, self.service)
        self.assertEqual(customer_service.unit_price, Decimal('150.00'))
    
    def test_list_customer_services_for_service(self):
        """Test listing all customer services for a specific service."""
        # Create a second customer
        customer2 = Customer.objects.create(
            company_name="Second Test Company",
            legal_business_name="Second Test Company LLC",
            email="second@example.com",
            phone="555-5678",
            address="567 Second St",
            city="Test City",
            state="TS",
            zip_code="56789",
            country="US"
        )
        
        # Create customer services for both customers
        cs1 = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('150.00')
        )
        
        cs2 = CustomerService.objects.create(
            customer=customer2,
            service=self.service,
            unit_price=Decimal('160.00')
        )
        
        # Get all customer services for the service
        customer_services = self.service.customerservice_set.all()
        
        self.assertEqual(customer_services.count(), 2)
        self.assertIn(cs1, customer_services)
        self.assertIn(cs2, customer_services)
    
    def test_rule_group_creation_for_service(self):
        """Test creating a rule group for a customer service using this service."""
        # Create a customer service
        customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('150.00')
        )
        
        # Create a rule group for the customer service
        rule_group = RuleGroup.objects.create(
            customer_service=customer_service,
            logic_operator='AND'
        )
        
        self.assertEqual(rule_group.customer_service, customer_service)
        self.assertEqual(rule_group.customer_service.service, self.service)
    
    def test_service_deletion_with_relationships(self):
        """
        Test that service deletion is prevented when it has customer service relationships.
        """
        # Create a customer service
        CustomerService.objects.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('150.00')
        )
        
        # Attempt to delete the service - should raise an error
        # Using transaction.atomic to avoid affecting other tests
        with transaction.atomic():
            with self.assertRaises(Exception):
                self.service.delete()
        
        # Verify service still exists
        self.assertTrue(Service.objects.filter(id=self.service.id).exists())
    
    def test_service_deletion_without_relationships(self):
        """
        Test that service deletion succeeds when it has no customer service relationships.
        """
        # Create a new service with no relationships
        service = Service.objects.create(
            service_name="Temporary Service",
            description="Service with no relationships",
            charge_type="single"
        )
        
        # Delete the service - should succeed
        service.delete()
        
        # Verify service no longer exists
        self.assertFalse(Service.objects.filter(service_name="Temporary Service").exists())