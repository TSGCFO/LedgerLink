"""
Unit tests for the BillingCalculator service.
"""

import pytest
from decimal import Decimal

from billing.billing_calculator import BillingCalculator
from test_utils.factories import OrderFactory, CustomerFactory, ProductFactory

pytestmark = pytest.mark.django_db


class TestBillingCalculator:
    """Tests for the BillingCalculator service."""

    def setup_method(self):
        """Set up test data."""
        self.customer = CustomerFactory()
        self.product = ProductFactory(price=Decimal('100.00'), weight=Decimal('2.5'))
        self.order = OrderFactory(customer=self.customer)
        self.calculator = BillingCalculator(self.order)

    def test_initialization(self):
        """Test that the calculator is initialized correctly."""
        assert self.calculator.order == self.order
        assert hasattr(self.calculator, 'calculate_total')
        assert hasattr(self.calculator, 'calculate_tax')
        assert hasattr(self.calculator, 'calculate_shipping')

    def test_calculate_subtotal(self):
        """Test calculating the subtotal for an order."""
        # Mock order items
        self.calculator._get_order_items = lambda: [
            {'quantity': 2, 'unit_price': Decimal('100.00')},
            {'quantity': 1, 'unit_price': Decimal('50.00')}
        ]
        
        subtotal = self.calculator.calculate_subtotal()
        assert subtotal == Decimal('250.00')

    def test_calculate_tax(self):
        """Test calculating tax for an order."""
        # Mock subtotal and tax rate
        self.calculator.calculate_subtotal = lambda: Decimal('200.00')
        self.calculator._get_tax_rate = lambda: Decimal('0.07')  # 7% tax rate
        
        tax = self.calculator.calculate_tax()
        assert tax == Decimal('14.00')

    def test_calculate_shipping(self):
        """Test calculating shipping costs."""
        # Mock total weight and shipping rate
        self.calculator._get_total_weight = lambda: Decimal('10.0')  # 10 kg
        self.calculator._get_shipping_rate = lambda: Decimal('2.50')  # $2.50 per kg
        
        shipping = self.calculator.calculate_shipping()
        assert shipping == Decimal('25.00')

    def test_calculate_total(self):
        """Test calculating the total cost of an order."""
        # Mock component calculations
        self.calculator.calculate_subtotal = lambda: Decimal('200.00')
        self.calculator.calculate_tax = lambda: Decimal('14.00')
        self.calculator.calculate_shipping = lambda: Decimal('25.00')
        
        total = self.calculator.calculate_total()
        assert total == Decimal('239.00')  # 200 + 14 + 25

    def test_calculate_with_discount(self):
        """Test calculating with a discount applied."""
        # Mock component calculations
        self.calculator.calculate_subtotal = lambda: Decimal('200.00')
        self.calculator.calculate_tax = lambda: Decimal('14.00')
        self.calculator.calculate_shipping = lambda: Decimal('25.00')
        self.calculator._get_discount = lambda: Decimal('20.00')  # $20 discount
        
        total = self.calculator.calculate_total()
        assert total == Decimal('219.00')  # 200 + 14 + 25 - 20

    def test_zero_quantity_item_no_cost(self):
        """Test that items with zero quantity contribute no cost."""
        # Mock order items with a zero quantity
        self.calculator._get_order_items = lambda: [
            {'quantity': 0, 'unit_price': Decimal('100.00')},
            {'quantity': 1, 'unit_price': Decimal('50.00')}
        ]
        
        subtotal = self.calculator.calculate_subtotal()
        assert subtotal == Decimal('50.00')  # Only the second item counts

    def test_free_shipping_threshold(self):
        """Test that shipping is free above a certain threshold."""
        # Mock subtotal and free shipping threshold
        self.calculator.calculate_subtotal = lambda: Decimal('300.00')
        self.calculator._get_free_shipping_threshold = lambda: Decimal('250.00')
        
        shipping = self.calculator.calculate_shipping()
        assert shipping == Decimal('0.00')

    def test_minimum_shipping_cost(self):
        """Test that shipping has a minimum cost even for light items."""
        # Mock total weight (very light) and shipping calculations
        self.calculator._get_total_weight = lambda: Decimal('0.1')  # 0.1 kg
        self.calculator._get_shipping_rate = lambda: Decimal('2.50')  # $2.50 per kg
        self.calculator._get_minimum_shipping = lambda: Decimal('5.00')  # $5 minimum
        
        shipping = self.calculator.calculate_shipping()
        assert shipping == Decimal('5.00')  # Minimum applies