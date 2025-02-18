from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling order CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on various parameters.
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by priority
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(reference_number__icontains=search) |
                Q(ship_to_name__icontains=search) |
                Q(ship_to_company__icontains=search) |
                Q(customer__company_name__icontains=search)
            )

        # Date range filtering
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        
        return queryset.select_related('customer')

    def list(self, request, *args, **kwargs):
        """
        List orders with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new order.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Order created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing order.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Order updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete an order.
        """
        instance = self.get_object()
        if instance.status not in ['draft', 'cancelled']:
            return Response({
                'success': False,
                'message': 'Can only delete draft or cancelled orders'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Order deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order.
        """
        instance = self.get_object()
        if instance.status == 'delivered':
            return Response({
                'success': False,
                'message': 'Cannot cancel a delivered order'
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.status = 'cancelled'
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Order cancelled successfully',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def status_counts(self, request):
        """
        Get count of orders by status.
        """
        counts = {}
        for status_choice in Order.STATUS_CHOICES:
            counts[status_choice[0]] = self.get_queryset().filter(
                status=status_choice[0]
            ).count()
        
        return Response({
            'success': True,
            'data': counts
        })

    @action(detail=False, methods=['get'])
    def choices(self, request):
        """
        Get available choices for status and priority fields.
        """
        return Response({
            'success': True,
            'data': {
                'status_choices': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in Order.STATUS_CHOICES
                ],
                'priority_choices': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in Order.PRIORITY_CHOICES
                ]
            }
        })