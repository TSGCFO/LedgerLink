# services/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as django_filters
from .models import Service
from .serializers import ServiceSerializer

# Keep existing template-based views
class ServiceListView(ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 10

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

class ServiceCreateView(CreateView):
    model = Service
    template_name = 'services/service_form.html'
    fields = ['service_name', 'description', 'charge_type']
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Service created successfully.')
        return super().form_valid(form)

class ServiceUpdateView(UpdateView):
    model = Service
    template_name = 'services/service_form.html'
    fields = ['service_name', 'description', 'charge_type']
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully.')
        return super().form_valid(form)

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('services:service_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Service deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Add new API views
class ServiceFilter(django_filters.FilterSet):
    """Filter set for advanced service filtering."""
    service_name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    charge_type = django_filters.ChoiceFilter(choices=Service.CHARGE_TYPES)
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    class Meta:
        model = Service
        fields = ['service_name', 'description', 'charge_type']

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for services with advanced filtering, searching, and sorting.
    
    Filter parameters:
    - service_name: Filter by service name (contains, case-insensitive)
    - description: Filter by description (contains, case-insensitive)
    - charge_type: Filter by exact charge type (single/quantity)
    - created_after: Filter by creation date (greater than or equal)
    - created_before: Filter by creation date (less than or equal)
    - updated_after: Filter by update date (greater than or equal)
    - updated_before: Filter by update date (less than or equal)
    
    Search:
    - Searches service_name and description fields
    
    Sorting:
    - Sort by any field using the ordering parameter
    - Prefix with '-' for descending order
    Example: ?ordering=-created_at
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    filterset_class = ServiceFilter
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['service_name', 'description']
    ordering_fields = ['service_name', 'charge_type', 'created_at', 'updated_at']
    ordering = ['service_name']  # Default ordering

    def get_queryset(self):
        """
        Optionally restricts the returned services by filtering against
        query parameters in the URL.
        """
        queryset = Service.objects.all()
        
        # Example of custom filtering
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(service_name__icontains=query) |
                Q(description__icontains=query)
            )
        
        return queryset
