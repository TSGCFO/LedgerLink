# customer_services/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as django_filters
from products.models import Product
from services.models import Service
from customers.models import Customer
from .models import CustomerService
from .forms import CustomerServiceForm
from .serializers import CustomerServiceSerializer

# Keep existing template-based views
class CustomerServiceListView(ListView):
    model = CustomerService
    template_name = 'customer_services/customer_service_list.html'
    context_object_name = 'customer_services'
    paginate_by = 10

class CustomerServiceDetailView(DetailView):
    model = CustomerService
    template_name = 'customer_services/customer_service_detail.html'
    context_object_name = 'customer_service'

class CustomerServiceCreateView(CreateView):
    model = CustomerService
    form_class = CustomerServiceForm
    template_name = 'customer_services/customer_service_form.html'
    success_url = reverse_lazy('customer_services:customer_service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer Service created successfully.')
        return super().form_valid(form)

class CustomerServiceUpdateView(UpdateView):
    model = CustomerService
    form_class = CustomerServiceForm
    template_name = 'customer_services/customer_service_form.html'
    success_url = reverse_lazy('customer_services:customer_service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer Service updated successfully.')
        return super().form_valid(form)

class CustomerServiceDeleteView(DeleteView):
    model = CustomerService
    template_name = 'customer_services/customer_service_confirm_delete.html'
    success_url = reverse_lazy('customer_services:customer_service_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Customer Service deleted successfully.')
        return super().delete(request, *args, **kwargs)

def get_customer_skus(request, customer_id):
    """API endpoint to get SKUs for a specific customer."""
    try:
        skus = Product.objects.filter(
            customer_id=customer_id
        ).values('id', 'sku').order_by('sku')

        return JsonResponse(list(skus), safe=False)
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=400
        )

# Add new API views
class CustomerServiceFilter(django_filters.FilterSet):
    """Filter set for advanced customer service filtering."""
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    service = django_filters.ModelChoiceFilter(queryset=Service.objects.all())
    unit_price_min = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte')
    unit_price_max = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    has_skus = django_filters.BooleanFilter(method='filter_has_skus')

    class Meta:
        model = CustomerService
        fields = ['customer', 'service']

    def filter_has_skus(self, queryset, name, value):
        """Filter services based on whether they have SKUs assigned."""
        if value:
            return queryset.annotate(sku_count=Count('skus')).filter(sku_count__gt=0)
        return queryset.annotate(sku_count=Count('skus')).filter(sku_count=0)

class CustomerServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for customer services with advanced filtering, searching, and sorting.
    
    Filter parameters:
    - customer: Filter by customer ID
    - service: Filter by service ID
    - unit_price_min: Filter by minimum unit price
    - unit_price_max: Filter by maximum unit price
    - created_after: Filter by creation date (greater than or equal)
    - created_before: Filter by creation date (less than or equal)
    - updated_after: Filter by update date (greater than or equal)
    - updated_before: Filter by update date (less than or equal)
    - has_skus: Filter by whether the service has SKUs assigned
    
    Search:
    - Searches across customer and service names
    
    Sorting:
    - Sort by any field using the ordering parameter
    - Prefix with '-' for descending order
    Example: ?ordering=-created_at
    """
    queryset = CustomerService.objects.select_related(
        'customer', 'service'
    ).prefetch_related('skus')
    serializer_class = CustomerServiceSerializer
    permission_classes = [AllowAny]
    filterset_class = CustomerServiceFilter
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        'customer__company_name',
        'service__service_name',
        'skus__sku'
    ]
    ordering_fields = [
        'customer__company_name',
        'service__service_name',
        'unit_price',
        'created_at',
        'updated_at'
    ]
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        """
        Optionally restricts the returned customer services by filtering against
        query parameters in the URL.
        """
        queryset = super().get_queryset()
        
        # Example of custom filtering
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(customer__company_name__icontains=query) |
                Q(service__service_name__icontains=query) |
                Q(skus__sku__icontains=query)
            ).distinct()
        
        return queryset
