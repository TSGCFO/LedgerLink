from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Service
from .serializers import ServiceSerializer
from customer_services.models import CustomerService
from customers.models import Customer


class ServiceModelTest(TestCase):
    """
    Test cases for the Service model.
    """
    def setUp(self):
        self.service = Service.objects.create(
            service_name="Test Service",
            description="This is a test service",
            charge_type="quantity"
        )
    
    def test_service_creation(self):
        """Test that service is created correctly."""
        self.assertEqual(self.service.service_name, "Test Service")
        self.assertEqual(self.service.description, "This is a test service")
        self.assertEqual(self.service.charge_type, "quantity")
    
    def test_string_representation(self):
        """Test string representation of Service."""
        self.assertEqual(str(self.service), "Test Service")
    
    def test_service_unique_name(self):
        """Test that service name must be unique."""
        with self.assertRaises(Exception):
            Service.objects.create(
                service_name="Test Service",
                description="This is another test service",
                charge_type="single"
            )
    
    def test_service_charge_types(self):
        """Test service charge type choices."""
        for charge_type, _ in Service.CHARGE_TYPES:
            service = Service.objects.create(
                service_name=f"Test Service {charge_type}",
                description=f"Test service with {charge_type} charge type",
                charge_type=charge_type
            )
            self.assertEqual(service.charge_type, charge_type)


class ServiceSerializerTest(TestCase):
    """
    Test cases for the ServiceSerializer.
    """
    def setUp(self):
        self.service_attributes = {
            'service_name': 'Test Service',
            'description': 'This is a test service',
            'charge_type': 'quantity'
        }
        
        self.service = Service.objects.create(**self.service_attributes)
        self.serializer = ServiceSerializer(instance=self.service)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {'id', 'service_name', 'description', 'charge_type', 'created_at', 'updated_at'}
        )
    
    def test_service_name_validation(self):
        """Test that serializer validates service name uniqueness."""
        duplicate_service = {
            'service_name': 'Test Service',
            'description': 'Another test service',
            'charge_type': 'single'
        }
        serializer = ServiceSerializer(data=duplicate_service)
        self.assertFalse(serializer.is_valid())
        self.assertIn('service_name', serializer.errors)
    
    def test_service_name_case_insensitive_validation(self):
        """Test that service name validation is case-insensitive."""
        duplicate_service = {
            'service_name': 'TEST SERVICE',  # Different case
            'description': 'Another test service',
            'charge_type': 'single'
        }
        serializer = ServiceSerializer(data=duplicate_service)
        self.assertFalse(serializer.is_valid())
        self.assertIn('service_name', serializer.errors)
    
    def test_update_validation(self):
        """Test validation during update operation."""
        # Create another service to test duplicate validation
        Service.objects.create(
            service_name="Another Service",
            description="Another test service",
            charge_type="single"
        )
        
        # Try to update with a name that already exists
        serializer = ServiceSerializer(
            instance=self.service,
            data={'service_name': 'Another Service'}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('service_name', serializer.errors)
        
        # Update with a new unique name should work
        serializer = ServiceSerializer(
            instance=self.service,
            data={'service_name': 'Updated Service Name'}
        )
        self.assertTrue(serializer.is_valid())


class ServiceAPITest(APITestCase):
    """
    Test cases for the Service API endpoints.
    """
    def setUp(self):
        self.client = APIClient()
        
        # Create test services
        self.service1 = Service.objects.create(
            service_name="Standard Shipping",
            description="Standard shipping service",
            charge_type="quantity"
        )
        
        self.service2 = Service.objects.create(
            service_name="Express Shipping",
            description="Express shipping service",
            charge_type="single"
        )
        
        self.service3 = Service.objects.create(
            service_name="Gift Wrapping",
            description="Gift wrapping service",
            charge_type="single"
        )
        
        # Create a customer for testing service relationships
        self.customer = Customer.objects.create(
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
        
        # Create a customer service assignment
        self.customer_service = CustomerService.objects.create(
            customer=self.customer,
            service=self.service1,
            unit_price=10.00
        )
    
    def test_list_services(self):
        """Test listing all services."""
        url = reverse('service-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)
    
    def test_search_services(self):
        """Test searching services."""
        url = reverse('service-list')
        response = self.client.get(f"{url}?search=express")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['service_name'], 'Express Shipping')
    
    def test_filter_by_charge_type(self):
        """Test filtering services by charge type."""
        url = reverse('service-list')
        response = self.client.get(f"{url}?charge_type=single")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)
        
        # Verify both services have the requested charge type
        charge_types = [service['charge_type'] for service in response.data['data']]
        self.assertTrue(all(charge_type == 'single' for charge_type in charge_types))
    
    def test_retrieve_service(self):
        """Test retrieving a specific service."""
        url = reverse('service-detail', args=[self.service1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.service1.id)
        self.assertEqual(response.data['service_name'], 'Standard Shipping')
        self.assertEqual(response.data['charge_type'], 'quantity')
    
    def test_create_service(self):
        """Test creating a new service."""
        url = reverse('service-list')
        data = {
            'service_name': 'New Service',
            'description': 'A brand new service',
            'charge_type': 'quantity'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['service_name'], 'New Service')
        self.assertEqual(response.data['data']['description'], 'A brand new service')
        self.assertEqual(response.data['data']['charge_type'], 'quantity')
        
        # Verify it was actually created in the database
        self.assertTrue(
            Service.objects.filter(service_name='New Service').exists()
        )
    
    def test_create_duplicate_service(self):
        """Test creating a service with a duplicate name."""
        url = reverse('service-list')
        data = {
            'service_name': 'Standard Shipping',  # Already exists
            'description': 'Another shipping service',
            'charge_type': 'quantity'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('service_name', response.data)
    
    def test_update_service(self):
        """Test updating an existing service."""
        url = reverse('service-detail', args=[self.service2.id])
        data = {
            'service_name': 'Premium Express Shipping',
            'description': 'Updated description',
            'charge_type': 'quantity'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['service_name'], 'Premium Express Shipping')
        self.assertEqual(response.data['data']['description'], 'Updated description')
        self.assertEqual(response.data['data']['charge_type'], 'quantity')
        
        # Verify it was actually updated in the database
        self.service2.refresh_from_db()
        self.assertEqual(self.service2.service_name, 'Premium Express Shipping')
        self.assertEqual(self.service2.description, 'Updated description')
        self.assertEqual(self.service2.charge_type, 'quantity')
    
    def test_delete_service(self):
        """Test deleting a service with no dependencies."""
        url = reverse('service-detail', args=[self.service3.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify it was actually deleted from the database
        self.assertFalse(
            Service.objects.filter(id=self.service3.id).exists()
        )
    
    def test_delete_service_with_dependencies(self):
        """Test deleting a service that has customer service assignments."""
        url = reverse('service-detail', args=[self.service1.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Cannot delete service as it is assigned to customers', response.data['message'])
        
        # Verify it was not deleted from the database
        self.assertTrue(
            Service.objects.filter(id=self.service1.id).exists()
        )
    
    def test_get_charge_types(self):
        """Test getting the list of available charge types."""
        url = reverse('service-charge-types')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify all charge types are in the response
        charge_types = [item['value'] for item in response.data['data']]
        expected_types = [choice[0] for choice in Service.CHARGE_TYPES]
        self.assertEqual(set(charge_types), set(expected_types))
        
        # Verify format of response
        for item in response.data['data']:
            self.assertIn('value', item)
            self.assertIn('label', item)