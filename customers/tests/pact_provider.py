import json
import os
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient

from pactman import Consumer, Provider
from customers.models import Customer
from customers.tests.factories import CustomerFactory

User = get_user_model()


class CustomerProviderTest(TestCase):
    """
    Provider side of the Pact contract test for customer endpoints.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        cls.client.force_authenticate(user=cls.admin_user)
        
        # Set up pact verifier
        cls.pact_dir = os.path.join(settings.BASE_DIR, 'pacts')
        os.makedirs(cls.pact_dir, exist_ok=True)
    
    def setUp(self):
        self.pact = Provider('LedgerLinkAPI', host_name='localhost', port=8000)
        self.pact.setup()
    
    def tearDown(self):
        self.pact.tear_down()
    
    def test_get_customers_list(self):
        """Test GET /api/v1/customers/ contract"""
        # Create test data
        CustomerFactory.create_batch(5)
        
        # Set up the pact
        pact_file = os.path.join(self.pact_dir, 'ledgerlinkfrontend-ledgerlinkapi-pact.json')
        if os.path.exists(pact_file):
            self.pact.honours_pact(
                Consumer('LedgerLinkFrontend'),
                pact_file,
                states={
                    'customers exist': lambda: None  # Already created
                }
            )
    
    def test_get_customer_by_id(self):
        """Test GET /api/v1/customers/:id/ contract"""
        # Create test data
        customer = CustomerFactory()
        
        # Set up the pact
        pact_file = os.path.join(self.pact_dir, 'ledgerlinkfrontend-ledgerlinkapi-pact.json')
        if os.path.exists(pact_file):
            self.pact.honours_pact(
                Consumer('LedgerLinkFrontend'),
                pact_file,
                states={
                    f'customer with ID {customer.id} exists': lambda: None  # Already created
                }
            )
    
    def test_create_customer(self):
        """Test POST /api/v1/customers/ contract"""
        # Set up the pact
        pact_file = os.path.join(self.pact_dir, 'ledgerlinkfrontend-ledgerlinkapi-pact.json')
        if os.path.exists(pact_file):
            self.pact.honours_pact(
                Consumer('LedgerLinkFrontend'),
                pact_file,
                states={
                    'can create a customer': lambda: None  # No setup needed
                }
            )