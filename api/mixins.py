import AuditLog
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError

class TimestampMixin:
    """
    Mixin to automatically handle created_at and updated_at fields.
    """
    def perform_create(self, serializer):
        serializer.save(
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())

class OrganizationQuerySetMixin:
    """
    Mixin to filter querysets based on user's organization.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_staff:
            return queryset
        
        if hasattr(user, 'organization') and user.organization:
            return queryset.filter(organization=user.organization)
        
        return queryset.none()

class SoftDeleteMixin:
    """
    Mixin to handle soft deletion of objects.
    Requires a boolean field 'is_active' on the model.
    """
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

class StandardizedResponseMixin:
    """
    Mixin to provide standardized response format for all actions.
    """
    def get_standardized_response(self, data=None, message=None, status_code=200):
        response_data = {
            'success': status_code < 400,
            'message': message,
            'data': data
        }
        return Response(response_data, status=status_code)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.get_standardized_response(
            data=response.data,
            message="Retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.get_standardized_response(
            data=response.data,
            message="Created successfully",
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.get_standardized_response(
            data=response.data,
            message="Updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return self.get_standardized_response(
            message="Deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )

class AuditLogMixin:
    """
    Mixin to log all changes to objects.
    Requires an AuditLog model to be defined.
    """
    def _log_action(self, action, instance, changes=None):
        from django.contrib.contenttypes.models import ContentType
        
        if not hasattr(self, 'request'):
            return
        
        content_type = ContentType.objects.get_for_model(instance)
        
        AuditLog.objects.create(
            user=self.request.user,
            content_type=content_type,
            object_id=instance.id,
            action=action,
            changes=changes
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_action('CREATE', instance)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self._log_action('UPDATE', instance, serializer.changes)
        return instance

    def perform_destroy(self, instance):
        self._log_action('DELETE', instance)
        super().perform_destroy(instance)

class ValidationMixin:
    """
    Mixin to provide additional validation capabilities.
    """
    def validate_unique_together(self, attrs, fields, queryset=None):
        """
        Validate unique together constraints manually.
        Useful when dealing with case-insensitive uniqueness.
        """
        if queryset is None:
            queryset = self.Meta.model.objects.all()

        filters = Q()
        for field in fields:
            if field in attrs:
                filters &= Q(**{f"{field}__iexact": attrs[field]})

        # Exclude current instance in case of updates
        instance = getattr(self, 'instance', None)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.filter(filters).exists():
            field_names = ', '.join(fields)
            raise ValidationError(f"The combination of {field_names} must be unique.")

class CacheMixin:
    """
    Mixin to handle caching of querysets.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self, 'action') and self.action == 'list':
            return queryset.cache()
        return queryset

class BulkOperationsMixin:
    """
    Mixin to handle bulk create, update, and delete operations.
    """
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()

    def bulk_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            self.get_queryset(),
            data=request.data,
            many=True,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data)

    def perform_bulk_update(self, serializer):
        serializer.save()

    def bulk_delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# api/mixins.py
# Add this new mixin class

class BulkOperationMixin:
    """
    Mixin to handle bulk operation functionality.
    """
    def get_bulk_operation_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for bulk operations.
        """
        serializer_class = self.get_bulk_operation_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_bulk_operation_serializer_class(self):
        """
        Return the class to use for bulk operation serializer.
        Defaults to using the regular serializer_class if not specified.
        """
        return getattr(self, 'bulk_operation_serializer_class', self.get_serializer_class())

    def perform_bulk_operation(self, serializer):
        """
        Perform the bulk operation.
        """
        serializer.save()

    def handle_bulk_exception(self, exc):
        """
        Handle any exception that occurs during bulk operations.
        """
        if isinstance(exc, ValidationError):
            return Response(
                {'detail': exc.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'detail': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )