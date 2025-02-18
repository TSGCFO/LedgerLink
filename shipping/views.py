from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import CADShipping, USShipping
from .serializers import CADShippingSerializer, USShippingSerializer

class CADShippingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CAD shipping CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = CADShipping.objects.all()
    serializer_class = CADShippingSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on various parameters.
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Filter by order
        transaction_id = self.request.query_params.get('transaction', None)
        if transaction_id:
            queryset = queryset.filter(transaction_id=transaction_id)

        # Filter by carrier
        carrier = self.request.query_params.get('carrier', None)
        if carrier:
            queryset = queryset.filter(carrier=carrier)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(tracking_number__icontains=search) |
                Q(ship_to_name__icontains=search) |
                Q(reference__icontains=search)
            )

        # Date range filtering
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(ship_date__range=[start_date, end_date])
        
        return queryset.select_related('customer', 'transaction')

    def list(self, request, *args, **kwargs):
        """
        List CAD shipping records with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new CAD shipping record.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'CAD shipping record created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing CAD shipping record.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'CAD shipping record updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete a CAD shipping record.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'CAD shipping record deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def carriers(self, request):
        """
        Get list of unique carriers.
        """
        carriers = CADShipping.objects.values_list(
            'carrier', flat=True
        ).distinct().order_by('carrier')
        return Response({
            'success': True,
            'data': list(filter(None, carriers))  # Filter out None values
        })

class USShippingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling US shipping CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = USShipping.objects.all()
    serializer_class = USShippingSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on various parameters.
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Filter by order
        transaction_id = self.request.query_params.get('transaction', None)
        if transaction_id:
            queryset = queryset.filter(transaction_id=transaction_id)

        # Filter by status
        current_status = self.request.query_params.get('current_status', None)
        if current_status:
            queryset = queryset.filter(current_status=current_status)

        delivery_status = self.request.query_params.get('delivery_status', None)
        if delivery_status:
            queryset = queryset.filter(delivery_status=delivery_status)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(tracking_number__icontains=search) |
                Q(ship_to_name__icontains=search) |
                Q(service_name__icontains=search)
            )

        # Date range filtering
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(ship_date__range=[start_date, end_date])
        
        return queryset.select_related('customer', 'transaction')

    def list(self, request, *args, **kwargs):
        """
        List US shipping records with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new US shipping record.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'US shipping record created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing US shipping record.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'US shipping record updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete a US shipping record.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'US shipping record deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def statuses(self, request):
        """
        Get lists of unique current and delivery statuses.
        """
        current_statuses = USShipping.objects.values_list(
            'current_status', flat=True
        ).distinct().order_by('current_status')
        delivery_statuses = USShipping.objects.values_list(
            'delivery_status', flat=True
        ).distinct().order_by('delivery_status')
        
        return Response({
            'success': True,
            'data': {
                'current_statuses': list(filter(None, current_statuses)),
                'delivery_statuses': list(filter(None, delivery_statuses))
            }
        })

    @action(detail=False, methods=['get'])
    def service_names(self, request):
        """
        Get list of unique service names.
        """
        services = USShipping.objects.values_list(
            'service_name', flat=True
        ).distinct().order_by('service_name')
        return Response({
            'success': True,
            'data': list(filter(None, services))
        })
