from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from decimal import Decimal
from materials.models import Material, BoxPrice
from materials.tests.factories import MaterialFactory, BoxPriceFactory

User = get_user_model()


class MaterialViewSetTest(APITestCase):
    """Test suite for the MaterialViewSet."""

    def setUp(self):
        """Set up test data."""
        self.material = MaterialFactory(
            name='Cardboard',
            description='Standard cardboard material for packaging',
            unit_price=Decimal('10.50')
        )
        
        # Create a test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs
        self.list_url = reverse('material-list')
        self.detail_url = reverse('material-detail', kwargs={'pk': self.material.pk})

    def test_list_materials_authenticated(self):
        """Test that authenticated users can list materials."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Cardboard')

    def test_list_materials_unauthenticated(self):
        """Test that unauthenticated users cannot list materials."""
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_material(self):
        """Test retrieving a single material."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.material.id)
        self.assertEqual(response.data['name'], 'Cardboard')
        self.assertEqual(response.data['description'], 'Standard cardboard material for packaging')
        self.assertEqual(Decimal(response.data['unit_price']), Decimal('10.50'))

    def test_create_material(self):
        """Test creating a new material."""
        data = {
            'name': 'Plastic',
            'description': 'Plastic material for packaging',
            'unit_price': '15.75'
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Plastic')
        self.assertEqual(Material.objects.count(), 2)

    def test_update_material(self):
        """Test updating a material."""
        data = {
            'name': 'Cardboard',
            'description': 'Updated description',
            'unit_price': '12.25'
        }
        
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(Decimal(response.data['unit_price']), Decimal('12.25'))
        
        # Verify the database was updated
        self.material.refresh_from_db()
        self.assertEqual(self.material.description, 'Updated description')
        self.assertEqual(self.material.unit_price, Decimal('12.25'))

    def test_delete_material(self):
        """Test deleting a material."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Material.objects.count(), 0)


class BoxPriceViewSetTest(APITestCase):
    """Test suite for the BoxPriceViewSet."""

    def setUp(self):
        """Set up test data."""
        self.box_price = BoxPriceFactory(
            box_type='Standard',
            price=Decimal('5.25'),
            length=Decimal('10.50'),
            width=Decimal('8.25'),
            height=Decimal('6.00')
        )
        
        # Create a test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs
        self.list_url = reverse('boxprice-list')
        self.detail_url = reverse('boxprice-detail', kwargs={'pk': self.box_price.pk})

    def test_list_box_prices_authenticated(self):
        """Test that authenticated users can list box prices."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['box_type'], 'Standard')

    def test_list_box_prices_unauthenticated(self):
        """Test that unauthenticated users cannot list box prices."""
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_box_price(self):
        """Test retrieving a single box price."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.box_price.id)
        self.assertEqual(response.data['box_type'], 'Standard')
        self.assertEqual(Decimal(response.data['price']), Decimal('5.25'))
        self.assertEqual(Decimal(response.data['length']), Decimal('10.50'))
        self.assertEqual(Decimal(response.data['width']), Decimal('8.25'))
        self.assertEqual(Decimal(response.data['height']), Decimal('6.00'))

    def test_create_box_price(self):
        """Test creating a new box price."""
        data = {
            'box_type': 'Small',
            'price': '3.50',
            'length': '5.00',
            'width': '4.00',
            'height': '3.00'
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['box_type'], 'Small')
        self.assertEqual(BoxPrice.objects.count(), 2)

    def test_update_box_price(self):
        """Test updating a box price."""
        data = {
            'box_type': 'Standard',
            'price': '6.50',
            'length': '10.50',
            'width': '8.25',
            'height': '6.00'
        }
        
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['price']), Decimal('6.50'))
        
        # Verify the database was updated
        self.box_price.refresh_from_db()
        self.assertEqual(self.box_price.price, Decimal('6.50'))

    def test_delete_box_price(self):
        """Test deleting a box price."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BoxPrice.objects.count(), 0)