import pytest
import json
import time
from django.test import TestCase, Client
from django.urls import reverse
from django.db import connection, reset_queries
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from customers.models import Customer
from orders.models import Order
from products.models import Product
from rules.models import RuleGroup, Rule, AdvancedRule
from billing.models import BillingReport


class PerformanceTest(TestCase):
    """Performance tests for key endpoints"""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for performance tests - run once for all tests"""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create test customers (100)
        cls.customers = []
        for i in range(1, 101):
            customer = Customer.objects.create(
                company_name=f"Company {i}",
                contact_name=f"Contact {i}",
                email=f"contact{i}@example.com",
                phone=f"555-{i:04d}",
                is_active=True
            )
            cls.customers.append(customer)
        
        # Create test products (50)
        cls.products = []
        for i in range(1, 51):
            product = Product.objects.create(
                name=f"Product {i}",
                sku=f"SKU{i:03d}",
                description=f"Description for product {i}",
                price=10.00 + (i % 10)
            )
            cls.products.append(product)
        
        # Create test orders (200)
        cls.orders = []
        for i in range(1, 201):
            # Rotate through customers
            customer = cls.customers[i % 100]
            
            # Create random sku quantities (3-5 products per order)
            sku_quantities = {}
            for j in range(3, 6):  # 3 to 5 products
                product_idx = (i + j) % 50
                sku_quantities[f"SKU{product_idx+1:03d}"] = j + 1
            
            order = Order.objects.create(
                customer=customer,
                status='pending' if i % 3 == 0 else 'completed',
                order_date=timezone.now() - timedelta(days=i % 30),
                priority='high' if i % 5 == 0 else 'normal',
                sku_quantities=json.dumps(sku_quantities)
            )
            cls.orders.append(order)
        
        # Create rule groups and rules
        cls.rule_group = RuleGroup.objects.create(
            name="Performance Test Rules",
            description="Rules for performance testing"
        )
        
        # Create 20 basic rules
        for i in range(1, 21):
            Rule.objects.create(
                rule_group=cls.rule_group,
                name=f"Basic Rule {i}",
                description=f"Description for rule {i}",
                field="quantity",
                operator="gt",
                value=str(i * 5),
                price_adjustment=i * 0.5,
                adjustment_type="per_item"
            )
        
        # Create 10 advanced rules
        tier_config = {
            "tiers": [
                {"min": 0, "max": 10, "value": 1.00},
                {"min": 11, "max": 50, "value": 0.75},
                {"min": 51, "max": 100, "value": 0.50},
                {"min": 101, "max": 999999, "value": 0.25}
            ]
        }
        
        for i in range(1, 11):
            condition = {
                "operator": "and",
                "conditions": [
                    {
                        "field": "quantity",
                        "operator": "gte",
                        "value": i * 5
                    },
                    {
                        "field": "sku_id",
                        "operator": "in",
                        "value": [f"SKU{j:03d}" for j in range(i, i+10)]
                    }
                ]
            }
            
            calculation = {
                "type": "case_based_tier" if i % 2 == 0 else "percent_discount",
                "field": "quantity" if i % 2 == 0 else None,
                "value": i * 2.5 if i % 2 != 0 else None
            }
            
            AdvancedRule.objects.create(
                rule_group=cls.rule_group,
                name=f"Advanced Rule {i}",
                description=f"Description for advanced rule {i}",
                conditions=json.dumps(condition),
                calculations=json.dumps(calculation),
                tier_config=json.dumps(tier_config) if i % 2 == 0 else None
            )
    
    def setUp(self):
        # Create authenticated client
        self.client = Client()
        self.client.login(username='testuser', password='password123')
    
    def test_orders_list_query_count(self):
        """Test that order list endpoint has acceptable query count"""
        reset_queries()  # Reset query count
        
        # Enable query counting
        with self.settings(DEBUG=True):
            # Make the request
            url = reverse('order-list')
            response = self.client.get(url)
            
            # Check response status
            self.assertEqual(response.status_code, 200)
            
            # Get query count
            query_count = len(connection.queries)
            
            # We expect a reasonable number of queries (e.g., 10 or fewer)
            # The exact number will depend on the implementation
            self.assertLessEqual(query_count, 10, 
                "Order list endpoint made too many queries")
            
            # Print queries for debugging
            # for i, query in enumerate(connection.queries):
            #     print(f"Query {i+1}: {query['sql']}")
    
    def test_orders_list_response_time(self):
        """Test that order list endpoint responds quickly"""
        # Make the request and time it
        url = reverse('order-list')
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Calculate response time
        response_time = end_time - start_time
        
        # The response time should be reasonable (e.g., less than 500ms)
        # Actual threshold depends on your requirements
        self.assertLess(response_time, 0.5, 
            f"Order list response time ({response_time:.2f}s) exceeds threshold")
    
    def test_advanced_rules_list_performance(self):
        """Test that advanced rules endpoint responds quickly and efficiently"""
        reset_queries()  # Reset query count
        
        # Enable query counting
        with self.settings(DEBUG=True):
            # Make the request and time it
            url = reverse('advancedrule-list')
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            # Check response status
            self.assertEqual(response.status_code, 200)
            
            # Get query count
            query_count = len(connection.queries)
            
            # Calculate response time
            response_time = end_time - start_time
            
            # Check both query count and response time
            self.assertLessEqual(query_count, 5, 
                "Advanced rules endpoint made too many queries")
            self.assertLess(response_time, 0.5, 
                f"Advanced rules response time ({response_time:.2f}s) exceeds threshold")
    
    def test_billing_calculation_performance(self):
        """Test billing calculation performance"""
        # Create data for billing calculation
        customer = self.customers[0]
        order_ids = [self.orders[i].id for i in range(5)]  # Use 5 orders
        
        # Make the request and time it
        url = reverse('billing-calculate')
        data = {
            'customer_id': customer.id,
            'order_ids': order_ids,
            'date_range': {
                'start_date': (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': timezone.now().strftime('%Y-%m-%d')
            }
        }
        
        start_time = time.time()
        response = self.client.post(
            url, 
            data=json.dumps(data),
            content_type='application/json'
        )
        end_time = time.time()
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Calculate response time
        response_time = end_time - start_time
        
        # For billing calculations with complex rules, a higher threshold is reasonable
        self.assertLess(response_time, 1.0, 
            f"Billing calculation response time ({response_time:.2f}s) exceeds threshold")
        
        # Verify the calculated data is reasonable
        response_data = json.loads(response.content)
        self.assertIn('total_amount', response_data)
        self.assertIn('line_items', response_data)
        self.assertEqual(len(response_data['line_items']), 
                        sum(len(json.loads(self.orders[i].sku_quantities)) for i in range(5)))
    
    @pytest.mark.slow
    def test_scaling_performance(self):
        """Test performance scaling with increasing data sizes"""
        # Test order list with various page sizes
        url = reverse('order-list')
        page_sizes = [10, 50, 100, 200]
        
        response_times = []
        for size in page_sizes:
            # Make the request and time it
            start_time = time.time()
            response = self.client.get(f"{url}?page_size={size}")
            end_time = time.time()
            
            # Check response status
            self.assertEqual(response.status_code, 200)
            
            # Calculate response time
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Verify response has the right number of items
            response_data = json.loads(response.content)
            results = response_data.get('results', [])
            self.assertLessEqual(len(results), size)
        
        # Verify that response time scales reasonably (not exponentially)
        # This is a simple check; more sophisticated scaling tests might be needed
        if len(response_times) > 1:
            scaling_ratio = response_times[-1] / response_times[0]
            data_ratio = page_sizes[-1] / page_sizes[0]
            
            # Response time should scale sublinearly with data size
            # (e.g., response time for 20x more data should be less than 20x longer)
            self.assertLess(scaling_ratio, data_ratio,
                f"Response time does not scale well: {scaling_ratio:.2f}x slower for {data_ratio:.2f}x more data")