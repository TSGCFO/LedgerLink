from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from inserts.models import Insert
from inserts.tests.factories import InsertFactory
from customers.tests.factories import CustomerFactory

User = get_user_model()


class InsertViewSetTest(APITestCase):
    """Test suite for the InsertViewSet."""

    def setUp(self):
        """Set up test data."""
        self.customer = CustomerFactory()
        self.insert = InsertFactory(
            sku='TEST-SKU-001',
            insert_name='Test Insert',
            insert_quantity=50,
            customer=self.customer
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
        self.list_url = reverse('insert-list')
        self.detail_url = reverse('insert-detail', kwargs={'pk': self.insert.pk})
        self.update_quantity_url = reverse('insert-update-quantity', kwargs={'pk': self.insert.pk})
        self.stats_url = reverse('insert-stats')

    def test_list_inserts(self):
        """Test retrieving a list of inserts."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'TEST-SKU-001')

    def test_retrieve_insert(self):
        """Test retrieving a single insert."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.insert.id)
        self.assertEqual(response.data['sku'], 'TEST-SKU-001')
        self.assertEqual(response.data['insert_name'], 'Test Insert')
        self.assertEqual(response.data['insert_quantity'], 50)

    def test_create_insert(self):
        """Test creating a new insert."""
        new_customer = CustomerFactory()
        data = {
            'sku': 'TEST-SKU-002',
            'insert_name': 'Test Insert 2',
            'insert_quantity': 25,
            'customer': new_customer.id
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['sku'], 'TEST-SKU-002')
        self.assertEqual(Insert.objects.count(), 2)

    def test_update_insert(self):
        """Test updating an insert."""
        data = {
            'sku': 'TEST-SKU-001',
            'insert_name': 'Updated Insert Name',
            'insert_quantity': 75,
            'customer': self.customer.id
        }
        
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['insert_name'], 'Updated Insert Name')
        self.assertEqual(response.data['data']['insert_quantity'], 75)
        
        # Verify the database was updated
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.insert_name, 'Updated Insert Name')
        self.assertEqual(self.insert.insert_quantity, 75)

    def test_delete_insert(self):
        """Test deleting an insert."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(Insert.objects.count(), 0)

    def test_update_quantity_add(self):
        """Test the update_quantity action with 'add' operation."""
        data = {
            'quantity': 25,
            'operation': 'add'
        }
        
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Verify the quantity was updated
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.insert_quantity, 75)  # 50 + 25

    def test_update_quantity_subtract(self):
        """Test the update_quantity action with 'subtract' operation."""
        data = {
            'quantity': 20,
            'operation': 'subtract'
        }
        
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # Verify the quantity was updated
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.insert_quantity, 30)  # 50 - 20

    def test_update_quantity_insufficient(self):
        """Test the update_quantity action with insufficient quantity."""
        data = {
            'quantity': 60,  # More than available
            'operation': 'subtract'
        }
        
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Insufficient quantity')
        
        # Verify the quantity was not updated
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.insert_quantity, 50)  # Unchanged

    def test_stats(self):
        """Test the stats action."""
        # Create another insert
        InsertFactory(
            sku='TEST-SKU-002',
            insert_name='Test Insert 2',
            insert_quantity=25,
            customer=self.customer
        )
        
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['total_inserts'], 2)
        self.assertEqual(response.data['data']['total_quantity'], 75)  # 50 + 25

    def test_filter_by_customer(self):
        """Test filtering inserts by customer."""
        # Create another customer and insert
        new_customer = CustomerFactory()
        InsertFactory(
            sku='TEST-SKU-003',
            insert_name='Test Insert 3',
            insert_quantity=30,
            customer=new_customer
        )
        
        # Filter by the original customer
        url = f"{self.list_url}?customer={self.customer.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'TEST-SKU-001')
        
        # Filter by the new customer
        url = f"{self.list_url}?customer={new_customer.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'TEST-SKU-003')