# services/tests/test_serializers.py

import pytest
from rest_framework.exceptions import ValidationError
from services.serializers import ServiceSerializer
from .factories import ServiceFactory

pytestmark = pytest.mark.django_db

class TestServiceSerializer:
    """
    Test cases for the ServiceSerializer.
    """
    
    def test_serialization(self):
        """Test serializing a service object."""
        service = ServiceFactory.create()
        serializer = ServiceSerializer(service)
        data = serializer.data
        
        assert data['id'] == service.id
        assert data['service_name'] == service.service_name
        assert data['description'] == service.description
        assert data['charge_type'] == service.charge_type
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_deserialization(self):
        """Test deserializing data to create a service."""
        service_data = {
            'service_name': 'New Test Service',
            'description': 'This is a test service description',
            'charge_type': 'single'
        }
        
        serializer = ServiceSerializer(data=service_data)
        assert serializer.is_valid()
        service = serializer.save()
        
        assert service.service_name == service_data['service_name']
        assert service.description == service_data['description']
        assert service.charge_type == service_data['charge_type']
    
    def test_validate_service_name_uniqueness(self):
        """Test validation of service_name uniqueness."""
        # Create a service first
        ServiceFactory.create(service_name="Existing Service")
        
        # Try to create another service with the same name
        serializer = ServiceSerializer(data={
            'service_name': 'Existing Service',
            'description': 'Duplicate service name',
            'charge_type': 'single'
        })
        
        assert not serializer.is_valid()
        assert 'service_name' in serializer.errors
    
    def test_validate_service_name_case_insensitive(self):
        """Test case-insensitive validation of service_name."""
        # Create a service first
        ServiceFactory.create(service_name="Case Service")
        
        # Try to create another service with the same name but different case
        serializer = ServiceSerializer(data={
            'service_name': 'CASE SERVICE',
            'description': 'Different case service name',
            'charge_type': 'single'
        })
        
        assert not serializer.is_valid()
        assert 'service_name' in serializer.errors
    
    def test_update_service(self):
        """Test updating a service."""
        service = ServiceFactory.create()
        
        updated_data = {
            'service_name': 'Updated Service Name',
            'description': 'Updated description',
            'charge_type': 'single' if service.charge_type == 'quantity' else 'quantity'
        }
        
        serializer = ServiceSerializer(service, data=updated_data, partial=True)
        assert serializer.is_valid()
        updated_service = serializer.save()
        
        assert updated_service.service_name == updated_data['service_name']
        assert updated_service.description == updated_data['description']
        assert updated_service.charge_type == updated_data['charge_type']
        
    def test_partial_update_service(self):
        """Test partial update of a service."""
        service = ServiceFactory.create()
        original_description = service.description
        
        updated_data = {
            'service_name': 'Partially Updated Service'
        }
        
        serializer = ServiceSerializer(service, data=updated_data, partial=True)
        assert serializer.is_valid()
        updated_service = serializer.save()
        
        assert updated_service.service_name == updated_data['service_name']
        assert updated_service.description == original_description  # Should not change