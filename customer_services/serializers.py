from rest_framework import serializers
from .models import CustomerService
from customers.serializers import CustomerSerializer
from services.models import Service
from services.serializers import ServiceSerializer
from products.models import Product

class CustomerServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerService model with nested customer and service details.
    """
    customer_details = CustomerSerializer(source='customer', read_only=True)
    service_details = ServiceSerializer(source='service', read_only=True)
    sku_list = serializers.ListField(source='get_sku_list', read_only=True)
    class Meta:
        model = CustomerService
        fields = [
            'id', 'customer', 'customer_details',
            'service', 'service_details', 'unit_price',
            'sku_list', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'customer_details', 'service_details', 'sku_list']

    def validate(self, data):
        """
        Validate that the customer-service combination is unique.
        """
        customer = data.get('customer')
        service = data.get('service')
        
        # Check for uniqueness only on creation
        if self.instance is None and CustomerService.objects.filter(
            customer=customer, service=service
        ).exists():
            raise serializers.ValidationError(
                "This service is already assigned to this customer."
            )
        
        return data