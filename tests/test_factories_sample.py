"""
Sample test file demonstrating how to use the factory classes.

This file provides examples of using the factories defined in factories.py 
to create realistic test data for various test scenarios.
"""

import pytest
import json
from decimal import Decimal
from django.test import TestCase
from django.utils.timezone import now

# Import factory classes
from tests.factories import (
    # Core factories
    UserFactory, AdminUserFactory, 
    CustomerFactory, RealisticCustomerFactory,
    OrderFactory, RealisticOrderFactory, 
    ProductFactory, ServiceFactory,
    
    # Specialized factories
    SubmittedOrderFactory, ShippedOrderFactory, DeliveredOrderFactory,
    CancelledOrderFactory, HighPriorityOrderFactory, LowPriorityOrderFactory,
    LargeOrderFactory, OrderWithComplexDataFactory,
    
    # Service-related factories
    FixedChargeServiceFactory, PerUnitServiceFactory,
    TieredServiceFactory, CaseTierServiceFactory,
    CustomerServiceFactory,
    
    # Rule factories
    RuleGroupFactory, RuleFactory, AdvancedRuleFactory,
    
    # Billing factories
    BillingReportFactory, BillingReportDetailFactory,
    
    # Other module factories
    MaterialFactory, BoxPriceFactory,
    USShippingFactory, CADShippingFactory,
    InsertFactory,
    
    # Helper functions
    create_order_with_services, create_billing_scenario,
    
    # Traits
    WithNotesTrait, WithTrackingHistoryTrait
)


class FactoriesSampleTests(TestCase):
    """Test cases demonstrating how to use the factory classes."""
    
    def test_basic_factories(self):
        """Test basic factory usage."""
        # Create a user
        user = UserFactory()
        self.assertTrue(user.id is not None)
        self.assertTrue(user.check_password('password123'))
        
        # Create an admin user
        admin = AdminUserFactory()
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        
        # Create a customer
        customer = CustomerFactory()
        self.assertTrue(customer.id is not None)
        self.assertEqual(customer.country, 'US')
        self.assertTrue(customer.is_active)
        
        # Create a product for this customer
        product = ProductFactory(customer=customer)
        self.assertTrue(product.id is not None)
        self.assertEqual(product.customer, customer)
        
        # Create a service
        service = ServiceFactory()
        self.assertTrue(service.id is not None)
        
        # Link customer and service
        customer_service = CustomerServiceFactory(
            customer=customer,
            service=service
        )
        self.assertTrue(customer_service.id is not None)
        self.assertEqual(customer_service.customer, customer)
        self.assertEqual(customer_service.service, service)
        
        # Create an order
        order = OrderFactory(customer=customer)
        self.assertTrue(order.id is not None)
        self.assertEqual(order.customer, customer)
        self.assertTrue(isinstance(order.transaction_id, int))
        self.assertTrue(order.transaction_id >= 100000)
        
        # Check SKU quantity format
        self.assertTrue(isinstance(order.sku_quantity, dict))
        self.assertTrue(len(order.sku_quantity) > 0)
    
    def test_specialized_order_factories(self):
        """Test specialized order factory variations."""
        # Create orders with different statuses
        submitted_order = SubmittedOrderFactory()
        self.assertEqual(submitted_order.status, 'submitted')
        self.assertIsNotNone(submitted_order.submission_date)
        
        shipped_order = ShippedOrderFactory()
        self.assertEqual(shipped_order.status, 'shipped')
        self.assertIsNotNone(shipped_order.submission_date)
        self.assertIsNotNone(shipped_order.ship_date)
        
        delivered_order = DeliveredOrderFactory()
        self.assertEqual(delivered_order.status, 'delivered')
        self.assertIsNotNone(delivered_order.delivery_date)
        
        cancelled_order = CancelledOrderFactory()
        self.assertEqual(cancelled_order.status, 'cancelled')
        self.assertIsNotNone(cancelled_order.cancellation_date)
        
        # Create orders with different priorities
        high_priority = HighPriorityOrderFactory()
        self.assertEqual(high_priority.priority, 'high')
        
        low_priority = LowPriorityOrderFactory()
        self.assertEqual(low_priority.priority, 'low')
        
        # Create a large order for performance testing
        large_order = LargeOrderFactory()
        self.assertTrue(len(large_order.sku_quantity) >= 20)
        
        # Create an order with complex data structure
        complex_order = OrderWithComplexDataFactory()
        for sku, data in complex_order.sku_quantity.items():
            self.assertTrue(isinstance(data, dict))
            self.assertIn('quantity', data)
            self.assertIn('cases', data)
            self.assertIn('picks', data)
            self.assertIn('dimensions', data)
    
    def test_service_factories(self):
        """Test service-related factories."""
        # Create services with different charge types
        fixed_service = FixedChargeServiceFactory()
        self.assertEqual(fixed_service.charge_type, 'fixed')
        
        per_unit_service = PerUnitServiceFactory()
        self.assertEqual(per_unit_service.charge_type, 'per_unit')
        
        tiered_service = TieredServiceFactory()
        self.assertEqual(tiered_service.charge_type, 'tiered')
        
        case_tier_service = CaseTierServiceFactory()
        self.assertEqual(case_tier_service.charge_type, 'case_based_tier')
    
    def test_rule_factories(self):
        """Test rule-related factories."""
        # Create a customer service first
        cs = CustomerServiceFactory()
        
        # Create a rule group with explicit customer service
        rule_group = RuleGroupFactory(customer_service=cs)
        self.assertEqual(rule_group.customer_service, cs)
        
        # Create a basic rule
        rule = RuleFactory(rule_group=rule_group)
        self.assertEqual(rule.rule_group, rule_group)
        self.assertTrue(rule.field in ['weight', 'line_items', 'total_item_qty', 
                                     'volume', 'packages', 'sku_count', 'is_rush'])
        self.assertTrue(rule.operator in ['eq', 'ne', 'gt', 'lt', 'gte', 'lte'])
        
        # Create an advanced rule
        advanced_rule = AdvancedRuleFactory(rule_group=rule_group)
        self.assertEqual(advanced_rule.rule_group, rule_group)
        
        # Check structure of conditions, calculations, tier_config
        self.assertTrue(isinstance(advanced_rule.conditions, dict))
        self.assertTrue(isinstance(advanced_rule.calculations, dict))
        self.assertTrue(isinstance(advanced_rule.tier_config, dict))
        
        # Check tier configuration structure
        self.assertIn('tiers', advanced_rule.tier_config)
        self.assertTrue(len(advanced_rule.tier_config['tiers']) >= 2)
        for tier in advanced_rule.tier_config['tiers']:
            self.assertIn('min', tier)
            self.assertIn('value', tier)
    
    def test_billing_factories(self):
        """Test billing-related factories."""
        # Create customer and order
        customer = CustomerFactory()
        order = OrderFactory(customer=customer)
        
        # Create billing report
        report = BillingReportFactory(customer=customer)
        self.assertEqual(report.customer, customer)
        
        # Check report_data structure
        self.assertTrue(isinstance(report.report_data, dict))
        self.assertIn('orders', report.report_data)
        self.assertIn('total_amount', report.report_data)
        self.assertIn('service_totals', report.report_data)
        
        # Create billing report detail
        detail = BillingReportDetailFactory(report=report, order=order)
        self.assertEqual(detail.report, report)
        self.assertEqual(detail.order, order)
        
        # Check service_breakdown structure
        self.assertTrue(isinstance(detail.service_breakdown, dict))
        self.assertIn('services', detail.service_breakdown)
    
    def test_shipping_factories(self):
        """Test shipping-related factories."""
        # Create order
        order = OrderFactory()
        
        # Create US shipping
        us_shipping = USShippingFactory(order=order)
        self.assertEqual(us_shipping.order, order)
        self.assertTrue(us_shipping.carrier in ['USPS', 'UPS', 'FedEx', 'DHL'])
        self.assertTrue(isinstance(us_shipping.shipping_cost, Decimal))
        
        # Create CAD shipping
        cad_shipping = CADShippingFactory(order=order)
        self.assertEqual(cad_shipping.order, order)
        self.assertTrue(cad_shipping.carrier in ['Canada Post', 'Purolator', 
                                               'UPS Canada', 'DHL Canada'])
        self.assertTrue(isinstance(cad_shipping.shipping_cost, Decimal))
        self.assertTrue(isinstance(cad_shipping.duties_and_taxes, Decimal))
    
    def test_material_factories(self):
        """Test material-related factories."""
        # Create material
        material = MaterialFactory()
        
        # Check properties structure
        self.assertTrue(isinstance(material.properties, dict))
        self.assertIn('color', material.properties)
        self.assertIn('thickness', material.properties)
        self.assertIn('weight_per_sqft', material.properties)
        
        # Create box price
        box_price = BoxPriceFactory(material=material)
        self.assertEqual(box_price.material, material)
        
        # Check dimensions structure
        self.assertTrue(isinstance(box_price.dimensions, dict))
        self.assertIn('length', box_price.dimensions)
        self.assertIn('width', box_price.dimensions)
        self.assertIn('height', box_price.dimensions)
    
    def test_realistic_data_factories(self):
        """Test factories that produce realistic data."""
        # Create realistic customer
        customer = RealisticCustomerFactory()
        self.assertTrue(len(customer.company_name.split()) >= 2)
        
        # Create realistic order
        order = RealisticOrderFactory()
        
        # SKU patterns should match production-like patterns
        sku_keys = list(order.sku_quantity.keys())
        # Each SKU should follow one of the format patterns
        for sku in sku_keys:
            # Check if SKU matches at least one of the expected patterns
            pattern_match = any([
                # ABC-1234 pattern
                (len(sku.split('-')) == 2 and 
                 all(c.isalpha() for c in sku.split('-')[0]) and 
                 sku.split('-')[1].isdigit()),
                # A123 pattern
                (len(sku) == 4 and sku[0].isalpha() and sku[1:].isdigit()),
                # 123A pattern
                (len(sku) == 4 and sku[-1].isalpha() and sku[:-1].isdigit()),
                # ABCD12345 pattern (Alpha prefix followed by digits)
                (any(c.isalpha() for c in sku) and any(c.isdigit() for c in sku))
            ])
            self.assertTrue(pattern_match, f"SKU {sku} doesn't match expected patterns")
    
    def test_factory_traits(self):
        """Test factory traits."""
        # Create order with notes trait
        order_with_notes = OrderFactory.create(WithNotesTrait())
        self.assertTrue(len(order_with_notes.notes.split('\n')) >= 3)
        
        # Create order with tracking history trait
        order_with_history = OrderFactory.create(WithTrackingHistoryTrait())
        self.assertTrue(isinstance(order_with_history.tracking_history, list))
        self.assertTrue(len(order_with_history.tracking_history) >= 3)
        
        # Check tracking event structure
        for event in order_with_history.tracking_history:
            self.assertIn('timestamp', event)
            self.assertIn('status', event)
            self.assertIn('location', event)
            self.assertIn('user', event)
    
    def test_helper_functions(self):
        """Test helper functions."""
        # Test create_order_with_services
        order, services, rules = create_order_with_services()
        self.assertTrue(isinstance(order.transaction_id, int))
        self.assertTrue(len(services) >= 1)
        self.assertTrue(len(rules) >= 2)  # At least one basic and one advanced rule
        
        # Test create_billing_scenario
        customer, orders, report, details = create_billing_scenario(orders_count=3)
        self.assertEqual(len(orders), 3)
        self.assertEqual(len(details), 3)
        self.assertEqual(report.customer, customer)
        for detail in details:
            self.assertEqual(detail.report, report)
            self.assertTrue(detail.order in orders)


class TestFactoryCombinations(TestCase):
    """Test cases demonstrating factory combinations for complex scenarios."""
    
    def test_order_with_shipping_and_billing(self):
        """Create order with shipping and billing."""
        # Create customer
        customer = RealisticCustomerFactory()
        
        # Create order
        order = RealisticOrderFactory(customer=customer)
        
        # Add shipping based on country
        if order.ship_to_country == 'US':
            shipping = USShippingFactory(order=order)
        else:
            shipping = CADShippingFactory(order=order)
        
        # Create service and customer service
        service = TieredServiceFactory()
        customer_service = CustomerServiceFactory(
            customer=customer,
            service=service
        )
        
        # Create rule group and rules
        rule_group = RuleGroupFactory(customer_service=customer_service)
        basic_rule = RuleFactory(
            rule_group=rule_group,
            field='weight',
            operator='gt',
            value=50
        )
        advanced_rule = AdvancedRuleFactory(rule_group=rule_group)
        
        # Create billing report
        report = BillingReportFactory(customer=customer)
        
        # Create billing report detail
        detail = BillingReportDetailFactory(
            report=report,
            order=order
        )
        
        # Verify relationships
        self.assertEqual(shipping.order, order)
        self.assertEqual(order.customer, customer)
        self.assertEqual(rule_group.customer_service, customer_service)
        self.assertEqual(basic_rule.rule_group, rule_group)
        self.assertEqual(detail.report, report)
        self.assertEqual(detail.order, order)
    
    def test_customer_with_multiple_orders(self):
        """Create customer with multiple orders in different states."""
        # Create customer
        customer = RealisticCustomerFactory()
        
        # Create orders in different states
        draft_order = OrderFactory(customer=customer)
        submitted_order = SubmittedOrderFactory(customer=customer)
        shipped_order = ShippedOrderFactory(customer=customer)
        delivered_order = DeliveredOrderFactory(customer=customer)
        cancelled_order = CancelledOrderFactory(customer=customer)
        
        # Create products linked to customer
        products = [ProductFactory(customer=customer) for _ in range(3)]
        
        # Create services and link to customer
        services = []
        for i in range(3):
            service = ServiceFactory()
            customer_service = CustomerServiceFactory(
                customer=customer,
                service=service,
                skus=products  # Link all products to this service
            )
            services.append(customer_service)
        
        # Create billing report with all orders
        report = BillingReportFactory(customer=customer)
        
        # Create billing report details for each order
        details = []
        for order in [draft_order, submitted_order, shipped_order, 
                     delivered_order, cancelled_order]:
            detail = BillingReportDetailFactory(
                report=report,
                order=order
            )
            details.append(detail)
        
        # Verify customer has multiple orders
        orders = [draft_order, submitted_order, shipped_order, 
                delivered_order, cancelled_order]
        for order in orders:
            self.assertEqual(order.customer, customer)
        
        # Verify billing report contains all orders
        self.assertEqual(len(details), 5)
        for detail in details:
            self.assertEqual(detail.report, report)
            self.assertIn(detail.order, orders)


if __name__ == '__main__':
    pytest.main()