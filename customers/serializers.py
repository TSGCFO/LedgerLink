from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    """
    Simplified customer serializer for essential CRUD operations.
    """
    class Meta:
        model = Customer
        fields = [
            'id', 'company_name', 'legal_business_name', 'email', 'phone',
            'address', 'city', 'state', 'zip', 'country',
            'business_type', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']