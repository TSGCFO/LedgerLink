from rest_framework import serializers
from .models import BillingReport, OrderCost, ServiceCost
from customers.models import Customer
from datetime import datetime


class ServiceCostSerializer(serializers.ModelSerializer):
    """Serializer for ServiceCost model"""
    
    class Meta:
        model = ServiceCost
        fields = ['service_id', 'service_name', 'amount']


class OrderCostSerializer(serializers.ModelSerializer):
    """Serializer for OrderCost model"""
    
    service_costs = ServiceCostSerializer(many=True, read_only=True)
    reference_number = serializers.CharField(source='order.reference_number', read_only=True)
    order_date = serializers.DateTimeField(source='order.close_date', read_only=True, format='%Y-%m-%d')
    
    class Meta:
        model = OrderCost
        fields = ['order_id', 'reference_number', 'order_date', 'service_costs', 'total_amount']
        
    order_id = serializers.SerializerMethodField()
    
    def get_order_id(self, obj):
        return obj.order.transaction_id


class BillingReportSerializer(serializers.ModelSerializer):
    """Serializer for BillingReport model"""
    
    order_costs = OrderCostSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    
    class Meta:
        model = BillingReport
        fields = [
            'id', 'customer_id', 'customer_name', 'start_date', 'end_date',
            'created_at', 'order_costs', 'service_totals', 'total_amount'
        ]
        

class BillingReportRequestSerializer(serializers.Serializer):
    """Serializer for billing report generation requests"""
    
    customer_id = serializers.IntegerField()
    start_date = serializers.DateField(format='%Y-%m-%d')
    end_date = serializers.DateField(format='%Y-%m-%d')
    customer_services = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of customer service IDs to include in report (empty means all services)"
    )
    output_format = serializers.ChoiceField(
        choices=['json', 'csv', 'pdf', 'dict'],
        default='json'
    )
    
    def validate_customer_id(self, value):
        """Validate customer ID exists"""
        if not Customer.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Customer with ID {value} not found")
        return value
    
    def validate_customer_services(self, value):
        """Validate customer services exist and belong to the customer"""
        if not value:  # Empty list means all services, which is valid
            return value
            
        from customer_services.models import CustomerService
        
        # Get customer ID from the data
        customer_id = self.initial_data.get('customer_id')
        if not customer_id:
            return value  # Skip validation if customer_id not provided
            
        # Check if services exist and belong to the customer
        valid_service_ids = CustomerService.objects.filter(
            customer_id=customer_id
        ).values_list('id', flat=True)
        
        # Convert to set for faster lookup
        valid_service_ids_set = set(valid_service_ids)
        
        # Find invalid services
        invalid_services = [svc_id for svc_id in value if svc_id not in valid_service_ids_set]
        
        if invalid_services:
            raise serializers.ValidationError(
                f"Invalid service IDs for customer {customer_id}: {invalid_services}"
            )
            
        return value
    
    def validate(self, data):
        """Validate start date is before end date"""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
            
        # Check if date range is not too large (uses MAX_REPORT_DATE_RANGE from settings)
        from django.conf import settings
        max_days = getattr(settings, 'MAX_REPORT_DATE_RANGE', 365)
        delta = (data['end_date'] - data['start_date']).days
        if delta > max_days:
            raise serializers.ValidationError(
                f"Date range exceeds maximum allowed ({max_days} days). " 
                f"Your range is {delta} days."
            )
            
        return data


class BillingReportSummarySerializer(serializers.ModelSerializer):
    """Serializer for BillingReport list views (summary only)"""
    
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    order_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BillingReport
        fields = [
            'id', 'customer_id', 'customer_name', 'start_date', 'end_date',
            'created_at', 'total_amount', 'order_count'
        ]
        
    def get_order_count(self, obj):
        return obj.order_costs.count()