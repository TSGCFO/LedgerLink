import time
import random
from datetime import datetime, timedelta
from decimal import Decimal
import json

from django.test import TestCase
from django.core.cache import cache
from django.utils import timezone
from django.test.utils import override_settings

from billing.models import BillingReport
from billing.services import BillingReportService
from billing.billing_calculator import BillingCalculator, generate_billing_report

from .factories import (
    CustomerFactory, OrderFactory, ServiceFactory,
    CustomerServiceFactory, RuleFactory, RuleGroupFactory,
    UserFactory
)


class PerformanceTestMixin:
    """Mixin with utility methods for performance testing."""
    
    def measure_execution_time(self, callable_func, *args, **kwargs):
        """Measure execution time of a function in milliseconds."""
        start_time = time.time()
        result = callable_func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return result, execution_time


class BillingCalculatorPerformanceTests(TestCase, PerformanceTestMixin):
    """Performance tests for the BillingCalculator."""
    
    def setUp(self):
        # Clear cache before tests
        cache.clear()
        
        # Create customer
        self.customer = CustomerFactory()
        
        # Create services
        self.service1 = ServiceFactory(service_name="Service 1", charge_type="single")
        self.service2 = ServiceFactory(service_name="Service 2", charge_type="quantity")
        
        # Create customer services
        self.cs1 = CustomerServiceFactory(
            customer=self.customer,
            service=self.service1,
            unit_price=Decimal('10.00')
        )
        self.cs2 = CustomerServiceFactory(
            customer=self.customer,
            service=self.service2,
            unit_price=Decimal('2.50')
        )
        
        # Create date range
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
        
        # Create test user
        self.user = UserFactory()
    
    def test_performance_scaling_with_order_count(self):
        """Test how performance scales with increasing numbers of orders."""
        order_counts = [5, 10, 20]
        execution_times = []
        
        for count in order_counts:
            # Create orders for this test case
            orders = self._create_test_orders(count)
            
            # Measure report generation time
            _, execution_time = self.measure_execution_time(
                generate_billing_report,
                customer_id=self.customer.id,
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            execution_times.append(execution_time)
            
            # Clean up orders to avoid interference between test cases
            for order in orders:
                order.delete()
            
            # Output for informational purposes
            print(f"Orders: {count}, Execution time: {execution_time:.2f} ms")
        
        # Verify scaling is roughly linear (or better)
        # We expect time to increase with more orders, but not exponentially
        if len(execution_times) >= 3:
            ratio1 = execution_times[1] / execution_times[0]
            ratio2 = execution_times[2] / execution_times[1]
            
            # The ratio of the ratios should be < 2 for acceptable scaling
            self.assertLess(ratio2 / ratio1, 2.0, 
                f"Performance scaling is worse than expected: {ratio1:.2f}, {ratio2:.2f}")
    
    def test_performance_with_complex_rules(self):
        """Test performance with varying complexity of rules."""
        # Create a set of orders
        orders = self._create_test_orders(10)
        
        # Create rule structure of increasing complexity
        test_cases = [
            ("Simple", 1, "Single Rule"),
            ("Medium", 5, "Five Rules"),
            ("Complex", 15, "Fifteen Rules")
        ]
        
        for complexity, rule_count, description in test_cases:
            # Create rule group
            rule_group = RuleGroupFactory(
                customer_service=self.cs1,
                logic_operator="OR",
                rules_count=0
            )
            
            # Add specified number of rules
            for i in range(rule_count):
                field = random.choice(["weight_lb", "total_item_qty", "ship_to_country"])
                operator = random.choice(["eq", "gt", "lt", "contains"])
                value = str(random.randint(1, 100))
                
                RuleFactory(
                    field=field,
                    operator=operator,
                    value=value,
                    set_rule_group=rule_group
                )
            
            # Measure execution time
            _, execution_time = self.measure_execution_time(
                generate_billing_report,
                customer_id=self.customer.id,
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Output for informational purposes
            print(f"Rules complexity: {complexity}, Rules: {rule_count}, Time: {execution_time:.2f} ms")
            
            # Clean up rule group to avoid interference
            rule_group.delete()
        
        # Clean up orders
        for order in orders:
            order.delete()
    
    def test_cached_vs_uncached_performance(self):
        """Test performance difference between cached and uncached report generation."""
        # Create test orders
        orders = self._create_test_orders(15)
        
        # Create service
        report_service = BillingReportService(self.user)
        
        # Clear cache to start
        cache.clear()
        
        # First call - uncached
        _, uncached_time = self.measure_execution_time(
            report_service.generate_report,
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Second call - should use cache
        _, cached_time = self.measure_execution_time(
            report_service.generate_report,
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Output for informational purposes
        print(f"Uncached time: {uncached_time:.2f} ms, Cached time: {cached_time:.2f} ms")
        
        # Cached should be significantly faster
        self.assertLess(cached_time, uncached_time * 0.5, 
            "Cached performance is not significantly better than uncached")
        
        # Clean up orders
        for order in orders:
            order.delete()
    
    def test_export_format_performance_comparison(self):
        """Compare performance of different export formats."""
        # Create test orders
        orders = self._create_test_orders(10)
        
        # Create service
        report_service = BillingReportService(self.user)
        
        # Test different formats
        formats = ['preview', 'csv', 'excel', 'pdf']
        execution_times = {}
        
        for format_name in formats:
            _, execution_time = self.measure_execution_time(
                report_service.generate_report,
                self.customer.id,
                self.start_date,
                self.end_date,
                output_format=format_name
            )
            
            execution_times[format_name] = execution_time
            
            # Output for informational purposes
            print(f"Format: {format_name}, Execution time: {execution_time:.2f} ms")
        
        # CSV should be faster than Excel and PDF
        self.assertLess(execution_times['csv'], execution_times['excel'], 
            "CSV generation should be faster than Excel")
        self.assertLess(execution_times['csv'], execution_times['pdf'], 
            "CSV generation should be faster than PDF")
        
        # Preview should be the fastest (usually)
        self.assertLess(execution_times['preview'], execution_times['excel'], 
            "Preview generation should be faster than Excel")
        
        # Clean up orders
        for order in orders:
            order.delete()
    
    def _create_test_orders(self, count):
        """Helper method to create a specified number of test orders."""
        orders = []
        for i in range(count):
            order = OrderFactory(
                customer=self.customer,
                transaction_id=f"ORD-{i+1:04d}",
                order_date=self.start_date + timedelta(days=i),
                close_date=self.start_date + timedelta(days=i+1),
                weight_lb=random.uniform(5.0, 25.0),
                total_item_qty=random.randint(5, 30),
                sku_quantity=json.dumps([
                    {"sku": f"SKU-{j+1}", "quantity": random.randint(1, 5)}
                    for j in range(random.randint(1, 5))
                ])
            )
            orders.append(order)
        return orders


class LargeDatasetTests(TestCase, PerformanceTestMixin):
    """Tests using larger datasets to assess performance with realistic workloads."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        print("\nPreparing large dataset test environment...")
        start_time = time.time()
        
        # Create customer
        cls.customer = CustomerFactory()
        
        # Create services (variety of charge types)
        cls.services = [
            ServiceFactory(service_name=f"Service {i}", 
                          charge_type=random.choice(["single", "quantity"]))
            for i in range(1, 6)  # 5 services
        ]
        
        # Create customer services
        cls.customer_services = [
            CustomerServiceFactory(
                customer=cls.customer,
                service=service,
                unit_price=Decimal(str(random.uniform(5.0, 25.0)))
            )
            for service in cls.services
        ]
        
        # Add some rules to services
        for cs in cls.customer_services[:3]:  # Add rules to first 3 services
            rule_group = RuleGroupFactory(
                customer_service=cs,
                logic_operator=random.choice(["AND", "OR"]),
                rules_count=0
            )
            
            # Add 1-3 rules per group
            for _ in range(random.randint(1, 3)):
                field = random.choice(["weight_lb", "total_item_qty", "ship_to_country"])
                operator = random.choice(["eq", "gt", "lt", "contains"])
                value = str(random.randint(1, 20) if field != "ship_to_country" else "US")
                
                RuleFactory(field=field, operator=operator, value=value, set_rule_group=rule_group)
        
        # Create date range (last 90 days)
        cls.start_date = timezone.now().date() - timedelta(days=90)
        cls.end_date = timezone.now().date()
        
        # Create test user
        cls.user = UserFactory()
        
        # Create orders - larger dataset
        cls.orders = []
        order_count = 50  # Create 50 orders
        
        for i in range(order_count):
            order_date = cls.start_date + timedelta(days=random.randint(0, 85))
            close_date = order_date + timedelta(days=random.randint(1, 5))
            
            order = OrderFactory(
                customer=cls.customer,
                transaction_id=f"LARGE-{i+1:04d}",
                order_date=order_date,
                close_date=close_date,
                weight_lb=random.uniform(5.0, 50.0),
                total_item_qty=random.randint(5, 100),
                sku_quantity=json.dumps([
                    {"sku": f"SKU-{j+1}", "quantity": random.randint(1, 10)}
                    for j in range(random.randint(1, 10))  # 1-10 SKUs per order
                ])
            )
            cls.orders.append(order)
        
        end_time = time.time()
        setup_time = end_time - start_time
        print(f"Large dataset environment ready (setup took {setup_time:.2f} seconds)")
    
    @classmethod
    def tearDownClass(cls):
        # Clean up created objects
        for order in cls.orders:
            order.delete()
        
        for cs in cls.customer_services:
            cs.delete()
        
        for service in cls.services:
            service.delete()
        
        cls.customer.delete()
        cls.user.delete()
        
        super().tearDownClass()
    
    @override_settings(MAX_REPORT_DATE_RANGE=100)  # Increase max range for this test
    def test_large_dataset_report_generation(self):
        """Test report generation performance with a large dataset."""
        # Create service
        report_service = BillingReportService(self.user)
        
        print(f"\nGenerating report for {len(self.orders)} orders...")
        
        # Measure time to generate report
        report_data, execution_time = self.measure_execution_time(
            report_service.generate_report,
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Log performance metrics
        print(f"Report generation completed in {execution_time:.2f} ms")
        print(f"Total orders processed: {len(report_data['orders'])}")
        print(f"Total services: {len(report_data['service_totals'])}")
        
        # Assert reasonable performance (adjust threshold as needed for your environment)
        # For 50 orders, we expect processing in under 30 seconds (30000 ms)
        max_expected_time = 30000  # 30 seconds in milliseconds
        self.assertLess(execution_time, max_expected_time, 
            f"Report generation took too long: {execution_time:.2f} ms > {max_expected_time} ms")
    
    @override_settings(MAX_REPORT_DATE_RANGE=100)  # Increase max range for this test
    def test_large_dataset_excel_export(self):
        """Test Excel export performance with a large dataset."""
        # Create service
        report_service = BillingReportService(self.user)
        
        print(f"\nGenerating Excel report for {len(self.orders)} orders...")
        
        # Measure time to generate Excel report
        _, execution_time = self.measure_execution_time(
            report_service.generate_report,
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='excel'
        )
        
        # Log performance metrics
        print(f"Excel report generation completed in {execution_time:.2f} ms")
        
        # Assert reasonable performance
        max_expected_time = 40000  # 40 seconds in milliseconds
        self.assertLess(execution_time, max_expected_time, 
            f"Excel report generation took too long: {execution_time:.2f} ms > {max_expected_time} ms")


class ReportCachePerformanceTests(TestCase, PerformanceTestMixin):
    """Tests for report cache performance."""
    
    def setUp(self):
        # Clear cache before tests
        cache.clear()
        
        # Create customer
        self.customer = CustomerFactory()
        
        # Create services
        self.service = ServiceFactory(service_name="Service 1", charge_type="single")
        
        # Create customer services
        self.cs = CustomerServiceFactory(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('10.00')
        )
        
        # Create date range
        self.start_date = timezone.now().date() - timedelta(days=30)
        self.end_date = timezone.now().date()
        
        # Create test user
        self.user = UserFactory()
        
        # Create 20 orders
        self.orders = self._create_test_orders(20)
        
        # Create service
        self.report_service = BillingReportService(self.user)
    
    def tearDown(self):
        # Clean up orders
        for order in self.orders:
            order.delete()
    
    @override_settings(REPORT_CACHE_TIMEOUT=60)  # 1 minute timeout for testing
    def test_cache_hit_rate(self):
        """Test cache hit rate with multiple report requests."""
        # Generate initial report to populate cache
        self.report_service.generate_report(
            self.customer.id,
            self.start_date,
            self.end_date,
            output_format='preview'
        )
        
        # Mock cache.get to track hits and misses
        original_get = cache.get
        cache_hits = 0
        cache_misses = 0
        
        def mock_get(*args, **kwargs):
            nonlocal cache_hits, cache_misses
            result = original_get(*args, **kwargs)
            if result is not None:
                cache_hits += 1
            else:
                cache_misses += 1
            return result
        
        # Test with multiple report requests for the same parameters
        with patch('django.core.cache.cache.get', side_effect=mock_get):
            for _ in range(5):
                self.report_service.generate_report(
                    self.customer.id,
                    self.start_date,
                    self.end_date,
                    output_format='preview'
                )
        
        # Output for informational purposes
        print(f"Cache hits: {cache_hits}, Cache misses: {cache_misses}, Hit rate: {cache_hits/(cache_hits+cache_misses):.2f}")
        
        # Cache hit rate should be high (at least 0.8 or 80%)
        hit_rate = cache_hits / (cache_hits + cache_misses)
        self.assertGreaterEqual(hit_rate, 0.8, f"Cache hit rate too low: {hit_rate:.2f}")
    
    def _create_test_orders(self, count):
        """Helper method to create a specified number of test orders."""
        orders = []
        for i in range(count):
            order = OrderFactory(
                customer=self.customer,
                transaction_id=f"ORD-{i+1:04d}",
                order_date=self.start_date + timedelta(days=i % 30),
                close_date=self.start_date + timedelta(days=(i % 30)+1),
                weight_lb=random.uniform(5.0, 25.0),
                total_item_qty=random.randint(5, 30)
            )
            orders.append(order)
        return orders