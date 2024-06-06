from rest_framework import serializers
from .models import Customer, Service, CustomerService, Insert, Product, ServiceLog, Order

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

class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
