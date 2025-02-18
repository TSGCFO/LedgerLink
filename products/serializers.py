from rest_framework import serializers
from decimal import Decimal
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model providing CRUD operations.
    Includes calculated fields and validation.
    """
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'customer', 'customer_details',
            'labeling_unit_1', 'labeling_quantity_1',
            'labeling_unit_2', 'labeling_quantity_2',
            'labeling_unit_3', 'labeling_quantity_3',
            'labeling_unit_4', 'labeling_quantity_4',
            'labeling_unit_5', 'labeling_quantity_5',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_customer_details(self, obj):
        if obj.customer:
            return {
                'id': obj.customer.id,
                'company_name': obj.customer.company_name
            }
        return None

    def validate_sku(self, value):
        """
        Validate that the SKU is unique for this customer.
        """
        value = value.upper()
        customer = self.initial_data.get('customer')
        if customer:
            existing = Product.objects.filter(
                customer=customer,
                sku__iexact=value
            )
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "This SKU is already in use for this customer."
                )
        return value

    def validate(self, data):
        """
        Validate labeling quantities are non-negative.
        """
        for i in range(1, 6):
            qty = data.get(f'labeling_quantity_{i}')
            if qty is not None and qty < 0:
                raise serializers.ValidationError({
                    f'labeling_quantity_{i}': "Quantity cannot be negative."
                })
        return data