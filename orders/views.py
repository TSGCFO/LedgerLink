from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Order
from .forms import OrderForm
from django.http import HttpResponse
import csv
from django.views import View

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    #ordering = ['-order_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')

        if search_query:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_query) |
                Q(customer__name__icontains=search_query) |
                Q(customer__email__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES
        context['priority_choices'] = Order.PRIORITY_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        return context

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Order created successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Order'
        return context

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Order #{self.object.transaction_id} updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Order #{self.object.transaction_id}'
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Order #{self.object.transaction_id}'
        return context

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')
    context_object_name = 'order'

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        messages.success(request, f'Order #{order.transaction_id} has been deleted.')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Order #{self.object.transaction_id}'
        return context


class OrderDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with CSV header
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="orders.csv"'},
        )

        # Get filtered queryset if any filters are applied
        queryset = Order.objects.all()
        search_query = request.GET.get('search')
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')

        if search_query:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_query) |
                Q(customer__name__icontains=search_query) |
                Q(customer__email__icontains=search_query)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        # Create the CSV writer
        writer = csv.writer(response)

        # Write the header row
        writer.writerow([
            'Transaction ID',
            'Customer',
            'close_date',
            'Status',
            'Priority',

        ])

        # Write the data rows
        for order in queryset:
            writer.writerow([
                order.transaction_id,
                str(order.customer),
                order.close_date,
                #order.get_status_display(),
                #order.get_priority_display(),

           ])

        return response