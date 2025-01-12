# ai_core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import AIOperation, CodePattern, FeatureRequest, ProjectContext


@admin.register(AIOperation)
class AIOperationAdmin(admin.ModelAdmin):
    list_display = ('operation_type', 'status', 'started_at', 'completed_at', 'error_status')
    list_filter = ('operation_type', 'status')
    search_fields = ('details', 'error_message')
    readonly_fields = ('started_at', 'completed_at')

    fieldsets = (
        ('Operation Info', {
            'fields': ('operation_type', 'status', 'started_at', 'completed_at')
        }),
        ('Details', {
            'fields': ('details', 'error_message'),
            'classes': ('collapse',)
        }),
    )

    def error_status(self, obj):
        if obj.error_message:
            return format_html(
                '<span style="color: red;">⚠ Error</span>'
            )
        return format_html(
            '<span style="color: green;">✓ OK</span>'
        )

    error_status.short_description = 'Error Status'


@admin.register(CodePattern)
class CodePatternAdmin(admin.ModelAdmin):
    list_display = ('pattern_type', 'frequency', 'confidence_score', 'last_used')
    list_filter = ('pattern_type',)
    search_fields = ('pattern_data',)
    readonly_fields = ('frequency', 'last_used', 'created_at')

    fieldsets = (
        ('Pattern Info', {
            'fields': ('pattern_type', 'frequency', 'confidence_score')
        }),
        ('Pattern Data', {
            'fields': ('pattern_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_used', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Patterns should be created by the AI system, not manually
        return False


@admin.register(FeatureRequest)
class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'requested_by', 'created_at', 'implementation_status')
    list_filter = ('status', 'requested_by')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'analysis_result', 'implementation_details')

    fieldsets = (
        ('Request Info', {
            'fields': ('title', 'description', 'status', 'requested_by')
        }),
        ('Analysis', {
            'fields': ('analysis_result',),
            'classes': ('collapse',)
        }),
        ('Implementation', {
            'fields': ('implementation_details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def implementation_status(self, obj):
        status_colors = {
            'pending': 'orange',
            'analyzed': 'blue',
            'implementing': 'purple',
            'testing': 'teal',
            'completed': 'green',
            'failed': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )

    implementation_status.short_description = 'Status'

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['completed', 'failed']:
            return self.readonly_fields + ('status',)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in ['implementing', 'testing']:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(ProjectContext)
class ProjectContextAdmin(admin.ModelAdmin):
    list_display = ('key', 'last_updated', 'value_preview')
    search_fields = ('key',)
    readonly_fields = ('last_updated',)

    def value_preview(self, obj):
        """Shows a preview of the JSON value"""
        import json
        preview = str(obj.value)
        if len(preview) > 50:
            preview = preview[:47] + '...'
        return preview

    value_preview.short_description = 'Value Preview'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ('key',)
        return self.readonly_fields


class AISystemAdminSite(admin.AdminSite):
    site_header = 'LedgerLink AI Administration'
    site_title = 'LedgerLink AI Admin'
    index_title = 'AI System Management'

# Uncomment these lines if you want a custom admin site for AI components
ai_admin_site = AISystemAdminSite(name='ai_admin')
ai_admin_site.register(AIOperation, AIOperationAdmin)
ai_admin_site.register(CodePattern, CodePatternAdmin)
ai_admin_site.register(FeatureRequest, FeatureRequestAdmin)
ai_admin_site.register(ProjectContext, ProjectContextAdmin)