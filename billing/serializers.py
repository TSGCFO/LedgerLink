from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from .models import BillingReport

class BillingReportSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BillingReport
        fields = [
            'id', 'customer', 'customer_name', 'start_date', 'end_date',
            'generated_at', 'total_amount', 'created_by', 'created_by_name',
            'updated_by', 'updated_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'generated_at', 'created_by', 'updated_by',
            'created_at', 'updated_at'
        ]

    def get_customer_name(self, obj):
        return obj.customer.company_name if obj.customer else None

    def get_created_by_name(self, obj):
        # Return None in development mode
        return None if not obj.created_by else obj.created_by.get_full_name()

    def get_updated_by_name(self, obj):
        # Return None in development mode
        return None if not obj.updated_by else obj.updated_by.get_full_name()

class ReportRequestSerializer(serializers.Serializer):
    customer = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    output_format = serializers.ChoiceField(
        choices=['preview', 'excel', 'pdf', 'csv'],
        default='preview'
    )

    def validate(self, data):
        """
        Validate the report request data.
        Basic validation only in development mode.
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                "date_range": "Start date must be before end date"
            })

        # Validate customer exists
        from customers.models import Customer
        try:
            Customer.objects.get(id=data['customer'])
        except Customer.DoesNotExist:
            raise serializers.ValidationError({
                "customer": "Selected customer does not exist"
            })
        
        return data 