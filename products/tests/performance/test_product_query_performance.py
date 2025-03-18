import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

from django.db import connection
from django.test import TransactionTestCase
from django.db.models import Q

from products.models import Product
from products.tests.factories import ProductFactory, CustomerFactory


@pytest.mark.performance
class ProductPerformanceTests(TransactionTestCase):
    """Performance tests for Product model queries."""
    
    def setUp(self):
        """Set up performance tests with a large number of products."""
        # Create customers
        self.customers = [CustomerFactory() for _ in range(5)]
        
        # Create a controlled number of products for consistent testing
        self.product_count = 100  # Adjust based on your needs
        self.products = []
        
        # Create products distributed across customers
        for i in range(self.product_count):
            customer = self.customers[i % len(self.customers)]
            self.products.append(
                ProductFactory(
                    customer=customer,
                    sku=f"TEST-SKU-{i:04d}",
                    labeling_unit_1="BOX",
                    labeling_quantity_1=i % 50 + 1
                )
            )
        
        # Create products with specific SKUs for search testing
        for i in range(10):
            ProductFactory(
                customer=self.customers[0],
                sku=f"SEARCHABLE-{i}",
                labeling_unit_1="CASE",
                labeling_quantity_1=10
            )
        
        # Reset connection to simulate real-world usage
        connection.close()
    
    def test_product_retrieve_performance(self):
        """Test the performance of retrieving a product by ID."""
        # Get a specific product ID
        product_id = self.products[0].id
        
        # Measure time to retrieve the product
        start_time = time.time()
        Product.objects.get(id=product_id)
        end_time = time.time()
        
        # The retrieval should be very fast (under 10ms)
        self.assertLess(end_time - start_time, 0.01, "Product retrieval by ID took too long")
    
    def test_product_filter_by_customer_performance(self):
        """Test the performance of filtering products by customer."""
        # Get a specific customer
        customer = self.customers[0]
        
        # Measure time to filter products
        start_time = time.time()
        products = Product.objects.filter(customer=customer)
        product_count = products.count()
        end_time = time.time()
        
        # Ensure we found the expected products
        expected_count = sum(1 for p in self.products if p.customer == customer)
        self.assertEqual(product_count, expected_count)
        
        # The filtering should be reasonably fast (under 50ms for 100 products)
        self.assertLess(end_time - start_time, 0.05, "Filtering products by customer took too long")
    
    def test_product_search_by_sku_performance(self):
        """Test the performance of searching products by SKU."""
        # Measure time to search by SKU
        start_time = time.time()
        products = Product.objects.filter(sku__icontains="SEARCHABLE")
        product_count = products.count()
        end_time = time.time()
        
        # Ensure we found the expected products
        self.assertEqual(product_count, 10)
        
        # The search should be reasonably fast (under 50ms for 100 products)
        self.assertLess(end_time - start_time, 0.05, "Searching products by SKU took too long")
    
    def test_complex_product_query_performance(self):
        """Test the performance of complex product queries."""
        # Measure time for a complex query with multiple conditions
        start_time = time.time()
        products = Product.objects.filter(
            Q(sku__icontains="TEST") & 
            Q(labeling_unit_1="BOX") &
            Q(labeling_quantity_1__gt=25)
        )
        product_count = products.count()
        end_time = time.time()
        
        # Ensure we found some products
        self.assertGreater(product_count, 0)
        
        # The complex query should be reasonably fast (under 100ms)
        self.assertLess(end_time - start_time, 0.1, "Complex product query took too long")
    
    def test_order_by_performance(self):
        """Test the performance of ordering products."""
        # Measure time to order products by SKU
        start_time = time.time()
        products = Product.objects.all().order_by('sku')
        product_count = products.count()
        end_time = time.time()
        
        # Ensure we got all products
        self.assertEqual(product_count, self.product_count + 10)  # Regular products + searchable ones
        
        # The ordering should be reasonably fast (under 50ms)
        self.assertLess(end_time - start_time, 0.05, "Ordering products took too long")
    
    def test_bulk_create_performance(self):
        """Test the performance of bulk product creation."""
        # Prepare data for bulk creation
        bulk_count = 50
        bulk_data = [
            Product(
                sku=f"BULK-SKU-{i:04d}",
                customer=self.customers[i % len(self.customers)],
                labeling_unit_1="PALLET",
                labeling_quantity_1=i
            ) for i in range(bulk_count)
        ]
        
        # Measure time for bulk creation
        start_time = time.time()
        Product.objects.bulk_create(bulk_data)
        end_time = time.time()
        bulk_time = end_time - start_time
        
        # Verify the products were created
        self.assertEqual(
            Product.objects.filter(sku__startswith="BULK-SKU").count(),
            bulk_count
        )
        
        # Bulk creation should be faster than individual creations
        # For 50 records, it should be under 100ms
        self.assertLess(bulk_time, 0.1, "Bulk product creation took too long")
        
        # For comparison, measure time for individual creations
        individual_creation_times = []
        for i in range(5):  # Just do 5 for comparison, not all 50
            start_time = time.time()
            Product.objects.create(
                sku=f"INDIV-SKU-{i:04d}",
                customer=self.customers[0],
                labeling_unit_1="EACH",
                labeling_quantity_1=i
            )
            end_time = time.time()
            individual_creation_times.append(end_time - start_time)
        
        avg_individual_time = sum(individual_creation_times) / len(individual_creation_times)
        # Total time for 50 individual creations would be approximately:
        estimated_total_individual_time = avg_individual_time * 50
        
        # Bulk creation should be significantly faster than individual creations
        self.assertLess(bulk_time, estimated_total_individual_time * 0.5, 
            "Bulk creation is not significantly faster than individual creations")
    
    def test_concurrent_access_performance(self):
        """Test the performance of concurrent product access."""
        product_ids = [p.id for p in self.products[:10]]  # Take 10 products to query
        
        def query_product(product_id):
            """Query a product by ID."""
            product = Product.objects.get(id=product_id)
            return product is not None
        
        # Measure time for concurrent access
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(query_product, product_ids))
        end_time = time.time()
        
        # All queries should have succeeded
        self.assertTrue(all(results))
        
        # Concurrent access should be reasonably performant
        # For 10 concurrent queries, it should be under 100ms
        self.assertLess(end_time - start_time, 0.1, "Concurrent product access took too long")
    
    def test_product_stats_query_performance(self):
        """Test the performance of product statistics queries."""
        # This tests the query used in the stats action of ProductViewSet
        from django.db.models import Count
        
        # Measure time to get product statistics
        start_time = time.time()
        queryset = Product.objects.all()
        total_products = queryset.count()
        products_by_customer = queryset.values(
            'customer__company_name'
        ).annotate(
            count=Count('id')
        ).order_by('customer__company_name')
        end_time = time.time()
        
        # Verify the statistics
        self.assertEqual(total_products, self.product_count + 10 + 50 + 5)  # All products we created
        self.assertEqual(len(products_by_customer), len(self.customers))
        
        # The statistics query should be reasonably fast (under 100ms)
        self.assertLess(end_time - start_time, 0.1, "Product statistics query took too long")