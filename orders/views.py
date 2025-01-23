# orders/views.py
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as django_filters
from .models import Order
from .serializers import OrderSerializer

class OrderFilter(django_filters.FilterSet):
    """Filter set for advanced order filtering."""
    customer = django_filters.NumberFilter(field_name='customer__id')
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Order.PRIORITY_CHOICES)
    reference_number = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    closed_after = django_filters.DateTimeFilter(field_name='close_date', lookup_expr='gte')
    closed_before = django_filters.DateTimeFilter(field_name='close_date', lookup_expr='lte')
    min_weight = django_filters.NumberFilter(field_name='weight_lb', lookup_expr='gte')
    max_weight = django_filters.NumberFilter(field_name='weight_lb', lookup_expr='lte')
    min_volume = django_filters.NumberFilter(field_name='volume_cuft', lookup_expr='gte')
    max_volume = django_filters.NumberFilter(field_name='volume_cuft', lookup_expr='lte')
    carrier = django_filters.CharFilter(lookup_expr='icontains')
    has_notes = django_filters.BooleanFilter(field_name='notes', lookup_expr='isnull', exclude=True)
    city = django_filters.CharFilter(field_name='ship_to_city', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='ship_to_state', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='ship_to_country', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = [
            'customer', 'status', 'priority', 'reference_number',
            'carrier', 'city', 'state', 'country'
        ]

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders with advanced filtering, searching, and sorting.
    
    Filter parameters:
    - customer: Filter by customer ID
    - status: Filter by order status (draft/submitted/shipped/delivered/cancelled)
    - priority: Filter by priority level (low/medium/high)
    - reference_number: Filter by reference number (contains, case-insensitive)
    - created_after: Filter by creation date (greater than or equal)
    - created_before: Filter by creation date (less than or equal)
    - closed_after: Filter by close date (greater than or equal)
    - closed_before: Filter by close date (less than or equal)
    - min_weight: Filter by minimum weight in pounds
    - max_weight: Filter by maximum weight in pounds
    - min_volume: Filter by minimum volume in cubic feet
    - max_volume: Filter by maximum volume in cubic feet
    - carrier: Filter by carrier name (contains, case-insensitive)
    - has_notes: Filter orders that have notes
    - city: Filter by shipping city (contains, case-insensitive)
    - state: Filter by shipping state (contains, case-insensitive)
    - country: Filter by shipping country (contains, case-insensitive)
    
    Search:
    - Searches across reference number, customer name, shipping details
    
    Sorting:
    - Sort by any field using the ordering parameter
    - Prefix with '-' for descending order
    Example: ?ordering=-created_at
    """
    queryset = Order.objects.select_related('customer')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    filterset_class = OrderFilter
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        'reference_number',
        'customer__company_name',
        'ship_to_name',
        'ship_to_company',
        'ship_to_address',
        'ship_to_city',
        'ship_to_state',
        'ship_to_country',
        'carrier',
        'notes'
    ]
    ordering_fields = [
        'transaction_id',
        'customer__company_name',
        'close_date',
        'reference_number',
        'weight_lb',
        'volume_cuft',
        'total_item_qty',
        'status',
        'priority'
    ]
    ordering = ['-transaction_id']  # Default ordering

    def get_queryset(self):
        """
        Optionally restricts the returned orders by filtering against
        query parameters in the URL.
        """
        queryset = super().get_queryset()
        
        # Example of custom filtering
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(reference_number__icontains=query) |
                Q(customer__company_name__icontains=query) |
                Q(ship_to_name__icontains=query) |
                Q(ship_to_company__icontains=query) |
                Q(ship_to_city__icontains=query) |
                Q(carrier__icontains=query)
            ).distinct()
        
        return queryset
