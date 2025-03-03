from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from .models import CustomerService
from .serializers import CustomerServiceSerializer
from customers.models import Customer
from services.models import Service
from products.models import Product


class CustomerServiceModelTest(TestCase):
    """
    Test cases for the CustomerService model.
    """
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Company LLC",
            email="test@example.com",
            phone="555-1234",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="US"
        )
        
        cls.service = Service.objects.create(
            service_name="Test Service",
            description="Service for testing",
            base_rate=Decimal('100.00'),
            charge_type="percentage"
        )
        
        cls.customer_service = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('75.00')
        )
        
        # Create some products
        cls.product1 = Product.objects.create(
            sku="TEST-SKU-001",
            customer=cls.customer,
            labeling_unit_1="Box",
            labeling_quantity_1=10
        )
        cls.product2 = Product.objects.create(
            sku="TEST-SKU-002",
            customer=cls.customer,
            labeling_unit_1="Case",
            labeling_quantity_1=20
        )
        
        # Add products to customer service
        cls.customer_service.skus.add(cls.product1, cls.product2)
    
    def test_customer_service_creation(self):
        """Test that customer service is created correctly."""
        self.assertEqual(self.customer_service.customer.company_name, "Test Company")
        self.assertEqual(self.customer_service.service.service_name, "Test Service")
        self.assertEqual(self.customer_service.unit_price, Decimal('75.00'))
    
    def test_string_representation(self):
        """Test string representation of CustomerService."""
        expected = f"{self.customer} - {self.service}"
        self.assertEqual(str(self.customer_service), expected)
    
    def test_get_skus(self):
        """Test get_skus returns all related products."""
        skus = self.customer_service.get_skus()
        self.assertEqual(skus.count(), 2)
        self.assertIn(self.product1, skus)
        self.assertIn(self.product2, skus)
    
    def test_get_sku_list(self):
        """Test get_sku_list returns list of SKU codes."""
        sku_list = self.customer_service.get_sku_list()
        self.assertEqual(len(sku_list), 2)
        self.assertIn("TEST-SKU-001", sku_list)
        self.assertIn("TEST-SKU-002", sku_list)
    
    def test_unique_together_constraint(self):
        """Test that unique_together constraint is enforced."""
        # Attempt to create duplicate customer service
        with self.assertRaises(Exception):
            CustomerService.objects.create(
                customer=self.customer,
                service=self.service,
                unit_price=Decimal('80.00')
            )


class CustomerServiceSerializerTest(TestCase):
    """
    Test cases for the CustomerServiceSerializer.
    """
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.customer = Customer.objects.create(
            company_name="Test Company",
            legal_business_name="Test Company LLC",
            email="test@example.com",
            phone="555-1234",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="US"
        )
        
        cls.service = Service.objects.create(
            service_name="Test Service",
            description="Service for testing",
            base_rate=Decimal('100.00'),
            charge_type="percentage"
        )
        
        cls.customer_service = CustomerService.objects.create(
            customer=cls.customer,
            service=cls.service,
            unit_price=Decimal('75.00')
        )
        
        # Create some products
        cls.product1 = Product.objects.create(
            sku="TEST-SKU-001",
            customer=cls.customer,
            labeling_unit_1="Box",
            labeling_quantity_1=10
        )
        
        # Add product to customer service
        cls.customer_service.skus.add(cls.product1)
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        serializer = CustomerServiceSerializer(instance=self.customer_service)
        data = serializer.data
        
        expected_fields = [
            'id', 'customer', 'customer_details',
            'service', 'service_details', 'unit_price',
            'sku_list', 'created_at', 'updated_at'
        ]
        
        self.assertEqual(set(data.keys()), set(expected_fields))
    
    def test_serializer_validates_unique_customer_service(self):
        """Test that serializer validates uniqueness of customer-service combination."""
        # Create data for duplicate customer service
        data = {
            'customer': self.customer.id,
            'service': self.service.id,
            'unit_price': '80.00'
        }
        
        serializer = CustomerServiceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('This service is already assigned to this customer', str(serializer.errors))


class CustomerServiceAPITest(APITestCase):
    """
    Test cases for the CustomerService API endpoints.
    """
    @classmethod
    def setUpTestData(cls):
        # Create test data
        cls.customer1 = Customer.objects.create(
            company_name="Test Company 1",
            legal_business_name="Test Company 1 LLC",
            email="test1@example.com",
            phone="555-1234",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            country="US"
        )
        
        cls.customer2 = Customer.objects.create(
            company_name="Test Company 2",
            legal_business_name="Test Company 2 LLC",
            email="test2@example.com",
            phone="555-5678",
            address="456 Test Ave",
            city="Test City",
            state="TS",
            zip_code="67890",
            country="US"
        )
        
        cls.service1 = Service.objects.create(
            service_name="Standard Shipping",
            description="Standard shipping service",
            base_rate=Decimal('50.00'),
            charge_type="flat_rate"
        )
        
        cls.service2 = Service.objects.create(
            service_name="Express Shipping",
            description="Express shipping service",
            base_rate=Decimal('100.00'),
            charge_type="flat_rate"
        )
        
        cls.customer_service1 = CustomerService.objects.create(
            customer=cls.customer1,
            service=cls.service1,
            unit_price=Decimal('45.00')
        )
        
        cls.customer_service2 = CustomerService.objects.create(
            customer=cls.customer2,
            service=cls.service1,
            unit_price=Decimal('48.00')
        )
        
        cls.customer_service3 = CustomerService.objects.create(
            customer=cls.customer1,
            service=cls.service2,
            unit_price=Decimal('95.00')
        )
        
        # Create products
        cls.product1 = Product.objects.create(
            sku="TEST-SKU-001",
            customer=cls.customer1,
            labeling_unit_1="Box",
            labeling_quantity_1=10
        )
        
        cls.product2 = Product.objects.create(
            sku="TEST-SKU-002",
            customer=cls.customer1,
            labeling_unit_1="Case",
            labeling_quantity_1=20
        )
        
        # Add products to customer service
        cls.customer_service1.skus.add(cls.product1, cls.product2)
    
    def setUp(self):
        self.client = APIClient()
        # Setup authentication if needed
        # self.client.force_authenticate(user=self.user)
    
    def test_list_customer_services(self):
        """Test listing all customer services."""
        url = reverse('customerservice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)
    
    def test_filter_by_customer(self):
        """Test filtering customer services by customer."""
        url = reverse('customerservice-list')
        response = self.client.get(f"{url}?customer={self.customer1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)
        
        for cs in response.data['data']:
            self.assertEqual(cs['customer'], self.customer1.id)
    
    def test_filter_by_service(self):
        """Test filtering customer services by service."""
        url = reverse('customerservice-list')
        response = self.client.get(f"{url}?service={self.service1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)
        
        for cs in response.data['data']:
            self.assertEqual(cs['service'], self.service1.id)
    
    def test_search_customer_services(self):
        """Test searching customer services."""
        url = reverse('customerservice-list')
        response = self.client.get(f"{url}?search=Express")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['service'], self.service2.id)
    
    def test_retrieve_customer_service(self):
        """Test retrieving a specific customer service."""
        url = reverse('customerservice-detail', args=[self.customer_service1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.customer_service1.id)
        self.assertEqual(response.data['customer'], self.customer1.id)
        self.assertEqual(response.data['service'], self.service1.id)
        self.assertEqual(response.data['unit_price'], '45.00')
        self.assertEqual(len(response.data['sku_list']), 2)
    
    def test_create_customer_service(self):
        """Test creating a new customer service."""
        url = reverse('customerservice-list')
        data = {
            'customer': self.customer2.id,
            'service': self.service2.id,
            'unit_price': '90.00'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['customer'], self.customer2.id)
        self.assertEqual(response.data['data']['service'], self.service2.id)
        self.assertEqual(response.data['data']['unit_price'], '90.00')
        
        # Verify it was actually created in the database
        self.assertTrue(
            CustomerService.objects.filter(
                customer=self.customer2,
                service=self.service2
            ).exists()
        )
    
    def test_update_customer_service(self):
        """Test updating an existing customer service."""
        url = reverse('customerservice-detail', args=[self.customer_service1.id])
        data = {
            'customer': self.customer1.id,
            'service': self.service1.id,
            'unit_price': '55.00'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['unit_price'], '55.00')
        
        # Verify it was actually updated in the database
        self.customer_service1.refresh_from_db()
        self.assertEqual(self.customer_service1.unit_price, Decimal('55.00'))
    
    def test_delete_customer_service(self):
        """Test deleting a customer service."""
        url = reverse('customerservice-detail', args=[self.customer_service1.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify it was actually deleted from the database
        self.assertFalse(
            CustomerService.objects.filter(id=self.customer_service1.id).exists()
        )
    
    def test_add_skus(self):
        """Test adding SKUs to a customer service."""
        url = reverse('customerservice-add-skus', args=[self.customer_service3.id])
        data = {
            'sku_ids': ['TEST-SKU-001', 'TEST-SKU-002']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify SKUs were added
        sku_list = response.data['data']['sku_list']
        self.assertEqual(len(sku_list), 2)
        self.assertIn('TEST-SKU-001', sku_list)
        self.assertIn('TEST-SKU-002', sku_list)
    
    def test_remove_skus(self):
        """Test removing SKUs from a customer service."""
        # First, add SKUs
        self.customer_service3.skus.add(self.product1, self.product2)
        
        url = reverse('customerservice-remove-skus', args=[self.customer_service3.id])
        data = {
            'sku_ids': [self.product1.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify SKU was removed
        self.assertNotIn(self.product1.id, self.customer_service3.skus.values_list('id', flat=True))