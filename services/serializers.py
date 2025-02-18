from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model providing CRUD operations.
    """
    class Meta:
        model = Service
        fields = [
            'id', 'service_name', 'description', 
            'charge_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_service_name(self, value):
        """
        Validate that the service name is unique.
        """
        if self.instance is None:  # Creating new service
            if Service.objects.filter(service_name__iexact=value).exists():
                raise serializers.ValidationError(
                    "A service with this name already exists."
                )
        else:  # Updating existing service
            if Service.objects.filter(
                service_name__iexact=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "A service with this name already exists."
                )
        return value