import pytest
from decimal import Decimal
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, PropertyMock

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from billing.billing_calculator import BillingCalculator, OrderCost, ServiceCost, normalize_sku, convert_sku_format
from customers.models import Customer
from orders.models import Order


class BillingCalculatorEdgeCaseTests(TestCase):
    """Test edge cases in the BillingCalculator class."""
    
    def setUp(self):
        # Create test objects
        self.customer = Customer.objects.create(
            company_name="Edge Case Test Co",
            contact_email="edge@test.com",
            phone_number="555-987-6543"
        )
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
        
        # Base calculator
        self.calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.start_date,
            end_date=self.end_date
        )
    
    def test_validate_input_invalid_customer(self):
        """Test validation fails with invalid customer ID."""
        calculator = BillingCalculator(
            customer_id=999999,  # Non-existent customer ID
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        with self.assertRaises(ValidationError):
            calculator.validate_input()
    
    def test_validate_input_invalid_date_range(self):
        """Test validation fails when start date is after end date."""
        calculator = BillingCalculator(
            customer_id=self.customer.id,
            start_date=self.end_date,  # Swapped dates
            end_date=self.start_date
        )
        
        with self.assertRaises(ValidationError):
            calculator.validate_input()
    
    def test_empty_order_list(self):
        """Test handling of empty order list."""
        # Patch the Order.objects.filter method to return empty queryset
        with patch('billing.billing_calculator.Order.objects.filter') as mock_filter:
            mock_filter.return_value = []
            
            # Generate report should return an empty report
            report = self.calculator.generate_report()
            
            self.assertEqual(report.total_amount, Decimal('0'))
            self.assertEqual(len(report.order_costs), 0)
            self.assertEqual(len(report.service_totals), 0)
    
    def test_invalid_sku_quantity_format(self):
        """Test handling of invalid SKU quantity format."""
        # Create an order with invalid SKU format
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="EDGE-001",
            close_date=timezone.now(),
            sku_quantity="invalid-json"  # Invalid JSON
        )
        
        # Mock CustomerService to always apply with invalid SKU quantity
        with patch('billing.billing_calculator.CustomerService.objects.filter') as mock_cs_filter:
            cs_mock = MagicMock()
            cs_mock.service.charge_type = 'quantity'
            cs_mock.get_sku_list.return_value = ['SKU-001']
            cs_mock.unit_price = Decimal('10.00')
            cs_mock.service.id = 1
            cs_mock.service.service_name = 'Test Service'
            
            # Mock the queryset
            mock_qs = MagicMock()
            mock_qs.select_related.return_value.prefetch_related.return_value = [cs_mock]
            mock_cs_filter.return_value = mock_qs
            
            # Add specific patch for orders
            with patch('billing.billing_calculator.Order.objects.filter') as mock_order_filter:
                mock_order_filter.return_value = [order]
                
                # Generate report
                report = self.calculator.generate_report()
                
                # Should have zero cost due to invalid SKU
                self.assertEqual(report.total_amount, Decimal('0'))
    
    def test_sku_quantity_missing_required_fields(self):
        """Test handling of SKU quantity missing required fields."""
        # Create an order with SKU missing quantity
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="EDGE-002",
            close_date=timezone.now(),
            sku_quantity=json.dumps([
                {"sku": "TEST-SKU-1"}  # Missing quantity
            ])
        )
        
        # Mock CustomerService to always apply with invalid SKU quantity
        with patch('billing.billing_calculator.CustomerService.objects.filter') as mock_cs_filter:
            cs_mock = MagicMock()
            cs_mock.service.charge_type = 'quantity'
            cs_mock.get_sku_list.return_value = ['TEST-SKU-1']
            cs_mock.unit_price = Decimal('10.00')
            cs_mock.service.id = 1
            cs_mock.service.service_name = 'Test Service'
            
            # Mock the queryset
            mock_qs = MagicMock()
            mock_qs.select_related.return_value.prefetch_related.return_value = [cs_mock]
            mock_cs_filter.return_value = mock_qs
            
            # Add specific patch for orders
            with patch('billing.billing_calculator.Order.objects.filter') as mock_order_filter:
                mock_order_filter.return_value = [order]
                
                # Generate report
                report = self.calculator.generate_report()
                
                # Should have zero cost due to missing quantity
                self.assertEqual(report.total_amount, Decimal('0'))
    
    def test_zero_quantity_sku(self):
        """Test handling of SKU with zero quantity."""
        # Create an order with zero quantity SKU
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="EDGE-003",
            close_date=timezone.now(),
            sku_quantity=json.dumps([
                {"sku": "TEST-SKU-1", "quantity": 0}  # Zero quantity
            ])
        )
        
        # Mock CustomerService to always apply with zero quantity SKU
        with patch('billing.billing_calculator.CustomerService.objects.filter') as mock_cs_filter:
            cs_mock = MagicMock()
            cs_mock.service.charge_type = 'quantity'
            cs_mock.get_sku_list.return_value = ['TEST-SKU-1']
            cs_mock.unit_price = Decimal('10.00')
            cs_mock.service.id = 1
            cs_mock.service.service_name = 'Test Service'
            
            # Mock the queryset
            mock_qs = MagicMock()
            mock_qs.select_related.return_value.prefetch_related.return_value = [cs_mock]
            mock_cs_filter.return_value = mock_qs
            
            # Add specific patch for orders
            with patch('billing.billing_calculator.Order.objects.filter') as mock_order_filter:
                mock_order_filter.return_value = [order]
                
                # Generate report
                report = self.calculator.generate_report()
                
                # Should have zero cost due to zero quantity
                self.assertEqual(report.total_amount, Decimal('0'))
    
    def test_negative_quantity_sku(self):
        """Test handling of SKU with negative quantity."""
        # Create an order with negative quantity SKU
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="EDGE-004",
            close_date=timezone.now(),
            sku_quantity=json.dumps([
                {"sku": "TEST-SKU-1", "quantity": -5}  # Negative quantity
            ])
        )
        
        # Mock CustomerService to always apply with negative quantity SKU
        with patch('billing.billing_calculator.CustomerService.objects.filter') as mock_cs_filter:
            cs_mock = MagicMock()
            cs_mock.service.charge_type = 'quantity'
            cs_mock.get_sku_list.return_value = ['TEST-SKU-1']
            cs_mock.unit_price = Decimal('10.00')
            cs_mock.service.id = 1
            cs_mock.service.service_name = 'Test Service'
            
            # Mock the queryset
            mock_qs = MagicMock()
            mock_qs.select_related.return_value.prefetch_related.return_value = [cs_mock]
            mock_cs_filter.return_value = mock_qs
            
            # Add specific patch for orders
            with patch('billing.billing_calculator.Order.objects.filter') as mock_order_filter:
                mock_order_filter.return_value = [order]
                
                # Generate report
                report = self.calculator.generate_report()
                
                # Should have zero cost due to negative quantity
                self.assertEqual(report.total_amount, Decimal('0'))
    
    def test_unknown_charge_type(self):
        """Test handling of unknown charge type."""
        # Create an order
        order = Order.objects.create(
            customer=self.customer,
            transaction_id="EDGE-005",
            close_date=timezone.now(),
            sku_quantity=json.dumps([
                {"sku": "TEST-SKU-1", "quantity": 5}
            ])
        )
        
        # Mock CustomerService with unknown charge type
        with patch('billing.billing_calculator.CustomerService.objects.filter') as mock_cs_filter:
            cs_mock = MagicMock()
            cs_mock.service.charge_type = 'unknown_type'  # Unknown charge type
            cs_mock.unit_price = Decimal('10.00')
            cs_mock.service.id = 1
            cs_mock.service.service_name = 'Test Service'
            
            # Mock rule evaluation to always return True
            with patch('billing.billing_calculator.RuleEvaluator.evaluate_rule_group', return_value=True):
                # Mock the queryset
                mock_qs = MagicMock()
                mock_qs.select_related.return_value.prefetch_related.return_value = [cs_mock]
                mock_cs_filter.return_value = mock_qs
                
                # Add specific patch for orders and rule_groups
                with patch('billing.billing_calculator.Order.objects.filter') as mock_order_filter:
                    mock_order_filter.return_value = [order]
                    
                    # Mock rule groups dict to be empty
                    with patch('billing.billing_calculator.RuleGroup.objects.filter') as mock_rg_filter:
                        mock_rg_filter.return_value.select_related.return_value.prefetch_related.return_value = []
                        
                        # Generate report
                        report = self.calculator.generate_report()
                        
                        # Should have zero cost due to unknown charge type
                        self.assertEqual(report.total_amount, Decimal('0'))


class OrderCostTests(TestCase):
    """Test OrderCost class functionality."""
    
    def test_order_cost_initialization(self):
        """Test OrderCost initialization."""
        # Initialize with just order_id
        order_cost = OrderCost(order_id=123)
        self.assertEqual(order_cost.order_id, 123)
        self.assertEqual(order_cost.service_costs, [])
        self.assertEqual(order_cost.total_amount, Decimal('0'))
        
        # Initialize with all parameters
        service_cost = ServiceCost(service_id=1, service_name="Test Service", amount=Decimal('10.50'))
        order_cost = OrderCost(
            order_id=123,
            service_costs=[service_cost],
            total_amount=Decimal('10.50')
        )
        self.assertEqual(order_cost.order_id, 123)
        self.assertEqual(len(order_cost.service_costs), 1)
        self.assertEqual(order_cost.total_amount, Decimal('10.50'))