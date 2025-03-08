# services/tests/test_views.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from services.models import Service
from .factories import ServiceFactory

pytestmark = pytest.mark.django_db

class TestServiceViewSet:
    """
    Test cases for the ServiceViewSet.
    """
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_list_services(self, api_client):
        """Test listing services."""
        # Create multiple services
        services = [ServiceFactory.create() for _ in range(3)]
        
        # Make API request
        url = reverse('service-list')
        response = api_client.get(url)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 3
        
        # Verify services are returned in correct order (by service_name)
        service_names = [s['service_name'] for s in response.data['data']]
        expected_names = sorted([s.service_name for s in services])
        assert service_names == expected_names
    
    def test_retrieve_service(self, api_client):
        """Test retrieving a single service."""
        service = ServiceFactory.create()
        
        url = reverse('service-detail', kwargs={'pk': service.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == service.pk
        assert response.data['service_name'] == service.service_name
        assert response.data['description'] == service.description
        assert response.data['charge_type'] == service.charge_type
    
    def test_create_service(self, api_client):
        """Test creating a service."""
        url = reverse('service-list')
        data = {
            'service_name': 'New API Service',
            'description': 'Created via API',
            'charge_type': 'single'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['message'] == 'Service created successfully'
        assert response.data['data']['service_name'] == data['service_name']
        
        # Verify service was actually created in db
        assert Service.objects.filter(service_name=data['service_name']).exists()
    
    def test_update_service(self, api_client):
        """Test updating a service."""
        service = ServiceFactory.create()
        
        url = reverse('service-detail', kwargs={'pk': service.pk})
        data = {
            'service_name': 'Updated API Service',
            'description': 'Updated via API',
            'charge_type': 'single' if service.charge_type == 'quantity' else 'quantity'
        }
        
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Service updated successfully'
        assert response.data['data']['service_name'] == data['service_name']
        
        # Verify service was actually updated in db
        service.refresh_from_db()
        assert service.service_name == data['service_name']
        assert service.description == data['description']
        assert service.charge_type == data['charge_type']
    
    def test_partial_update_service(self, api_client):
        """Test partially updating a service."""
        service = ServiceFactory.create()
        original_charge_type = service.charge_type
        
        url = reverse('service-detail', kwargs={'pk': service.pk})
        data = {
            'description': 'Partially updated via API'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Verify only specified field was updated
        service.refresh_from_db()
        assert service.description == data['description']
        assert service.charge_type == original_charge_type  # Unchanged
    
    def test_delete_service(self, api_client):
        """Test deleting a service."""
        service = ServiceFactory.create()
        
        url = reverse('service-detail', kwargs={'pk': service.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Service deleted successfully'
        
        # Verify service was actually deleted from db
        assert not Service.objects.filter(pk=service.pk).exists()
    
    def test_search_services(self, api_client):
        """Test searching services."""
        # Create services with different names
        ServiceFactory.create(service_name="First Service")
        ServiceFactory.create(service_name="Second Service")
        ServiceFactory.create(service_name="Different Name")
        
        # Search for 'Service'
        url = reverse('service-list')
        response = api_client.get(f"{url}?search=Service")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 3  # All match 'Service'
        
        # Search for 'First'
        response = api_client.get(f"{url}?search=First")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['service_name'] == "First Service"
    
    def test_filter_by_charge_type(self, api_client):
        """Test filtering services by charge_type."""
        # Create services with different charge types
        ServiceFactory.create(service_name="Service A", charge_type="single")
        ServiceFactory.create(service_name="Service B", charge_type="single")
        ServiceFactory.create(service_name="Service C", charge_type="quantity")
        
        # Filter for 'single' charge type
        url = reverse('service-list')
        response = api_client.get(f"{url}?charge_type=single")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2
        for service in response.data['data']:
            assert service['charge_type'] == 'single'
    
    def test_charge_types_action(self, api_client):
        """Test the charge_types action."""
        url = reverse('service-charge-types')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 2  # Should have two charge types
        
        # Verify charge types are returned
        charge_types = [item['value'] for item in response.data['data']]
        assert 'single' in charge_types
        assert 'quantity' in charge_types