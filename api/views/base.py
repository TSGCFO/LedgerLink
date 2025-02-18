from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Prefetch
from django_filters import rest_framework as filters

class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that provides common functionality.
    All model viewsets should inherit from this.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    
    def get_queryset(self):
        """
        Get the base queryset and apply common optimizations and filters.
        Override get_base_queryset in child classes to provide the initial queryset.
        """
        queryset = self.get_base_queryset()
        queryset = self.optimize_queryset(queryset)
        return self.apply_filters(queryset)
    
    def get_base_queryset(self):
        """
        Hook for child classes to provide their base queryset.
        """
        if self.queryset is None:
            raise NotImplementedError(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.queryset or override %(cls)s.get_base_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return self.queryset
    
    def optimize_queryset(self, queryset):
        """
        Hook for implementing query optimizations in child classes.
        Override this to add select_related, prefetch_related, or annotations.
        """
        return queryset
    
    def apply_filters(self, queryset):
        """
        Hook for applying custom filters in child classes.
        """
        return queryset
    
    def handle_exception(self, exc):
        """
        Handle exceptions in a consistent way across all viewsets.
        """
        if hasattr(exc, 'detail'):
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR),
                        'message': str(exc.detail),
                    }
                },
                status=getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        return super().handle_exception(exc)
    
    def get_success_headers(self, data):
        """
        Add common success headers for create operations.
        """
        headers = super().get_success_headers(data)
        if 'id' in data:
            headers['Resource-ID'] = str(data['id'])
        return headers
    
    def perform_create(self, serializer):
        """
        Extend create operation to handle additional business logic.
        """
        instance = serializer.save()
        self.post_create(instance)
    
    def post_create(self, instance):
        """
        Hook for implementing post-create operations in child classes.
        """
        pass
    
    def perform_update(self, serializer):
        """
        Extend update operation to handle additional business logic.
        """
        instance = serializer.save()
        self.post_update(instance)
    
    def post_update(self, instance):
        """
        Hook for implementing post-update operations in child classes.
        """
        pass
    
    def perform_destroy(self, instance):
        """
        Extend destroy operation to handle additional business logic.
        """
        self.pre_destroy(instance)
        super().perform_destroy(instance)
    
    def pre_destroy(self, instance):
        """
        Hook for implementing pre-destroy operations in child classes.
        """
        pass