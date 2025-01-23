# products/serializers.py
from rest_framework import serializers
from .models import Product
from customers.serializers import CustomerSerializer

class ProductSerializer(serializers.ModelSerializer):
    customer_details = CustomerSerializer(source='customer', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'description', 'weight_lb', 'volume_cuft',
            'customer', 'customer_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_sku(self, value):
        """
        Validate that SKU is unique.
        """
        instance = self.instance
        if Product.objects.filter(sku=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError("This SKU is already in use.")
        return value

    def validate(self, data):
        """
        Validate weight and volume are non-negative if provided.
        """
        weight_lb = data.get('weight_lb')
        volume_cuft = data.get('volume_cuft')

        if weight_lb is not None and weight_lb < 0:
            raise serializers.ValidationError({
                'weight_lb': 'Weight must be non-negative.'
            })

        if volume_cuft is not None and volume_cuft < 0:
            raise serializers.ValidationError({
                'volume_cuft': 'Volume must be non-negative.'
            })

        return data
