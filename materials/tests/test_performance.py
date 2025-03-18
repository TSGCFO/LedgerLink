import time
import random
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from materials.models import Material, BoxPrice
from materials.tests.factories import MaterialFactory, BoxPriceFactory

User = get_user_model()


class MaterialQueryPerformanceTest(TestCase):
    """Test database query performance for Material model."""
    
    def setUp(self):
        """Set up test data for performance testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a large number of materials for performance testing
        self.material_count = 50
        for i in range(self.material_count):
            MaterialFactory(
                name=f'Material {i}',
                description=f'Description for material {i}',
                unit_price=Decimal(f'{random.uniform(5.0, 100.0):.2f}')
            )
    
    def test_query_count_list(self):
        """Test the number of queries executed for listing materials."""
        url = reverse('material-list')
        
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), self.material_count)
        
        # Check query count - should be a small number regardless of material count
        query_count = len(queries)
        self.assertLessEqual(query_count, 5, 
                            f"Too many queries ({query_count}) for material list endpoint")
    
    def test_query_execution_time(self):
        """Test the execution time for retrieving a list of materials."""
        url = reverse('material-list')
        
        # Measure execution time
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Calculate execution time in milliseconds
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Execution time should be reasonable
        self.assertLess(execution_time, 500, 
                       f"API response too slow: {execution_time:.2f}ms")
    
    def test_query_by_name_performance(self):
        """Test performance of filtering by name."""
        # Pick a random material
        random_index = random.randint(0, self.material_count - 1)
        material_name = f'Material {random_index}'
        
        # Measure query time
        start_time = time.time()
        materials = Material.objects.filter(name=material_name)
        end_time = time.time()
        
        # Verify the query
        self.assertEqual(materials.count(), 1)
        
        # Calculate execution time in milliseconds
        execution_time = (end_time - start_time) * 1000
        
        # Should be very fast since we're querying by a field that should have an index
        self.assertLess(execution_time, 50, 
                       f"Name lookup too slow: {execution_time:.2f}ms")


class BoxPriceQueryPerformanceTest(TestCase):
    """Test database query performance for BoxPrice model."""
    
    def setUp(self):
        """Set up test data for performance testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a large number of box prices for performance testing
        self.box_count = 50
        for i in range(self.box_count):
            BoxPriceFactory(
                box_type=f'Box Type {i}',
                price=Decimal(f'{random.uniform(2.0, 50.0):.2f}'),
                length=Decimal(f'{random.uniform(5.0, 30.0):.2f}'),
                width=Decimal(f'{random.uniform(3.0, 25.0):.2f}'),
                height=Decimal(f'{random.uniform(2.0, 20.0):.2f}')
            )
    
    def test_bulk_create_performance(self):
        """Test performance of bulk creating box prices."""
        # Create box price data
        box_prices_to_create = 20
        start_time = time.time()
        
        BoxPrice.objects.bulk_create([
            BoxPrice(
                box_type=f'Bulk Box {i}',
                price=Decimal(f'{random.uniform(2.0, 50.0):.2f}'),
                length=Decimal(f'{random.uniform(5.0, 30.0):.2f}'),
                width=Decimal(f'{random.uniform(3.0, 25.0):.2f}'),
                height=Decimal(f'{random.uniform(2.0, 20.0):.2f}')
            ) for i in range(box_prices_to_create)
        ])
        
        end_time = time.time()
        
        # Verify the creation
        self.assertEqual(BoxPrice.objects.count(), self.box_count + box_prices_to_create)
        
        # Calculate execution time in milliseconds
        execution_time = (end_time - start_time) * 1000
        
        # Should be relatively fast for bulk creation
        self.assertLess(execution_time, 500, 
                       f"Bulk creation too slow: {execution_time:.2f}ms")
    
    def test_complex_filtering_performance(self):
        """Test performance of complex filtering."""
        # Filter by dimension range
        min_length = Decimal('10.0')
        max_length = Decimal('20.0')
        min_width = Decimal('5.0')
        max_width = Decimal('15.0')
        min_height = Decimal('4.0')
        max_height = Decimal('10.0')
        
        # Measure query time
        start_time = time.time()
        filtered_boxes = BoxPrice.objects.filter(
            length__gte=min_length,
            length__lte=max_length,
            width__gte=min_width,
            width__lte=max_width,
            height__gte=min_height,
            height__lte=max_height
        )
        end_time = time.time()
        
        # Calculate execution time in milliseconds
        execution_time = (end_time - start_time) * 1000
        
        # Complex filtering should still be reasonably fast
        self.assertLess(execution_time, 100, 
                       f"Complex filtering too slow: {execution_time:.2f}ms")


class APILoadTest(TestCase):
    """Test API endpoints under load."""
    
    def setUp(self):
        """Set up test data for load testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create materials
        for i in range(20):
            MaterialFactory()
        
        # Create box prices
        for i in range(20):
            BoxPriceFactory()
        
        # URLs
        self.material_url = reverse('material-list')
        self.boxprice_url = reverse('boxprice-list')
    
    def test_repeated_api_calls(self):
        """Test making multiple API calls in succession."""
        num_calls = 10
        total_time = 0
        
        # Make multiple calls to material endpoint
        for i in range(num_calls):
            start_time = time.time()
            response = self.client.get(self.material_url)
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            total_time += (end_time - start_time)
        
        # Calculate average response time
        avg_time = (total_time / num_calls) * 1000  # in milliseconds
        
        # Average should be fast
        self.assertLess(avg_time, 200, 
                       f"Average response time too slow: {avg_time:.2f}ms")
    
    def test_interleaved_api_calls(self):
        """Test interleaving calls to different endpoints."""
        num_iterations = 5
        total_time = 0
        
        # Alternate between material and box price endpoints
        for i in range(num_iterations):
            # Material endpoint
            start_time = time.time()
            response1 = self.client.get(self.material_url)
            self.assertEqual(response1.status_code, 200)
            
            # Box price endpoint
            response2 = self.client.get(self.boxprice_url)
            self.assertEqual(response2.status_code, 200)
            end_time = time.time()
            
            total_time += (end_time - start_time)
        
        # Calculate average time per iteration (two API calls)
        avg_time = (total_time / num_iterations) * 1000  # in milliseconds
        
        # Should be reasonably fast for both calls
        self.assertLess(avg_time, 400, 
                       f"Interleaved API calls too slow: {avg_time:.2f}ms")
    
    def test_concurrent_read_write_performance(self):
        """Test performance of mixing read and write operations."""
        # Start with a read operation
        start_time = time.time()
        
        # Get materials
        response1 = self.client.get(self.material_url)
        self.assertEqual(response1.status_code, 200)
        
        # Create a new material
        create_response = self.client.post(self.material_url, {
            'name': f'Load Test Material {int(time.time())}',  # Unique name
            'description': 'Created during load test',
            'unit_price': '25.99'
        })
        self.assertEqual(create_response.status_code, 201)
        
        # Get box prices
        response2 = self.client.get(self.boxprice_url)
        self.assertEqual(response2.status_code, 200)
        
        # Update the material we just created
        new_material_id = create_response.data['id']
        update_response = self.client.patch(
            f"{self.material_url}{new_material_id}/",
            {'description': 'Updated during load test'}
        )
        self.assertEqual(update_response.status_code, 200)
        
        # Get materials again to see the update
        response3 = self.client.get(self.material_url)
        self.assertEqual(response3.status_code, 200)
        
        end_time = time.time()
        
        # Calculate total execution time for the sequence
        execution_time = (end_time - start_time) * 1000  # in milliseconds
        
        # Should finish in a reasonable time
        self.assertLess(execution_time, 1000, 
                       f"Read-write sequence too slow: {execution_time:.2f}ms")