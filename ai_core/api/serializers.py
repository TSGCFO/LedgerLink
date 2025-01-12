# ai_core/api/serializers.py
from rest_framework import serializers
from ..models import FeatureRequest, AIOperation, CodePattern

class FeatureRequestSerializer(serializers.ModelSerializer):
    """Serializer for feature requests"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requested_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FeatureRequest
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'requested_by', 'created_at', 'updated_at',
            'analysis_result', 'implementation_details'
        ]
        read_only_fields = [
            'status', 'status_display', 'created_at', 'updated_at',
            'analysis_result', 'implementation_details', 'requested_by'
        ]

class AIOperationSerializer(serializers.ModelSerializer):
    """Serializer for AI operations"""
    duration = serializers.SerializerMethodField()

    class Meta:
        model = AIOperation
        fields = [
            'id', 'operation_type', 'status',
            'started_at', 'completed_at',
            'details', 'error_message', 'duration'
        ]
        read_only_fields = ['started_at', 'completed_at', 'duration']

    def get_duration(self, obj):
        """Calculate operation duration"""
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None

class CodePatternSerializer(serializers.ModelSerializer):
    """Serializer for code patterns"""
    class Meta:
        model = CodePattern
        fields = [
            'id', 'pattern_type', 'pattern_data',
            'frequency', 'confidence_score',
            'last_used', 'created_at'
        ]
        read_only_fields = ['frequency', 'last_used', 'created_at']

class CodeAnalysisSerializer(serializers.Serializer):
    """Serializer for code analysis requests"""
    code = serializers.CharField(required=True, help_text="Code to analyze")
    analysis_type = serializers.ChoiceField(
        choices=[
            ('model', 'Model Analysis'),
            ('view', 'View Analysis'),
            ('form', 'Form Analysis'),
            ('serializer', 'Serializer Analysis'),
            ('url', 'URL Pattern Analysis')
        ],
        help_text="Type of analysis to perform"
    )
    context = serializers.JSONField(
        required=False,
        help_text="Additional context for analysis"
    )

class CodeGenerationSerializer(serializers.Serializer):
    """Serializer for code generation requests"""
    type = serializers.ChoiceField(
        choices=[
            ('model', 'Generate Model'),
            ('view', 'Generate View'),
            ('form', 'Generate Form'),
            ('serializer', 'Generate Serializer')
        ],
        help_text="Type of code to generate"
    )
    specification = serializers.JSONField(
        help_text="Specifications for code generation"
    )

class FeatureImplementationSerializer(serializers.Serializer):
    """Serializer for feature implementation requests"""
    priority = serializers.ChoiceField(
        choices=[
            ('low', 'Low Priority'),
            ('normal', 'Normal Priority'),
            ('high', 'High Priority')
        ],
        default='normal',
        help_text="Implementation priority level"
    )
    schedule_for = serializers.DateTimeField(
        required=False,
        help_text="Optional scheduled implementation time"
    )

class ImplementationStatusSerializer(serializers.Serializer):
    """Serializer for implementation status"""
    status = serializers.CharField(read_only=True)
    analysis_result = serializers.JSONField(read_only=True)
    implementation_details = serializers.JSONField(read_only=True)
    operations = serializers.JSONField(read_only=True)

    def to_representation(self, instance):
        """Customize the status representation"""
        data = super().to_representation(instance)
        # Add additional status information
        if instance.get('operations'):
            data['latest_operation'] = instance['operations'].get('latest_operation')
            data['progress'] = {
                'total_operations': instance['operations'].get('total', 0),
                'completed_operations': instance['operations'].get('completed', 0),
                'failed_operations': instance['operations'].get('failed', 0)
            }
        return data

class ProjectAnalysisSerializer(serializers.Serializer):
    """Serializer for project analysis results"""
    apps = serializers.JSONField(read_only=True)
    models = serializers.JSONField(read_only=True)
    views = serializers.JSONField(read_only=True)
    urls = serializers.JSONField(read_only=True)
    templates = serializers.JSONField(read_only=True)
    stats = serializers.JSONField(read_only=True)

class ErrorSerializer(serializers.Serializer):
    """Serializer for error responses"""
    error = serializers.CharField()
    details = serializers.JSONField(required=False)