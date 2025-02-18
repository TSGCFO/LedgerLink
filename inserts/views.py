from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Sum
from .models import Insert
from .serializers import InsertSerializer

class InsertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling insert CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = Insert.objects.all()
    serializer_class = InsertSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on various parameters.
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(sku__icontains=search) |
                Q(insert_name__icontains=search) |
                Q(customer__company_name__icontains=search)
            )

        # Quantity filter
        min_quantity = self.request.query_params.get('min_quantity', None)
        max_quantity = self.request.query_params.get('max_quantity', None)
        if min_quantity:
            queryset = queryset.filter(insert_quantity__gte=min_quantity)
        if max_quantity:
            queryset = queryset.filter(insert_quantity__lte=max_quantity)
        
        return queryset.select_related('customer')

    def list(self, request, *args, **kwargs):
        """
        List inserts with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new insert.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Insert created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing insert.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Insert updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete an insert.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Insert deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        """
        Update insert quantity.
        Expects quantity and operation ('add' or 'subtract') in request data.
        """
        instance = self.get_object()
        quantity = request.data.get('quantity')
        operation = request.data.get('operation', 'add')

        if not quantity or not isinstance(quantity, int) or quantity <= 0:
            return Response({
                'success': False,
                'message': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation not in ['add', 'subtract']:
            return Response({
                'success': False,
                'message': 'Invalid operation'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if operation == 'add':
                instance.insert_quantity += quantity
            else:
                if instance.insert_quantity < quantity:
                    return Response({
                        'success': False,
                        'message': 'Insufficient quantity'
                    }, status=status.HTTP_400_BAD_REQUEST)
                instance.insert_quantity -= quantity

            instance.save()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'message': f'Quantity {operation}ed successfully',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get insert statistics.
        """
        total_inserts = self.get_queryset().count()
        total_quantity = self.get_queryset().aggregate(
            total=Sum('insert_quantity')
        )['total'] or 0
        
        return Response({
            'success': True,
            'data': {
                'total_inserts': total_inserts,
                'total_quantity': total_quantity
            }
        })
