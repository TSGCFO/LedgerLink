from rest_framework import viewsets, status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Customer
from .serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling customer CRUD operations.
    Provides standard CRUD endpoints plus additional actions.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def list(self, request, *args, **kwargs):
        """
        List all customers with optional filtering.
        """
        queryset = self.get_queryset()
        # Basic search functionality
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) |
                Q(legal_business_name__icontains=search)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new customer.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Customer created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing customer.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Customer updated successfully',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        Delete a customer.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Customer deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get basic customer statistics.
        """
        total_customers = self.get_queryset().count()
        return Response({
            'success': True,
            'data': {
                'total_customers': total_customers
            }
        })