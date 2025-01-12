# ai_core/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class AIOperation(models.Model):
    """Tracks all AI system operations"""
    OPERATION_TYPES = [
        ('analysis', 'Project Analysis'),
        ('generation', 'Code Generation'),
        ('modification', 'Code Modification'),
        ('feature', 'Feature Implementation')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    details = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'ai_operations'
        ordering = ['-started_at']


class CodePattern(models.Model):
    """Stores identified code patterns for learning"""
    pattern_type = models.CharField(max_length=50)
    pattern_data = models.JSONField()
    frequency = models.IntegerField(default=1)
    confidence_score = models.FloatField(default=1.0)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_code_patterns'
        indexes = [
            models.Index(fields=['pattern_type', 'frequency'])
        ]


class FeatureRequest(models.Model):
    """Tracks feature implementation requests"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    requested_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Analysis'),
            ('analyzed', 'Analyzed'),
            ('implementing', 'Implementing'),
            ('testing', 'Testing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    analysis_result = models.JSONField(null=True, blank=True)
    implementation_details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_feature_requests'


class ProjectContext(models.Model):
    """Stores project context data"""
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_project_context'