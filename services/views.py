from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Service
from .serializers import ServiceSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling service CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on search parameters.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        charge_type = self.request.query_params.get('charge_type', None)

        if search:
            queryset = queryset.filter(
                Q(service_name__icontains=search) |
                Q(description__icontains=search)
            )
        if charge_type:
            queryset = queryset.filter(charge_type=charge_type)
        
        return queryset.order_by('service_name')

    def list(self, request, *args, **kwargs):
        """
        List services with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new service.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Service created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing service.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Service updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete a service.
        """
        instance = self.get_object()
        # Check if service is being used by any customer services
        if instance.customerservice_set.exists():
            return Response({
                'success': False,
                'message': 'Cannot delete service as it is assigned to customers'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Service deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def charge_types(self, request):
        """
        Get list of available charge types.
        """
        return Response({
            'success': True,
            'data': [
                {'value': choice[0], 'label': choice[1]}
                for choice in Service.CHARGE_TYPES
            ]
        })
