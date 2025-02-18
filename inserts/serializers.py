from rest_framework import serializers
from .models import Insert
from customers.serializers import CustomerSerializer

class InsertSerializer(serializers.ModelSerializer):
    """
    Serializer for Insert model providing CRUD operations.
    Includes nested customer details.
    """
    customer_details = CustomerSerializer(source='customer', read_only=True)

    class Meta:
        model = Insert
        fields = [
            'id', 'sku', 'insert_name', 'insert_quantity',
            'customer', 'customer_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_insert_quantity(self, value):
        """
        Validate that the insert quantity is positive.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "Insert quantity must be greater than zero."
            )
        return value

    def validate_sku(self, value):
        """
        Validate SKU format and uniqueness per customer.
        """
        if not value:
            raise serializers.ValidationError("SKU is required.")

        # Check uniqueness only on creation or when SKU changes
        customer = self.initial_data.get('customer')
        if customer:
            existing = Insert.objects.filter(
                customer=customer,
                sku__iexact=value
            )
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "This SKU is already in use for this customer."
                )
        
        return value.upper()