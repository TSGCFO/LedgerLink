from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
import logging
from .models import CustomerService
from .serializers import CustomerServiceSerializer

logger = logging.getLogger(__name__)

class CustomerServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling customer service CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = CustomerService.objects.all()
    serializer_class = CustomerServiceSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on customer or service.
        """
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer', None)
        service_id = self.request.query_params.get('service', None)
        search = self.request.query_params.get('search', None)

        logger.debug('Query params - customer_id: %s, service_id: %s, search: %s',
                    customer_id, service_id, search)

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        if search:
            queryset = queryset.filter(
                Q(customer__company_name__icontains=search) |
                Q(service__service_name__icontains=search)
            )
        
        queryset = queryset.select_related(
            'customer',
            'service'
        ).prefetch_related('skus')

        logger.debug('Filtered queryset count: %d', queryset.count())
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().select_related(
                'customer',
                'service'
            )
            serializer = self.get_serializer(queryset, many=True)
            
            response_data = {
                'success': True,
                'data': serializer.data
            }
            logger.info('Customer Services Response: %s', response_data)
            return Response(response_data)
        except Exception as e:
            logger.error('Error in customer services list: %s', str(e))
            return Response({
                'success': False,
                'error': 'Failed to fetch customer services',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        """
        List customer services with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        try:
            response_data = {
                'success': True,
                'data': serializer.data
            }
            logger.info('Customer Services Response: %s', response_data)
            return Response(response_data)
        except Exception as e:
            logger.error('Error in customer services list: %s', str(e))
            return Response({
                'success': False,
                'error': 'Failed to fetch customer services'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """
        Create a new customer service assignment.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Customer service created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing customer service.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Customer service updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete a customer service assignment.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Customer service deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_skus(self, request, pk=None):
        """
        Add SKUs to a customer service.
        """
        instance = self.get_object()
        sku_codes = request.data.get('sku_ids', [])
        
        # Convert SKU codes to Product instances
        from products.models import Product
        products = Product.objects.filter(
            sku__in=sku_codes,
            customer=instance.customer  # Only get SKUs for this customer
        )
        
        # Check if all SKUs were found and belong to the customer
        found_sku_codes = set(products.values_list('sku', flat=True))
        missing_sku_codes = set(sku_codes) - found_sku_codes
        
        if missing_sku_codes:
            return Response({
                'success': False,
                'message': f'SKUs not found or do not belong to this customer: {", ".join(missing_sku_codes)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add the products to the customer service
        instance.skus.add(*products)
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'SKUs added successfully',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def remove_skus(self, request, pk=None):
        """
        Remove SKUs from a customer service.
        """
        instance = self.get_object()
        sku_ids = request.data.get('sku_ids', [])
        instance.skus.remove(*sku_ids)
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'SKUs removed successfully',
            'data': serializer.data
        })