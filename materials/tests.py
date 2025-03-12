from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from decimal import Decimal

from .models import Material, BoxPrice
from .serializers import MaterialSerializer, BoxPriceSerializer


class MaterialModelTests(TestCase):
    """Test cases for the Material model"""

    def test_create_material(self):
        """Test creating a Material instance"""
        material = Material.objects.create(
            name="Test Material",
            description="Test description",
            unit_price=Decimal("10.50")
        )
        self.assertEqual(material.name, "Test Material")
        self.assertEqual(material.description, "Test description")
        self.assertEqual(material.unit_price, Decimal("10.50"))

    def test_material_str_representation(self):
        """Test the string representation of a Material"""
        material = Material.objects.create(
            name="Test Material",
            description="Test description",
            unit_price=Decimal("10.50")
        )
        self.assertEqual(str(material), "Test Material")

    def test_material_name_unique(self):
        """Test that material names must be unique"""
        Material.objects.create(
            name="Unique Material",
            description="Test description",
            unit_price=Decimal("10.50")
        )
        
        # Attempting to create another material with the same name should raise an error
        with self.assertRaises(Exception):  # Could be more specific with IntegrityError
            Material.objects.create(
                name="Unique Material",
                description="Another description",
                unit_price=Decimal("15.75")
            )


class BoxPriceModelTests(TestCase):
    """Test cases for the BoxPrice model"""

    def test_create_box_price(self):
        """Test creating a BoxPrice instance"""
        box_price = BoxPrice.objects.create(
            box_type="Small Box",
            price=Decimal("5.25"),
            length=Decimal("10.0"),
            width=Decimal("8.0"),
            height=Decimal("6.0")
        )
        self.assertEqual(box_price.box_type, "Small Box")
        self.assertEqual(box_price.price, Decimal("5.25"))
        self.assertEqual(box_price.length, Decimal("10.0"))
        self.assertEqual(box_price.width, Decimal("8.0"))
        self.assertEqual(box_price.height, Decimal("6.0"))

    def test_box_price_str_representation(self):
        """Test the string representation of a BoxPrice"""
        box_price = BoxPrice.objects.create(
            box_type="Medium Box",
            price=Decimal("7.50"),
            length=Decimal("12.0"),
            width=Decimal("10.0"),
            height=Decimal("8.0")
        )
        self.assertEqual(str(box_price), "Medium Box - 7.50")


class MaterialSerializerTests(TestCase):
    """Test cases for the MaterialSerializer"""

    def test_material_serializer_valid_data(self):
        """Test serializing a Material instance"""
        material_data = {
            'name': 'New Material',
            'description': 'New material description',
            'unit_price': '15.75'
        }
        serializer = MaterialSerializer(data=material_data)
        self.assertTrue(serializer.is_valid())
        
    def test_material_serializer_missing_required_field(self):
        """Test serializer with missing required field"""
        # Missing 'name' field which is required
        material_data = {
            'description': 'Missing name field',
            'unit_price': '15.75'
        }
        serializer = MaterialSerializer(data=material_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class BoxPriceSerializerTests(TestCase):
    """Test cases for the BoxPriceSerializer"""

    def test_box_price_serializer_valid_data(self):
        """Test serializing a BoxPrice instance"""
        box_price_data = {
            'box_type': 'Large Box',
            'price': '12.50',
            'length': '15.0',
            'width': '12.0',
            'height': '10.0'
        }
        serializer = BoxPriceSerializer(data=box_price_data)
        self.assertTrue(serializer.is_valid())
        
    def test_box_price_serializer_missing_required_field(self):
        """Test serializer with missing required field"""
        # Missing 'price' field which is required
        box_price_data = {
            'box_type': 'Large Box',
            'length': '15.0',
            'width': '12.0',
            'height': '10.0'
        }
        serializer = BoxPriceSerializer(data=box_price_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)


class MaterialAPITests(APITestCase):
    """Test cases for the Material API endpoints"""

    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.material = Material.objects.create(
            name="API Test Material",
            description="For API testing",
            unit_price=Decimal("20.00")
        )
        
        self.material_url = reverse('material-list')
        self.material_detail_url = reverse('material-detail', kwargs={'pk': self.material.pk})

    def test_get_material_list(self):
        """Test GET request to retrieve all materials"""
        response = self.client.get(self.material_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_create_material(self):
        """Test POST request to create a new material"""
        data = {
            'name': 'New API Material',
            'description': 'Created via API',
            'unit_price': '25.50'
        }
        response = self.client.post(self.material_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 2)
        
    def test_retrieve_material_detail(self):
        """Test GET request to retrieve a specific material"""
        response = self.client.get(self.material_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Test Material')
        
    def test_update_material(self):
        """Test PUT request to update a material"""
        data = {
            'name': 'Updated Material',
            'description': 'Updated description',
            'unit_price': '22.50'
        }
        response = self.client.put(self.material_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.material.refresh_from_db()
        self.assertEqual(self.material.name, 'Updated Material')
        
    def test_delete_material(self):
        """Test DELETE request to delete a material"""
        response = self.client.delete(self.material_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Material.objects.count(), 0)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to the API"""
        self.client.logout()
        response = self.client.get(self.material_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BoxPriceAPITests(APITestCase):
    """Test cases for the BoxPrice API endpoints"""

    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.box_price = BoxPrice.objects.create(
            box_type="API Test Box",
            price=Decimal("15.00"),
            length=Decimal("12.0"),
            width=Decimal("10.0"),
            height=Decimal("8.0")
        )
        
        self.box_price_url = reverse('boxprice-list')
        self.box_price_detail_url = reverse('boxprice-detail', kwargs={'pk': self.box_price.pk})

    def test_get_box_price_list(self):
        """Test GET request to retrieve all box prices"""
        response = self.client.get(self.box_price_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_create_box_price(self):
        """Test POST request to create a new box price"""
        data = {
            'box_type': 'New API Box',
            'price': '18.50',
            'length': '14.0',
            'width': '12.0',
            'height': '10.0'
        }
        response = self.client.post(self.box_price_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BoxPrice.objects.count(), 2)
        
    def test_retrieve_box_price_detail(self):
        """Test GET request to retrieve a specific box price"""
        response = self.client.get(self.box_price_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['box_type'], 'API Test Box')
        
    def test_update_box_price(self):
        """Test PUT request to update a box price"""
        data = {
            'box_type': 'Updated Box',
            'price': '16.50',
            'length': '13.0',
            'width': '11.0',
            'height': '9.0'
        }
        response = self.client.put(self.box_price_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.box_price.refresh_from_db()
        self.assertEqual(self.box_price.box_type, 'Updated Box')
        
    def test_delete_box_price(self):
        """Test DELETE request to delete a box price"""
        response = self.client.delete(self.box_price_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BoxPrice.objects.count(), 0)
