from rest_framework import serializers
from .models import CADShipping, USShipping
from orders.serializers import OrderSerializer
from customers.serializers import CustomerSerializer

class CADShippingSerializer(serializers.ModelSerializer):
    """
    Serializer for CADShipping model providing CRUD operations.
    Includes nested order and customer details.
    """
    order_details = OrderSerializer(source='transaction', read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    total_tax = serializers.SerializerMethodField()
    total_charges = serializers.SerializerMethodField()

    class Meta:
        model = CADShipping
        fields = [
            'transaction', 'order_details', 'customer', 'customer_details',
            'service_code_description', 'ship_to_name', 'ship_to_address_1',
            'ship_to_address_2', 'shiptoaddress3', 'ship_to_city',
            'ship_to_state', 'ship_to_country', 'ship_to_postal_code',
            'tracking_number', 'pre_tax_shipping_charge',
            'tax1type', 'tax1amount', 'tax2type', 'tax2amount',
            'tax3type', 'tax3amount', 'fuel_surcharge', 'reference',
            'weight', 'gross_weight', 'box_length', 'box_width',
            'box_height', 'box_name', 'ship_date', 'carrier',
            'raw_ship_date', 'total_tax', 'total_charges'
        ]
        read_only_fields = ['transaction']

    def get_total_tax(self, obj):
        """
        Calculate total tax amount.
        """
        total = 0
        if obj.tax1amount:
            total += obj.tax1amount
        if obj.tax2amount:
            total += obj.tax2amount
        if obj.tax3amount:
            total += obj.tax3amount
        return total

    def get_total_charges(self, obj):
        """
        Calculate total charges including shipping, taxes, and fuel surcharge.
        """
        total = 0
        if obj.pre_tax_shipping_charge:
            total += obj.pre_tax_shipping_charge
        if obj.fuel_surcharge:
            total += obj.fuel_surcharge
        total += self.get_total_tax(obj)
        return total

    def validate(self, data):
        """
        Custom validation for shipping data.
        """
        # Ensure required shipping address fields are provided together
        shipping_fields = [
            'ship_to_name', 'ship_to_address_1', 'ship_to_city',
            'ship_to_state', 'ship_to_postal_code'
        ]
        
        if any(data.get(field) for field in shipping_fields):
            missing_fields = [
                field for field in shipping_fields 
                if not data.get(field)
            ]
            if missing_fields:
                raise serializers.ValidationError({
                    'shipping': f"Missing required shipping fields: {', '.join(missing_fields)}"
                })

        return data

class USShippingSerializer(serializers.ModelSerializer):
    """
    Serializer for USShipping model providing CRUD operations.
    Includes nested order and customer details.
    """
    order_details = OrderSerializer(source='transaction', read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    total_charges = serializers.SerializerMethodField()
    delivery_days = serializers.SerializerMethodField()

    class Meta:
        model = USShipping
        fields = [
            'transaction', 'order_details', 'customer', 'customer_details',
            'ship_date', 'ship_to_name', 'ship_to_address_1',
            'ship_to_address_2', 'ship_to_city', 'ship_to_state',
            'ship_to_zip', 'ship_to_country_code', 'tracking_number',
            'service_name', 'weight_lbs', 'length_in', 'width_in',
            'height_in', 'base_chg', 'carrier_peak_charge',
            'wizmo_peak_charge', 'accessorial_charges', 'rate',
            'hst', 'gst', 'current_status', 'delivery_status',
            'first_attempt_date', 'delivery_date', 'days_to_first_deliver',
            'total_charges', 'delivery_days'
        ]
        read_only_fields = ['transaction', 'days_to_first_deliver']

    def get_total_charges(self, obj):
        """
        Calculate total charges including base charge, peak charges, and taxes.
        """
        total = 0
        if obj.base_chg:
            total += obj.base_chg
        if obj.carrier_peak_charge:
            total += obj.carrier_peak_charge
        if obj.wizmo_peak_charge:
            total += obj.wizmo_peak_charge
        if obj.accessorial_charges:
            total += obj.accessorial_charges
        if obj.hst:
            total += obj.hst
        if obj.gst:
            total += obj.gst
        return total

    def get_delivery_days(self, obj):
        """
        Get delivery days, either from days_to_first_deliver or calculate from dates.
        """
        if obj.days_to_first_deliver is not None:
            return obj.days_to_first_deliver
        elif obj.delivery_date and obj.ship_date:
            return (obj.delivery_date - obj.ship_date.date()).days
        return None

    def validate(self, data):
        """
        Custom validation for shipping data.
        """
        # Ensure required shipping address fields are provided together
        shipping_fields = [
            'ship_to_name', 'ship_to_address_1', 'ship_to_city',
            'ship_to_state', 'ship_to_zip'
        ]
        
        if any(data.get(field) for field in shipping_fields):
            missing_fields = [
                field for field in shipping_fields 
                if not data.get(field)
            ]
            if missing_fields:
                raise serializers.ValidationError({
                    'shipping': f"Missing required shipping fields: {', '.join(missing_fields)}"
                })

        # Validate dates
        if data.get('delivery_date') and data.get('ship_date'):
            if data['delivery_date'] < data['ship_date']:
                raise serializers.ValidationError({
                    'delivery_date': "Delivery date cannot be earlier than ship date"
                })

        if data.get('first_attempt_date'):
            if data.get('ship_date') and data['first_attempt_date'] < data['ship_date']:
                raise serializers.ValidationError({
                    'first_attempt_date': "First attempt date cannot be earlier than ship date"
                })

        return data