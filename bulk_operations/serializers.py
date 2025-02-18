# bulk_operations/serializers.py
from rest_framework import serializers
from django.apps import apps
import json
from decimal import Decimal
import pandas as pd
import numpy as np


class BulkImportResponseSerializer(serializers.Serializer):
    """
    Serializer for bulk import responses.
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    errors = serializers.ListField(required=False)
    import_summary = serializers.DictField(required=False)


class BulkOperationBaseSerializer(serializers.Serializer):
    """
    Base serializer for bulk operations with common validation methods.
    """

    def validate_foreign_key(self, value, model):
        try:
            return model.objects.get(id=value)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with id {value} does not exist")
        except (ValueError, TypeError):
            raise serializers.ValidationError(f"Invalid {model.__name__} ID format")


class CustomerBulkSerializer(BulkOperationBaseSerializer):
    company_name = serializers.CharField(max_length=255)
    legal_business_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    zip = serializers.CharField(max_length=20, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    business_type = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def create(self, validated_data):
        Customer = apps.get_model('customers', 'Customer')
        return Customer.objects.create(**validated_data)


class OrderBulkSerializer(BulkOperationBaseSerializer):
    transaction_id = serializers.IntegerField()  # Primary key, externally assigned
    customer = serializers.IntegerField()
    close_date = serializers.DateTimeField(required=False, allow_null=True)
    reference_number = serializers.CharField(max_length=50)
    ship_to_name = serializers.CharField(max_length=255)
    ship_to_company = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ship_to_address = serializers.CharField(max_length=255)
    ship_to_address2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ship_to_city = serializers.CharField(max_length=100)
    ship_to_state = serializers.CharField(max_length=100)
    ship_to_zip = serializers.CharField(max_length=20)
    ship_to_country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    weight_lb = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    line_items = serializers.IntegerField(required=False, allow_null=True)
    sku_quantity = serializers.JSONField(required=False, allow_null=True)
    total_item_qty = serializers.IntegerField(required=False, allow_null=True)
    volume_cuft = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    packages = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    carrier = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(
        choices=['draft', 'submitted', 'shipped', 'delivered', 'cancelled'],
        required=False,
        allow_blank=True,
        allow_null=True,
        default='draft'
    )
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        required=False,
        allow_blank=True,
        allow_null=True,
        default='medium'
    )

    def validate_customer(self, value):
        Customer = apps.get_model('customers', 'Customer')
        return self.validate_foreign_key(value, Customer)

    def validate_sku_quantity(self, value):
        if pd.isna(value) or value is None or value == '' or value == 'nan':
            return None

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for SKU quantity")

        if not isinstance(value, dict):
            raise serializers.ValidationError("SKU quantity must be a dictionary")

        for sku, qty in value.items():
            if not isinstance(qty, (int, float)) or qty <= 0:
                raise serializers.ValidationError(f"Invalid quantity for SKU {sku}: {qty}")
        return value

    def validate_status(self, value):
        if pd.isna(value) or value is None or value == '' or value == 'nan' or isinstance(value, float):
            return 'draft'
        return value

    def validate_priority(self, value):
        if pd.isna(value) or value is None or value == '' or value == 'nan' or isinstance(value, float):
            return 'medium'
        return value

    def create(self, validated_data):
        Order = apps.get_model('orders', 'Order')
        return Order.objects.create(**validated_data)


class ProductBulkSerializer(BulkOperationBaseSerializer):
    sku = serializers.CharField(max_length=50)
    customer = serializers.IntegerField()
    labeling_unit_1 = serializers.CharField(max_length=50, required=False, allow_blank=True)
    labeling_quantity_1 = serializers.IntegerField(required=False)
    labeling_unit_2 = serializers.CharField(max_length=50, required=False, allow_blank=True)
    labeling_quantity_2 = serializers.IntegerField(required=False)
    labeling_unit_3 = serializers.CharField(max_length=50, required=False, allow_blank=True)
    labeling_quantity_3 = serializers.IntegerField(required=False)
    labeling_unit_4 = serializers.CharField(max_length=50, required=False, allow_blank=True)
    labeling_quantity_4 = serializers.IntegerField(required=False)
    labeling_unit_5 = serializers.CharField(max_length=50, required=False, allow_blank=True)
    labeling_quantity_5 = serializers.IntegerField(required=False)

    def validate_customer(self, value):
        Customer = apps.get_model('customers', 'Customer')
        return self.validate_foreign_key(value, Customer)

    def create(self, validated_data):
        Product = apps.get_model('products', 'Product')
        return Product.objects.create(**validated_data)


class ServiceBulkSerializer(BulkOperationBaseSerializer):
    service_name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    charge_type = serializers.ChoiceField(
        choices=[('single', 'Single Charge'), ('quantity', 'Quantity Based')],
        default='quantity'
    )

    def create(self, validated_data):
        Service = apps.get_model('services', 'Service')
        return Service.objects.create(**validated_data)


class MaterialBulkSerializer(BulkOperationBaseSerializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        Material = apps.get_model('materials', 'Material')
        return Material.objects.create(**validated_data)


class InsertBulkSerializer(BulkOperationBaseSerializer):
    sku = serializers.CharField(max_length=50)
    insert_name = serializers.CharField(max_length=255)
    insert_quantity = serializers.IntegerField()
    customer = serializers.IntegerField()

    def validate_customer(self, value):
        Customer = apps.get_model('customers', 'Customer')
        return self.validate_foreign_key(value, Customer)

    def create(self, validated_data):
        Insert = apps.get_model('inserts', 'Insert')
        return Insert.objects.create(**validated_data)


class CADShippingBulkSerializer(BulkOperationBaseSerializer):
    transaction = serializers.IntegerField()  # Order ID
    customer = serializers.IntegerField()
    service_code_description = serializers.CharField(max_length=255, required=False)
    ship_to_name = serializers.CharField(max_length=255)
    ship_to_address_1 = serializers.CharField(max_length=255)
    ship_to_address_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shiptoaddress3 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ship_to_city = serializers.CharField(max_length=100)
    ship_to_state = serializers.CharField(max_length=100)
    ship_to_country = serializers.CharField(max_length=100, required=False, default='CA')
    ship_to_postal_code = serializers.CharField(max_length=20)
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pre_tax_shipping_charge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    tax1type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    tax1amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    tax2type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    tax2amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    tax3type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    tax3amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    fuel_surcharge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    gross_weight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    box_length = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    box_width = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    box_height = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    box_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    carrier = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_transaction(self, value):
        Order = apps.get_model('orders', 'Order')
        return self.validate_foreign_key(value, Order)

    def validate_customer(self, value):
        Customer = apps.get_model('customers', 'Customer')
        return self.validate_foreign_key(value, Customer)

    def create(self, validated_data):
        CADShipping = apps.get_model('shipping', 'CADShipping')
        return CADShipping.objects.create(**validated_data)


class USShippingBulkSerializer(BulkOperationBaseSerializer):
    transaction = serializers.IntegerField()  # Order ID
    customer = serializers.IntegerField()
    ship_date = serializers.DateField(required=False)
    ship_to_name = serializers.CharField(max_length=255)
    ship_to_address_1 = serializers.CharField(max_length=255)
    ship_to_address_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    ship_to_city = serializers.CharField(max_length=100)
    ship_to_state = serializers.CharField(max_length=100)
    ship_to_zip = serializers.CharField(max_length=20)
    ship_to_country_code = serializers.CharField(max_length=2, default='US')
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    service_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    weight_lbs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    length_in = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    width_in = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    height_in = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    base_chg = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    carrier_peak_charge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    wizmo_peak_charge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    accessorial_charges = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    hst = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    gst = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    current_status = serializers.ChoiceField(
        choices=['pending', 'in_transit', 'delivered', 'exception'],
        required=False,
        default='pending'
    )
    delivery_status = serializers.ChoiceField(
        choices=['pending', 'attempted', 'delivered', 'failed'],
        required=False,
        default='pending'
    )

    def validate_transaction(self, value):
        Order = apps.get_model('orders', 'Order')
        return self.validate_foreign_key(value, Order)

    def validate_customer(self, value):
        Customer = apps.get_model('customers', 'Customer')
        return self.validate_foreign_key(value, Customer)

    def create(self, validated_data):
        USShipping = apps.get_model('shipping', 'USShipping')
        return USShipping.objects.create(**validated_data)


class BulkSerializerFactory:
    """
    Factory class to get the appropriate serializer for a given template type.
    """
    SERIALIZER_MAP = {
        'customers': CustomerBulkSerializer,
        'orders': OrderBulkSerializer,
        'products': ProductBulkSerializer,
        'services': ServiceBulkSerializer,
        'materials': MaterialBulkSerializer,
        'inserts': InsertBulkSerializer,
        'cad_shipping': CADShippingBulkSerializer,
        'us_shipping': USShippingBulkSerializer,
    }

    @classmethod
    def get_serializer(cls, template_type):
        serializer_class = cls.SERIALIZER_MAP.get(template_type)
        if not serializer_class:
            raise KeyError(f"No serializer found for template type: {template_type}")
        return serializer_class