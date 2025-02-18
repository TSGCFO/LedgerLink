from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer that includes common fields and functionality.
    All model serializers should inherit from this.
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True

    def validate(self, attrs):
        """
        Perform base validation and then any model-specific validation
        """
        attrs = super().validate(attrs)
        self.validate_business_rules(attrs)
        return attrs

    def validate_business_rules(self, attrs):
        """
        Hook for implementing business rule validations in child classes
        """
        pass