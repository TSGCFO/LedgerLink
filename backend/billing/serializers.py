from rest_framework import serializers
from .models import Customer, Service, CustomerService, Insert, Product, ServiceLog, Order
import json

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class CustomerServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerService
        fields = '__all__'

class InsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insert
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ServiceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLog
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    sku_quantity = serializers.JSONField()

    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        # Ensure sku_quantity is properly formatted for JSON
        representation = super().to_representation(instance)
        if isinstance(instance.sku_quantity, str):
            representation['sku_quantity'] = json.loads(instance.sku_quantity)
        return representation

    def to_internal_value(self, data):
        # Ensure sku_quantity is properly formatted for JSON
        if isinstance(data.get('sku_quantity'), list):
            data['sku_quantity'] = json.dumps(data['sku_quantity'])
        return super().to_internal_value(data)