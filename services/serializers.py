# services/serializers.py
from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id', 'service_name', 'description', 'charge_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_charge_type(self, value):
        """
        Validate that charge_type is one of the allowed choices.
        """
        valid_choices = dict(Service.CHARGE_TYPES).keys()
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid charge type. Must be one of: {', '.join(valid_choices)}"
            )
        return value
