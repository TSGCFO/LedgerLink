# customers/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .models import Customer
from .forms import CustomerForm
from django.utils.timezone import now, timedelta
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from .models import Customer
from .serializers import CustomerSerializer


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10
    ordering = ['-created_at']

    def get_template_names(self):
        search_query = self.request.GET.get('search')
        if self.request.GET.get('search'):
            return ['customers/customer_search_list.html']
        return ['customers/customer_list.html']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        sort_by = self.request.GET.get('sort')
        filter_by = self.request.GET.get('filter')

        # Search functionality
        if search_query:
            queryset = queryset.filter(
                Q(company_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(city__icontains=search_query)
            )

        # Sorting functionality
        if sort_by in ['company_name', 'email', 'created_at']:
            queryset = queryset.order_by(sort_by)

        # Filtering functionality
        if filter_by == 'recent':
            queryset = queryset.filter(created_at__gte=now() - timedelta(days=30))
        elif filter_by == 'active':
            # Assuming an is_active field exists in the model
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort'] = self.request.GET.get('sort', '')
        context['filter'] = self.request.GET.get('filter', '')
        return context


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:list')

    def get_success_url(self):
        return reverse_lazy('customers:create_success')

    def form_valid(self, form):
        messages.success(self.request, 'Customer created successfully!')
        return super().form_valid(form)

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully!')
        return super().form_valid(form)

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Customer deleted successfully!')
        return super().delete(request, *args, **kwargs)


'====================================================================================================================='
'====================================================================================================================='
'====================================================================================================================='


class CustomerFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Customer
        fields = {
            'company_name': ['icontains'],
            'email': ['icontains'],
            'city': ['icontains'],
            'state': ['exact'],
            'country': ['exact'],
            'is_active': ['exact'],
            'business_type': ['exact'],
        }


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CustomerFilter
    search_fields = ['company_name', 'legal_business_name', 'email', 'phone', 'city']
    ordering_fields = [
        'company_name', 'email', 'phone', 'city', 'state',
        'country', 'is_active', 'created_at', 'business_type'
    ]
    ordering = ['company_name']

    def get_queryset(self):
        return Customer.objects.all()