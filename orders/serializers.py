from rest_framework import serializers
from .models import Order
from customers.serializers import CustomerSerializer

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model providing CRUD operations.
    Includes nested customer details and choice field handling.
    """
    customer_details = CustomerSerializer(source='customer', read_only=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=False, default='draft')
    priority = serializers.ChoiceField(choices=Order.PRIORITY_CHOICES, required=False, default='medium')

    class Meta:
        model = Order
        fields = [
            'transaction_id', 'customer', 'customer_details', 'close_date',
            'reference_number', 'status', 'priority',
            'ship_to_name', 'ship_to_company', 'ship_to_address',
            'ship_to_address2', 'ship_to_city', 'ship_to_state',
            'ship_to_zip', 'ship_to_country', 'weight_lb',
            'line_items', 'sku_quantity', 'total_item_qty',
            'volume_cuft', 'packages', 'notes', 'carrier'
        ]
        read_only_fields = ['transaction_id']

    def validate_sku_quantity(self, value):
        """
        Validate the SKU quantity JSON structure.
        Expected format: {"SKU1": quantity1, "SKU2": quantity2, ...}
        """
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError(
                    "SKU quantity must be a dictionary mapping SKUs to quantities"
                )
            for sku, qty in value.items():
                if not isinstance(qty, (int, float)) or qty <= 0:
                    raise serializers.ValidationError(
                        f"Invalid quantity for SKU {sku}. Must be a positive number."
                    )
        return value

    def create(self, validated_data):
        """
        Create a new order with a generated transaction_id.
        """
        # Generate a transaction_id (using the current timestamp as a simple example)
        from django.utils import timezone
        import time
        validated_data['transaction_id'] = int(time.time() * 1000)  # milliseconds since epoch
        return super().create(validated_data)

    def validate(self, data):
        """
        Custom validation for the entire order.
        """
        # Calculate total_item_qty from sku_quantity if provided
        sku_quantity = data.get('sku_quantity')
        if sku_quantity:
            total_qty = sum(sku_quantity.values())
            data['total_item_qty'] = total_qty
            data['line_items'] = len(sku_quantity)

        # Ensure shipping address is complete if any shipping field is provided
        shipping_fields = [
            'ship_to_name', 'ship_to_company', 'ship_to_address',
            'ship_to_city', 'ship_to_state', 'ship_to_zip', 'ship_to_country'
        ]
        
        has_shipping = any(data.get(field) for field in shipping_fields)
        if has_shipping:
            required_fields = ['ship_to_name', 'ship_to_address', 'ship_to_city', 
                             'ship_to_state', 'ship_to_zip']
            missing_fields = [
                field for field in required_fields 
                if not data.get(field)
            ]
            if missing_fields:
                raise serializers.ValidationError({
                    'shipping': f"Missing required shipping fields: {', '.join(missing_fields)}"
                })

        # Status transition validation
        if self.instance and 'status' in data:
            old_status = self.instance.status
            new_status = data['status']
            
            # Prevent changing status of cancelled orders
            if old_status == 'cancelled' and new_status != 'cancelled':
                raise serializers.ValidationError({
                    'status': "Cannot change status of cancelled orders"
                })
            
            # Prevent skipping statuses (e.g., draft -> delivered)
            status_order = ['draft', 'submitted', 'shipped', 'delivered']
            if old_status in status_order and new_status in status_order:
                old_idx = status_order.index(old_status)
                new_idx = status_order.index(new_status)
                if new_idx > old_idx + 1:
                    raise serializers.ValidationError({
                        'status': f"Cannot change status from {old_status} to {new_status}"
                    })

        return data