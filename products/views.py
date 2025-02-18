from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling product CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on various parameters.
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer = self.request.query_params.get('customer', None)
        if customer:
            queryset = queryset.filter(customer=customer)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(sku__icontains=search) |
                Q(customer__company_name__icontains=search)
            )
        
        return queryset.order_by('sku')

    def list(self, request, *args, **kwargs):
        """
        List products with optional filtering.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new product.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Product created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing product.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Product updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete a product.
        """
        instance = self.get_object()
        # Check if product is being used in any orders
        if instance.customerservice_set.exists():
            return Response({
                'success': False,
                'message': 'Cannot delete product as it is used in customer services'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get product statistics.
        """
        from django.db.models import Count
        
        total_products = self.get_queryset().count()
        products_by_customer = self.get_queryset().values(
            'customer__company_name'
        ).annotate(
            count=Count('id')
        ).order_by('customer__company_name')
        
        return Response({
            'success': True,
            'data': {
                'total_products': total_products,
                'products_by_customer': list(products_by_customer)
            }
        })