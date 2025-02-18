from django_filters import rest_framework as filters
from django.db.models import Q
from datetime import datetime

class BaseFilterSet(filters.FilterSet):
    """
    Base filter set with common filtering functionality.
    """
    search = filters.CharFilter(method='search_filter')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    def search_filter(self, queryset, name, value):
        """
        Generic search filter to be overridden by child classes.
        """
        return queryset

class DateRangeFilterMixin:
    """
    Mixin to add date range filtering capabilities.
    """
    date_after = filters.DateFilter(method='filter_date_after')
    date_before = filters.DateFilter(method='filter_date_before')
    date_field = 'created_at'  # Override this in child classes if needed

    def filter_date_after(self, queryset, name, value):
        if value:
            kwargs = {f'{self.date_field}__gte': datetime.combine(value, datetime.min.time())}
            return queryset.filter(**kwargs)
        return queryset

    def filter_date_before(self, queryset, name, value):
        if value:
            kwargs = {f'{self.date_field}__lte': datetime.combine(value, datetime.max.time())}
            return queryset.filter(**kwargs)
        return queryset

class NumericRangeFilterMixin:
    """
    Mixin to add numeric range filtering capabilities.
    """
    min_value = filters.NumberFilter(method='filter_min_value')
    max_value = filters.NumberFilter(method='filter_max_value')
    value_field = None  # Must be set in child classes

    def filter_min_value(self, queryset, name, value):
        if value and self.value_field:
            kwargs = {f'{self.value_field}__gte': value}
            return queryset.filter(**kwargs)
        return queryset

    def filter_max_value(self, queryset, name, value):
        if value and self.value_field:
            kwargs = {f'{self.value_field}__lte': value}
            return queryset.filter(**kwargs)
        return queryset

class CustomerFilterSet(BaseFilterSet, DateRangeFilterMixin):
    """
    Filter set for Customer model.
    """
    email = filters.CharFilter(lookup_expr='iexact')
    name = filters.CharFilter(lookup_expr='icontains')
    is_active = filters.BooleanFilter()

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value)
        )

class OrderFilterSet(BaseFilterSet, DateRangeFilterMixin, NumericRangeFilterMixin):
    """
    Filter set for Order model.
    """
    status = filters.ChoiceFilter(choices=[])  # Choices should be set from Order model
    customer = filters.NumberFilter()
    value_field = 'total'  # For NumericRangeFilterMixin

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(order_number__icontains=value) |
            Q(customer__name__icontains=value) |
            Q(customer__email__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set choices if model is available
        model = self._meta.model
        if model and hasattr(model, 'STATUS_CHOICES'):
            self.filters['status'].extra['choices'] = model.STATUS_CHOICES

class ProductFilterSet(BaseFilterSet):
    """
    Filter set for Product model.
    """
    category = filters.CharFilter(lookup_expr='iexact')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_active = filters.BooleanFilter()

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(sku__icontains=value)
        )

class ServiceFilterSet(BaseFilterSet):
    """
    Filter set for Service model.
    """
    category = filters.CharFilter(lookup_expr='iexact')
    is_active = filters.BooleanFilter()

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

class BillingFilterSet(BaseFilterSet, DateRangeFilterMixin, NumericRangeFilterMixin):
    """
    Filter set for Billing model.
    """
    status = filters.ChoiceFilter(choices=[])  # Choices should be set from Billing model
    customer = filters.NumberFilter()
    value_field = 'amount'  # For NumericRangeFilterMixin

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(invoice_number__icontains=value) |
            Q(customer__name__icontains=value) |
            Q(description__icontains=value)
        )