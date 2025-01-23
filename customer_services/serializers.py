# customer_services/serializers.py
from rest_framework import serializers
from .models import CustomerService
from customers.serializers import CustomerSerializer
from services.serializers import ServiceSerializer
from products.models import Product

class CustomerServiceSerializer(serializers.ModelSerializer):
    customer_details = CustomerSerializer(source='customer', read_only=True)
    service_details = ServiceSerializer(source='service', read_only=True)
    sku_list = serializers.SerializerMethodField()

    class Meta:
        model = CustomerService
        fields = [
            'id', 'customer', 'service', 'unit_price',
            'created_at', 'updated_at', 'customer_details',
            'service_details', 'sku_list'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_sku_list(self, obj):
        """Get a list of SKUs with their details."""
        return [
            {
                'id': sku.id,
                'sku': sku.sku,
                'customer': sku.customer.company_name,
            }
            for sku in obj.skus.all()
        ]

    def validate(self, data):
        """
        Validate that the customer-service combination is unique
        and the unit price is positive.
        """
        if self.instance is None:  # Only for creation
            customer = data.get('customer')
            service = data.get('service')
            if CustomerService.objects.filter(
                customer=customer,
                service=service
            ).exists():
                raise serializers.ValidationError(
                    "This customer already has this service assigned."
                )

        unit_price = data.get('unit_price')
        if unit_price and unit_price <= 0:
            raise serializers.ValidationError(
                "Unit price must be greater than zero."
            )

        return data
