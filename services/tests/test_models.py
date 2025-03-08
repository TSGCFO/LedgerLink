# services/tests/test_models.py

import pytest
from django.db import IntegrityError
from services.models import Service
from .factories import ServiceFactory

pytestmark = pytest.mark.django_db

class TestServiceModel:
    """
    Test cases for the Service model.
    """
    
    def test_create_service(self):
        """Test creating a service."""
        service = ServiceFactory.create()
        assert service.pk is not None
        assert Service.objects.count() == 1
        assert Service.objects.first().service_name == service.service_name
    
    def test_service_str_method(self):
        """Test the string representation of a service."""
        service = ServiceFactory.create(service_name="Test Service")
        assert str(service) == "Test Service"
    
    def test_service_unique_name(self):
        """Test that service names must be unique."""
        ServiceFactory.create(service_name="Unique Service")
        
        # Attempting to create another service with the same name should fail
        with pytest.raises(IntegrityError):
            ServiceFactory.create(service_name="Unique Service")
    
    def test_service_charge_types(self):
        """Test service charge types."""
        service_single = ServiceFactory.create(charge_type="single")
        service_quantity = ServiceFactory.create(charge_type="quantity")
        
        assert service_single.charge_type == "single"
        assert service_quantity.charge_type == "quantity"
    
    def test_service_defaults(self):
        """Test service default values."""
        service = ServiceFactory.create(description=None)
        
        assert service.description is None
        assert service.charge_type == "quantity"  # Default value
        assert service.created_at is not None
        assert service.updated_at is not None