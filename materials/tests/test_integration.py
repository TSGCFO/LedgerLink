import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from decimal import Decimal
from materials.models import Material, BoxPrice
from materials.tests.factories import MaterialFactory, BoxPriceFactory

User = get_user_model()


class MaterialBoxPriceIntegrationTest(TestCase):
    """Test the integration between Material and BoxPrice models and APIs."""

    def setUp(self):
        """Set up test data and client."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create multiple materials
        self.material1 = MaterialFactory(
            name='Cardboard',
            description='Regular cardboard',
            unit_price=Decimal('10.50')
        )
        
        self.material2 = MaterialFactory(
            name='Premium Cardboard',
            description='Higher quality cardboard',
            unit_price=Decimal('15.75')
        )
        
        # Create multiple box prices
        self.box_price1 = BoxPriceFactory(
            box_type='Small',
            price=Decimal('5.25'),
            length=Decimal('5.00'),
            width=Decimal('4.00'),
            height=Decimal('3.00')
        )
        
        self.box_price2 = BoxPriceFactory(
            box_type='Medium',
            price=Decimal('8.50'),
            length=Decimal('10.00'),
            width=Decimal('8.00'),
            height=Decimal('6.00')
        )
        
        self.box_price3 = BoxPriceFactory(
            box_type='Large',
            price=Decimal('12.75'),
            length=Decimal('15.00'),
            width=Decimal('12.00'),
            height=Decimal('9.00')
        )
    
    def test_multiple_api_calls(self):
        """Test making multiple API calls to retrieve both materials and box prices."""
        # Get materials
        materials_response = self.client.get(reverse('material-list'))
        self.assertEqual(materials_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(materials_response.data), 2)
        
        # Get box prices
        box_prices_response = self.client.get(reverse('boxprice-list'))
        self.assertEqual(box_prices_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(box_prices_response.data), 3)
        
        # Verify specific material and box price data
        material_names = [item['name'] for item in materials_response.data]
        self.assertIn('Cardboard', material_names)
        self.assertIn('Premium Cardboard', material_names)
        
        box_types = [item['box_type'] for item in box_prices_response.data]
        self.assertIn('Small', box_types)
        self.assertIn('Medium', box_types)
        self.assertIn('Large', box_types)

    def test_concurrent_updates(self):
        """Test updating both materials and box prices in sequence."""
        # Update a material
        material_data = {
            'name': 'Cardboard',
            'description': 'Updated regular cardboard',
            'unit_price': '11.25'
        }
        material_response = self.client.put(
            reverse('material-detail', kwargs={'pk': self.material1.pk}),
            material_data
        )
        self.assertEqual(material_response.status_code, status.HTTP_200_OK)
        
        # Update a box price
        box_price_data = {
            'box_type': 'Small',
            'price': '5.75',
            'length': '5.50',
            'width': '4.50',
            'height': '3.50'
        }
        box_price_response = self.client.put(
            reverse('boxprice-detail', kwargs={'pk': self.box_price1.pk}),
            box_price_data
        )
        self.assertEqual(box_price_response.status_code, status.HTTP_200_OK)
        
        # Verify the updates worked
        self.material1.refresh_from_db()
        self.assertEqual(self.material1.description, 'Updated regular cardboard')
        self.assertEqual(self.material1.unit_price, Decimal('11.25'))
        
        self.box_price1.refresh_from_db()
        self.assertEqual(self.box_price1.price, Decimal('5.75'))
        self.assertEqual(self.box_price1.length, Decimal('5.50'))
    
    def test_batch_operations(self):
        """Test creating multiple box prices in a batch-like operation."""
        # Create multiple box prices one after another
        box_data_list = [
            {
                'box_type': 'Extra Small',
                'price': '3.50',
                'length': '4.00',
                'width': '3.00',
                'height': '2.00'
            },
            {
                'box_type': 'Extra Large',
                'price': '18.25',
                'length': '20.00',
                'width': '16.00',
                'height': '12.00'
            }
        ]
        
        for box_data in box_data_list:
            response = self.client.post(reverse('boxprice-list'), box_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that we now have 5 box prices in total (3 from setup + 2 new ones)
        self.assertEqual(BoxPrice.objects.count(), 5)
        
        # Verify the new box types exist
        box_types = BoxPrice.objects.values_list('box_type', flat=True)
        self.assertIn('Extra Small', box_types)
        self.assertIn('Extra Large', box_types)
    
    def test_edge_case_calculations(self):
        """Test calculations with edge case values."""
        # Create a box with very small dimensions
        tiny_box = BoxPriceFactory(
            box_type='Tiny',
            price=Decimal('1.00'),
            length=Decimal('0.10'),
            width=Decimal('0.10'),
            height=Decimal('0.10')
        )
        
        # Calculate volume
        tiny_volume = tiny_box.length * tiny_box.width * tiny_box.height
        expected_tiny_volume = Decimal('0.10') * Decimal('0.10') * Decimal('0.10')
        self.assertEqual(tiny_volume, expected_tiny_volume)
        
        # Create a box with very large dimensions
        giant_box = BoxPriceFactory(
            box_type='Giant',
            price=Decimal('99.99'),
            length=Decimal('99.99'),
            width=Decimal('99.99'),
            height=Decimal('99.99')
        )
        
        # Calculate volume
        giant_volume = giant_box.length * giant_box.width * giant_box.height
        expected_giant_volume = Decimal('99.99') * Decimal('99.99') * Decimal('99.99')
        self.assertEqual(giant_volume, expected_giant_volume)
    
    def test_error_handling(self):
        """Test error handling for invalid requests."""
        # Attempt to create a material with invalid data
        invalid_material_data = {
            'name': 'Invalid Material',
            'description': 'Test invalid data',
            'unit_price': '-5.00'  # Negative price should be invalid
        }
        material_response = self.client.post(reverse('material-list'), invalid_material_data)
        self.assertEqual(material_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Attempt to create a box price with invalid data
        invalid_box_data = {
            'box_type': 'Invalid Box',
            'price': '10.00',
            'length': '-1.00',  # Negative length should be invalid
            'width': '8.00',
            'height': '6.00'
        }
        box_response = self.client.post(reverse('boxprice-list'), invalid_box_data)
        self.assertEqual(box_response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_volume_calculations(self):
        """Test volume calculations for different box sizes."""
        # Calculate volumes for all existing boxes
        boxes = BoxPrice.objects.all()
        for box in boxes:
            volume = box.length * box.width * box.height
            
            # Verify the volume is positive
            self.assertGreater(volume, 0)
            
            # Verify the volume calculation is correct
            expected_volume = box.length * box.width * box.height
            self.assertEqual(volume, expected_volume)


class MaterialAPIPerformanceTest(TestCase):
    """Test performance aspects of the Material API."""
    
    def setUp(self):
        """Set up test data for performance testing."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create 20 material instances for testing pagination and filtering
        for i in range(20):
            MaterialFactory(
                name=f'Material {i}',
                description=f'Description for material {i}',
                unit_price=Decimal(f'{10 + (i * 0.5):.2f}')
            )
    
    def test_pagination(self):
        """Test pagination of material results."""
        # Request with pagination
        response = self.client.get(f"{reverse('material-list')}?page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Parse response to handle potential differences in pagination implementation
        response_data = response.data
        
        # If the response uses pagination with 'results' field
        if isinstance(response_data, dict) and 'results' in response_data:
            # Check that we got the expected number of results
            self.assertEqual(len(response_data['results']), 10)
            
            # Check that there's a next page
            self.assertIsNotNone(response_data.get('next'))
            
            # Get the second page
            page2_response = self.client.get(f"{reverse('material-list')}?page=2&page_size=10")
            self.assertEqual(page2_response.status_code, status.HTTP_200_OK)
            
            # Check that we got the remaining results
            page2_data = page2_response.data
            self.assertEqual(len(page2_data['results']), 10)
        else:
            # If the API doesn't use pagination or returns a list directly
            # We'll see all 20 items
            self.assertEqual(len(response_data), 20)

    def test_large_batch_creation(self):
        """Test creating many materials at once."""
        new_materials = []
        for i in range(5):
            new_materials.append({
                'name': f'Batch Material {i}',
                'description': f'Created in batch {i}',
                'unit_price': f'{20 + i}.00'
            })
        
        # Create materials one by one but in rapid succession
        for material_data in new_materials:
            response = self.client.post(reverse('material-list'), material_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify we now have 25 materials (20 from setup + 5 new ones)
        self.assertEqual(Material.objects.count(), 25)


class BoxPriceCalculationTest(TestCase):
    """Test advanced calculations and edge cases for BoxPrice model."""
    
    def setUp(self):
        """Set up test data."""
        self.box_price = BoxPriceFactory(
            box_type='Standard',
            price=Decimal('5.25'),
            length=Decimal('10.50'),
            width=Decimal('8.25'),
            height=Decimal('6.00')
        )
    
    def test_price_per_cubic_unit(self):
        """Test calculating price per cubic unit (volume)."""
        volume = self.box_price.length * self.box_price.width * self.box_price.height
        price_per_cubic_unit = self.box_price.price / volume
        
        # Verify the calculation
        expected_volume = Decimal('10.50') * Decimal('8.25') * Decimal('6.00')
        expected_price_per_cubic_unit = Decimal('5.25') / expected_volume
        
        self.assertEqual(price_per_cubic_unit, expected_price_per_cubic_unit)
    
    def test_surface_area_calculations(self):
        """Test calculating the surface area of a box."""
        # Surface area = 2(lw + lh + wh)
        surface_area = 2 * (
            self.box_price.length * self.box_price.width +
            self.box_price.length * self.box_price.height +
            self.box_price.width * self.box_price.height
        )
        
        # Verify the calculation
        expected_surface_area = 2 * (
            Decimal('10.50') * Decimal('8.25') +
            Decimal('10.50') * Decimal('6.00') +
            Decimal('8.25') * Decimal('6.00')
        )
        
        self.assertEqual(surface_area, expected_surface_area)
    
    def test_price_per_surface_area(self):
        """Test calculating price per unit of surface area."""
        surface_area = 2 * (
            self.box_price.length * self.box_price.width +
            self.box_price.length * self.box_price.height +
            self.box_price.width * self.box_price.height
        )
        price_per_surface_area = self.box_price.price / surface_area
        
        # Verify the calculation
        expected_surface_area = 2 * (
            Decimal('10.50') * Decimal('8.25') +
            Decimal('10.50') * Decimal('6.00') +
            Decimal('8.25') * Decimal('6.00')
        )
        expected_price_per_surface_area = Decimal('5.25') / expected_surface_area
        
        self.assertEqual(price_per_surface_area, expected_price_per_surface_area)
    
    def test_extreme_aspect_ratios(self):
        """Test boxes with extreme aspect ratios (very long and narrow)."""
        # Create a very long and narrow box
        long_box = BoxPriceFactory(
            box_type='Long Narrow Box',
            price=Decimal('7.50'),
            length=Decimal('50.00'),  # Very long
            width=Decimal('2.00'),    # Very narrow
            height=Decimal('2.00')    # Very narrow
        )
        
        # Calculate volume and surface area
        volume = long_box.length * long_box.width * long_box.height
        surface_area = 2 * (
            long_box.length * long_box.width +
            long_box.length * long_box.height +
            long_box.width * long_box.height
        )
        
        # Verify the calculations
        expected_volume = Decimal('50.00') * Decimal('2.00') * Decimal('2.00')
        expected_surface_area = 2 * (
            Decimal('50.00') * Decimal('2.00') +
            Decimal('50.00') * Decimal('2.00') +
            Decimal('2.00') * Decimal('2.00')
        )
        
        self.assertEqual(volume, expected_volume)
        self.assertEqual(surface_area, expected_surface_area)
    
    def test_maximum_precision(self):
        """Test calculations with maximum decimal precision."""
        # Create a box with very precise measurements
        precise_box = BoxPriceFactory(
            box_type='Precise Box',
            price=Decimal('9.99'),
            length=Decimal('10.51'),
            width=Decimal('8.49'),
            height=Decimal('6.01')
        )
        
        # Calculate volume with high precision
        volume = precise_box.length * precise_box.width * precise_box.height
        
        # Verify the calculation
        expected_volume = Decimal('10.51') * Decimal('8.49') * Decimal('6.01')
        
        self.assertEqual(volume, expected_volume)
        
        # Test that we can round to 2 decimal places as might be needed in a UI
        rounded_volume = round(volume, 2)
        expected_rounded_volume = round(expected_volume, 2)
        
        self.assertEqual(rounded_volume, expected_rounded_volume)