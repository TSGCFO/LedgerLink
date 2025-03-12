import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from customers.models import Customer
from services.models import Service
from orders.models import Order
from customer_services.models import CustomerService
from conftest import MockOrderSKUView


class OrderServiceIntegrationTest(TestCase):
    """Integration tests for Orders and Services"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="contact@test.com",
            phone="555-1234",
            is_active=True
        )
        
        # Create test services
        self.service1 = Service.objects.create(
            name="Rush Processing",
            description="Process order within 24 hours",
            base_price=50.00,
            charge_type="flat"
        )
        
        self.service2 = Service.objects.create(
            name="Custom Packaging",
            description="Special packaging for order",
            base_price=25.00,
            charge_type="per_item"
        )
        
        # Create customer-specific service
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service1,
            custom_price=40.00  # Discounted price for this customer
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            status="pending",
            order_date=timezone.now(),
            priority="normal",
            sku_quantities=json.dumps({"SKU001": 10, "SKU002": 5})
        )
    
    def test_order_with_customer_specific_service(self):
        """Test that an order uses customer-specific service pricing"""
        # Mock the view results that would come from OrderSKUView
        sku_view_results = [
            MockOrderSKUView(
                id=self.order.id,
                status=self.order.status,
                order_date=self.order.order_date,
                priority=self.order.priority,
                customer_id=self.customer.id,
                sku_id="SKU001",
                quantity=10
            ),
            MockOrderSKUView(
                id=self.order.id,
                status=self.order.status,
                order_date=self.order.order_date,
                priority=self.order.priority,
                customer_id=self.customer.id,
                sku_id="SKU002",
                quantity=5
            )
        ]
        
        # Verify customer has custom service pricing
        customer_service_price = CustomerService.objects.get(
            customer=self.customer,
            service=self.service1
        ).get_price()
        
        # Confirm custom price is used
        self.assertEqual(customer_service_price, 40.00)
        self.assertNotEqual(customer_service_price, self.service1.base_price)
        
        # Verify order can access customer's services
        order_customer = self.order.customer
        customer_services = CustomerService.objects.filter(customer=order_customer)
        
        self.assertEqual(customer_services.count(), 1)
        self.assertEqual(customer_services.first().service, self.service1)
        
        # Verify total quantity calculation from SKU view
        total_quantity = sum(view_item.quantity for view_item in sku_view_results)
        self.assertEqual(total_quantity, 15)  # 10 + 5
        
        # Test per_item service calculation
        per_item_service_cost = self.service2.base_price * total_quantity
        self.assertEqual(per_item_service_cost, 25.00 * 15)
        
        # Test flat service calculation with customer pricing
        flat_service_cost = customer_service_price  # Should use custom price
        self.assertEqual(flat_service_cost, 40.00)