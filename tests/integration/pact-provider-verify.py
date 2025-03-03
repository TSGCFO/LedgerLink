import os
import json
import django
import sys
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from customers.models import Customer
from orders.models import Order
from products.models import Product
from rules.models import RuleGroup, Rule, AdvancedRule
from billing.models import BillingReport

# Pact verifier
from pact import Verifier


class PactProviderTest:
    """Provider verification tests for Pact contracts"""
    
    @staticmethod
    def setup_provider_state(state_name, state_params=None):
        """Set up test data based on the provider state requested by Pact"""
        print(f"Setting up provider state: {state_name}")
        
        # Create test user
        user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True
            }
        )
        user.set_password('password123')
        user.save()
        
        # Create test customers
        customer1, _ = Customer.objects.get_or_create(
            id=1,
            defaults={
                'company_name': 'Test Company 1',
                'contact_name': 'Test Contact 1',
                'email': 'contact1@test.com',
                'phone': '555-1234',
                'is_active': True
            }
        )
        
        customer2, _ = Customer.objects.get_or_create(
            id=2,
            defaults={
                'company_name': 'Test Company 2',
                'contact_name': 'Test Contact 2',
                'email': 'contact2@test.com',
                'phone': '555-5678',
                'is_active': True
            }
        )
        
        # Create test products
        product1, _ = Product.objects.get_or_create(
            sku='SKU001',
            defaults={
                'name': 'Test Product 1',
                'description': 'Test description 1',
                'price': 10.00
            }
        )
        
        product2, _ = Product.objects.get_or_create(
            sku='SKU002',
            defaults={
                'name': 'Test Product 2',
                'description': 'Test description 2',
                'price': 10.00
            }
        )
        
        product3, _ = Product.objects.get_or_create(
            sku='SKU003',
            defaults={
                'name': 'Test Product 3',
                'description': 'Test description 3',
                'price': 20.00
            }
        )
        
        product4, _ = Product.objects.get_or_create(
            sku='SKU004',
            defaults={
                'name': 'Test Product 4',
                'description': 'Test description 4',
                'price': 20.00
            }
        )
        
        # Handle different provider states
        if state_name == 'orders exist':
            # Create test orders
            order1, _ = Order.objects.get_or_create(
                id=1,
                defaults={
                    'customer': customer1,
                    'status': 'pending',
                    'order_date': timezone.now(),
                    'priority': 'normal',
                    'sku_quantities': json.dumps({'SKU001': 5, 'SKU002': 10})
                }
            )
            
            order2, _ = Order.objects.get_or_create(
                id=2,
                defaults={
                    'customer': customer2,
                    'status': 'completed',
                    'order_date': timezone.now() - timedelta(days=1),
                    'priority': 'normal',
                    'sku_quantities': json.dumps({'SKU003': 3, 'SKU004': 7})
                }
            )
            
        elif state_name == 'an order with ID 1 exists':
            # Create specific order
            order1, _ = Order.objects.get_or_create(
                id=1,
                defaults={
                    'customer': customer1,
                    'status': 'pending',
                    'order_date': timezone.now(),
                    'priority': 'normal',
                    'sku_quantities': json.dumps({'SKU001': 5, 'SKU002': 10})
                }
            )
            
        elif state_name == 'order can be created':
            # No setup needed, just ensure the customer exists
            pass
            
        elif state_name == 'rules exist':
            # Create rule group
            rule_group, _ = RuleGroup.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'Test Rule Group',
                    'description': 'Test rule group'
                }
            )
            
            # Create rules
            rule1, _ = AdvancedRule.objects.get_or_create(
                id=1,
                defaults={
                    'rule_group': rule_group,
                    'name': 'Volume Discount',
                    'description': 'Applies discount for large orders',
                    'conditions': json.dumps({'field': 'quantity', 'operator': 'gt', 'value': 10}),
                    'calculations': json.dumps({'type': 'percent_discount', 'value': 5.0})
                }
            )
            
            rule2, _ = AdvancedRule.objects.get_or_create(
                id=2,
                defaults={
                    'rule_group': rule_group,
                    'name': 'Tiered Pricing',
                    'description': 'Applies tiered pricing based on quantity',
                    'conditions': json.dumps({'field': 'sku_id', 'operator': 'in', 'value': ['SKU001', 'SKU002']}),
                    'calculations': json.dumps({'type': 'case_based_tier', 'field': 'quantity'}),
                    'tier_config': json.dumps({
                        'tiers': [
                            {'min': 0, 'max': 10, 'value': 1.00},
                            {'min': 11, 'max': 50, 'value': 0.75},
                            {'min': 51, 'max': 1000, 'value': 0.50}
                        ]
                    })
                }
            )
            
        elif state_name == 'a rule with ID 1 exists':
            # Create rule group
            rule_group, _ = RuleGroup.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'Test Rule Group',
                    'description': 'Test rule group'
                }
            )
            
            # Create specific rule
            rule1, _ = AdvancedRule.objects.get_or_create(
                id=1,
                defaults={
                    'rule_group': rule_group,
                    'name': 'Volume Discount',
                    'description': 'Applies discount for large orders',
                    'conditions': json.dumps({'field': 'quantity', 'operator': 'gt', 'value': 10}),
                    'calculations': json.dumps({'type': 'percent_discount', 'value': 5.0})
                }
            )
            
        elif state_name == 'billing reports exist':
            # Create billing reports
            report1, _ = BillingReport.objects.get_or_create(
                id=1,
                defaults={
                    'customer': customer1,
                    'billing_date': timezone.now(),
                    'total_amount': 150.00,
                    'created_by': user,
                    'details': json.dumps([
                        {
                            'sku': 'SKU001',
                            'quantity': 5,
                            'base_price': 10.00,
                            'total': 50.00
                        },
                        {
                            'sku': 'SKU002',
                            'quantity': 10,
                            'base_price': 10.00,
                            'total': 100.00
                        }
                    ])
                }
            )
            
            report2, _ = BillingReport.objects.get_or_create(
                id=2,
                defaults={
                    'customer': customer2,
                    'billing_date': timezone.now() - timedelta(days=1),
                    'total_amount': 220.00,
                    'created_by': user,
                    'details': json.dumps([
                        {
                            'sku': 'SKU003',
                            'quantity': 3,
                            'base_price': 20.00,
                            'total': 60.00
                        },
                        {
                            'sku': 'SKU004',
                            'quantity': 8,
                            'base_price': 20.00,
                            'total': 160.00
                        }
                    ])
                }
            )
            
        elif state_name == 'billing can be calculated':
            # Create test orders if they don't exist
            order1, _ = Order.objects.get_or_create(
                id=1,
                defaults={
                    'customer': customer1,
                    'status': 'pending',
                    'order_date': timezone.now(),
                    'priority': 'normal',
                    'sku_quantities': json.dumps({'SKU001': 5, 'SKU002': 10})
                }
            )
            
            order2, _ = Order.objects.get_or_create(
                id=2,
                defaults={
                    'customer': customer2,
                    'status': 'completed',
                    'order_date': timezone.now() - timedelta(days=1),
                    'priority': 'normal',
                    'sku_quantities': json.dumps({'SKU003': 3, 'SKU004': 7})
                }
            )
            
        return {
            'result': True,
            'providerState': state_name
        }

    @staticmethod
    def verify_pacts():
        """Verify all pacts between frontend and backend"""
        # Configure verifier
        verifier = Verifier(
            provider_name="LedgerLinkBackend",
            provider_base_url="http://localhost:8000",
        )
        
        # Set up provider state URL
        provider_states_setup_url = "http://localhost:8000/pact-states-setup"
        
        # Load contract file
        pact_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'pacts',
            'ledgerlinkfrontend-ledgerlinkbackend.json'
        )
        
        # Verify the contract
        success = verifier.verify_pacts(
            pact_files=[pact_file],
            provider_states_setup_url=provider_states_setup_url,
            verbose=True
        )
        
        assert success, "Pact verification failed"


if __name__ == '__main__':
    # This would be run separately as a provider verification process
    PactProviderTest.verify_pacts()