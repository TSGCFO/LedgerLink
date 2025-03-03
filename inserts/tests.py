from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timezone

from .models import Insert
from .serializers import InsertSerializer
from customers.models import Customer


class InsertModelTests(TestCase):
    """Test cases for the Insert model"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )

    def test_create_insert(self):
        """Test creating an Insert instance"""
        insert = Insert.objects.create(
            sku="TEST-SKU",
            insert_name="Test Insert",
            insert_quantity=100,
            customer=self.customer
        )
        self.assertEqual(insert.sku, "TEST-SKU")
        self.assertEqual(insert.insert_name, "Test Insert")
        self.assertEqual(insert.insert_quantity, 100)
        self.assertEqual(insert.customer, self.customer)
        self.assertIsNotNone(insert.created_at)
        self.assertIsNotNone(insert.updated_at)

    def test_insert_str_representation(self):
        """Test the string representation of an Insert"""
        insert = Insert.objects.create(
            sku="TEST-SKU",
            insert_name="Test Insert",
            insert_quantity=100,
            customer=self.customer
        )
        self.assertEqual(str(insert), "Test Insert (TEST-SKU)")
        
    def test_insert_auto_timestamps(self):
        """Test that created_at and updated_at are auto-set"""
        insert = Insert.objects.create(
            sku="TEST-SKU",
            insert_name="Test Insert",
            insert_quantity=100,
            customer=self.customer
        )
        
        # Both timestamps should be set and close to now
        self.assertIsNotNone(insert.created_at)
        self.assertIsNotNone(insert.updated_at)
        
        # Save the created_at timestamp
        original_created_at = insert.created_at
        original_updated_at = insert.updated_at
        
        # Update the insert and save
        insert.insert_quantity = 200
        insert.save()
        
        # created_at should not change
        self.assertEqual(insert.created_at, original_created_at)
        
        # updated_at should change
        self.assertNotEqual(insert.updated_at, original_updated_at)

    def test_customer_cascade_delete(self):
        """Test that deleting a customer deletes associated inserts"""
        Insert.objects.create(
            sku="TEST-SKU1",
            insert_name="Test Insert 1",
            insert_quantity=100,
            customer=self.customer
        )
        Insert.objects.create(
            sku="TEST-SKU2",
            insert_name="Test Insert 2",
            insert_quantity=200,
            customer=self.customer
        )
        
        # Verify two inserts exist
        self.assertEqual(Insert.objects.count(), 2)
        
        # Delete the customer
        self.customer.delete()
        
        # Verify inserts are deleted via cascade
        self.assertEqual(Insert.objects.count(), 0)


class InsertSerializerTests(TestCase):
    """Test cases for the InsertSerializer"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.insert_data = {
            'sku': 'TEST-SKU',
            'insert_name': 'Test Insert',
            'insert_quantity': 100,
            'customer': self.customer.id
        }

    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        serializer = InsertSerializer(data=self.insert_data)
        self.assertTrue(serializer.is_valid())
        
    def test_serializer_missing_required_field(self):
        """Test serializer with missing required field"""
        # Missing 'sku' field
        invalid_data = {
            'insert_name': 'Test Insert',
            'insert_quantity': 100,
            'customer': self.customer.id
        }
        serializer = InsertSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku', serializer.errors)
        
    def test_serializer_invalid_quantity(self):
        """Test validation of insert_quantity"""
        # Negative quantity
        invalid_data = dict(self.insert_data)
        invalid_data['insert_quantity'] = -10
        serializer = InsertSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('insert_quantity', serializer.errors)
        
        # Zero quantity
        invalid_data['insert_quantity'] = 0
        serializer = InsertSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('insert_quantity', serializer.errors)
        
    def test_serializer_sku_uppercase(self):
        """Test that SKU is converted to uppercase"""
        data = dict(self.insert_data)
        data['sku'] = 'test-sku-lowercase'
        serializer = InsertSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        insert = serializer.save()
        self.assertEqual(insert.sku, 'TEST-SKU-LOWERCASE')
        
    def test_serializer_sku_uniqueness_per_customer(self):
        """Test validation of SKU uniqueness per customer"""
        # Create first insert
        Insert.objects.create(
            sku="DUPLICATE-SKU",
            insert_name="First Insert",
            insert_quantity=100,
            customer=self.customer
        )
        
        # Try to create another insert with same SKU for same customer
        duplicate_data = {
            'sku': 'DUPLICATE-SKU',
            'insert_name': 'Second Insert',
            'insert_quantity': 200,
            'customer': self.customer.id
        }
        serializer = InsertSerializer(data=duplicate_data)
        
        # Should detect duplicate and be invalid
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku', serializer.errors)
        
        # Create another customer
        another_customer = Customer.objects.create(
            company_name="Another Company",
            contact_name="Jane Smith",
            contact_email="jane@example.com",
            contact_phone="987-654-3210"
        )
        
        # Same SKU but different customer should be valid
        valid_data = dict(duplicate_data)
        valid_data['customer'] = another_customer.id
        serializer = InsertSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        

class InsertAPITests(APITestCase):
    """Test cases for the Insert API endpoints"""

    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.insert = Insert.objects.create(
            sku="API-TEST-SKU",
            insert_name="API Test Insert",
            insert_quantity=100,
            customer=self.customer
        )
        
        self.insert_url = reverse('insert-list')
        self.insert_detail_url = reverse('insert-detail', kwargs={'pk': self.insert.pk})
        self.update_quantity_url = reverse('insert-update-quantity', kwargs={'pk': self.insert.pk})
        self.stats_url = reverse('insert-stats')

    def test_get_insert_list(self):
        """Test GET request to retrieve all inserts"""
        response = self.client.get(self.insert_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        
    def test_create_insert(self):
        """Test POST request to create a new insert"""
        data = {
            'sku': 'NEW-API-SKU',
            'insert_name': 'New API Insert',
            'insert_quantity': 200,
            'customer': self.customer.id
        }
        response = self.client.post(self.insert_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Insert.objects.count(), 2)
        
    def test_retrieve_insert_detail(self):
        """Test GET request to retrieve a specific insert"""
        response = self.client.get(self.insert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sku'], 'API-TEST-SKU')
        
    def test_update_insert(self):
        """Test PUT request to update an insert"""
        data = {
            'sku': 'UPDATED-SKU',
            'insert_name': 'Updated Insert',
            'insert_quantity': 150,
            'customer': self.customer.id
        }
        response = self.client.put(self.insert_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.sku, 'UPDATED-SKU')
        self.assertEqual(self.insert.insert_quantity, 150)
        
    def test_delete_insert(self):
        """Test DELETE request to delete an insert"""
        response = self.client.delete(self.insert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(Insert.objects.count(), 0)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to the API"""
        self.client.logout()
        response = self.client.get(self.insert_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_filter_by_customer(self):
        """Test filtering inserts by customer"""
        # Create another customer and insert
        another_customer = Customer.objects.create(
            company_name="Another Company",
            contact_name="Jane Smith",
            contact_email="jane@example.com",
            contact_phone="987-654-3210"
        )
        
        Insert.objects.create(
            sku="ANOTHER-SKU",
            insert_name="Another Insert",
            insert_quantity=300,
            customer=another_customer
        )
        
        # Filter by first customer
        response = self.client.get(f"{self.insert_url}?customer={self.customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'API-TEST-SKU')
        
        # Filter by second customer
        response = self.client.get(f"{self.insert_url}?customer={another_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'ANOTHER-SKU')
        
    def test_search_functionality(self):
        """Test search functionality"""
        # Create another insert for the test
        Insert.objects.create(
            sku="SEARCHABLE-SKU",
            insert_name="Searchable Insert",
            insert_quantity=300,
            customer=self.customer
        )
        
        # Search by SKU
        response = self.client.get(f"{self.insert_url}?search=SEARCHABLE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'SEARCHABLE-SKU')
        
        # Search by insert name
        response = self.client.get(f"{self.insert_url}?search=Test Insert")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'API-TEST-SKU')
        
    def test_quantity_filter(self):
        """Test filtering by quantity"""
        # Create inserts with different quantities
        Insert.objects.create(
            sku="LOW-QTY",
            insert_name="Low Quantity Insert",
            insert_quantity=50,
            customer=self.customer
        )
        
        Insert.objects.create(
            sku="HIGH-QTY",
            insert_name="High Quantity Insert",
            insert_quantity=500,
            customer=self.customer
        )
        
        # Filter with min_quantity
        response = self.client.get(f"{self.insert_url}?min_quantity=200")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'HIGH-QTY')
        
        # Filter with max_quantity
        response = self.client.get(f"{self.insert_url}?max_quantity=75")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'LOW-QTY')
        
        # Filter with both min and max
        response = self.client.get(f"{self.insert_url}?min_quantity=75&max_quantity=200")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['sku'], 'API-TEST-SKU')
        
    def test_update_quantity_action(self):
        """Test the update_quantity custom action"""
        # Test adding quantity
        data = {
            'quantity': 50,
            'operation': 'add'
        }
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.insert_quantity, 150)
        
        # Test subtracting quantity
        data = {
            'quantity': 25,
            'operation': 'subtract'
        }
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.insert.refresh_from_db()
        self.assertEqual(self.insert.insert_quantity, 125)
        
        # Test invalid operation
        data = {
            'quantity': 50,
            'operation': 'invalid'
        }
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Test insufficient quantity
        data = {
            'quantity': 1000,
            'operation': 'subtract'
        }
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Test invalid quantity
        data = {
            'quantity': -50,
            'operation': 'add'
        }
        response = self.client.post(self.update_quantity_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
    def test_stats_action(self):
        """Test the stats custom action"""
        # Create additional inserts to test stats
        Insert.objects.create(
            sku="STATS-TEST-1",
            insert_name="Stats Test 1",
            insert_quantity=200,
            customer=self.customer
        )
        
        Insert.objects.create(
            sku="STATS-TEST-2",
            insert_name="Stats Test 2",
            insert_quantity=300,
            customer=self.customer
        )
        
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should be 3 inserts total
        self.assertEqual(response.data['data']['total_inserts'], 3)
        
        # Total quantity should be 100 + 200 + 300 = 600
        self.assertEqual(response.data['data']['total_quantity'], 600)
