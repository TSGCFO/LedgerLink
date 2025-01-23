# orders/serializers.py
from rest_framework import serializers
from customers.serializers import CustomerSerializer
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    customer_details = CustomerSerializer(source='customer', read_only=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Order.PRIORITY_CHOICES, required=False)
    sku_quantity = serializers.JSONField(required=False)

    class Meta:
        model = Order
        fields = [
            'transaction_id',
            'customer',
            'customer_details',
            'close_date',
            'reference_number',
            'ship_to_name',
            'ship_to_company',
            'ship_to_address',
            'ship_to_address2',
            'ship_to_city',
            'ship_to_state',
            'ship_to_zip',
            'ship_to_country',
            'weight_lb',
            'line_items',
            'sku_quantity',
            'total_item_qty',
            'volume_cuft',
            'packages',
            'notes',
            'carrier',
            'status',
            'priority'
        ]
        read_only_fields = ['transaction_id']

    def validate_sku_quantity(self, value):
        """
        Validate that sku_quantity is a valid JSON object with SKU codes as keys
        and quantities as positive integer values.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("SKU quantity must be a JSON object")
        
        for sku, qty in value.items():
            if not isinstance(sku, str):
                raise serializers.ValidationError("SKU codes must be strings")
            if not isinstance(qty, int) or qty < 0:
                raise serializers.ValidationError("Quantities must be positive integers")
        
        return value

    def validate(self, data):
        """
        Custom validation for the entire order.
        """
        # Calculate total_item_qty from sku_quantity if provided
        if 'sku_quantity' in data:
            data['total_item_qty'] = sum(data['sku_quantity'].values())
            data['line_items'] = len(data['sku_quantity'])

        # Ensure shipping address is complete if any shipping field is provided
        shipping_fields = [
            'ship_to_name', 'ship_to_company', 'ship_to_address',
            'ship_to_city', 'ship_to_state', 'ship_to_zip', 'ship_to_country'
        ]
        
        provided_fields = [f for f in shipping_fields if data.get(f)]
        if provided_fields and len(provided_fields) != len(shipping_fields):
            raise serializers.ValidationError(
                "All shipping address fields must be provided if any are present"
            )

        return data
