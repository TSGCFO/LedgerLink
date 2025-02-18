from rest_framework import serializers
from .models import Material, BoxPrice

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'unit_price']

class BoxPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPrice
        fields = ['id', 'box_type', 'price', 'length', 'width', 'height']